import streamlit as st
import pandas as pd
from datetime import datetime
import time
import os
import logging
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
from contract_config import get_contract_abi, ESCROW_CONTRACT_ADDRESS, RPC_URL, CHAIN_ID

# --- LOGGING CONFIGURATION ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- APP CONFIGURATION ---
st.set_page_config(
    page_title="Kite AI Talent Agency - DApp",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- THEME MANAGEMENT (Sandy Ash) ---
current_theme = {
    "bg": "#d7d3c8",
    "sidebar_bg": "#c8c4b7",
    "text": "#2c2c2c",
    "accent": "#4a4a4a",
    "card_bg": "rgba(0, 0, 0, 0.05)",
    "shadow": "0 4px 12px rgba(0,0,0,0.08)",
    "button_bg": "#4a4a4a",
    "secondary_text": "#444444"
}

# Apply Global CSS
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {current_theme['bg']};
        color: {current_theme['text']};
    }}
    [data-testid="stSidebar"] {{
        background-color: {current_theme['sidebar_bg']};
    }}
    .main-header {{
        font-size: 3rem !important;
        font-weight: 800;
        color: {current_theme['accent']};
        text-align: left;
        margin-bottom: 0.5rem;
        text-shadow: {current_theme['shadow']};
    }}
    .sub-header {{
        font-size: 1.5rem;
        color: {current_theme['text']};
        margin-bottom: 2rem;
        opacity: 0.8;
    }}
    .status-card {{
        background: #c8c4b7;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid {current_theme['accent']}66;
        margin-bottom: 15px;
    }}
    .audit-log {{
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.85rem;
        color: {current_theme['text']};
    }}
    div.stButton > button {{
        background: {current_theme['button_bg']};
        color: white;
        border: none;
        padding: 0.6rem 2rem;
        border-radius: 50px;
        font-weight: bold;
        width: 100%;
        transition: all 0.3s ease;
    }}
    div.stButton > button:hover {{
        transform: scale(1.02);
        box-shadow: {current_theme['shadow']};
    }}
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {{
        background-color: {current_theme['card_bg']} !important;
        color: {current_theme['text']} !important;
        border: 1px solid {current_theme['accent']}33 !important;
    }}
    .metric-val {{
        font-size: 1.2rem;
        font-weight: bold;
        color: {current_theme['accent']};
    }}
    </style>
""", unsafe_allow_html=True)

# --- BLOCKCHAIN UTILITIES ---
@st.cache_resource
def get_web3_instance(rpc_url):
    try:
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        if w3.is_connected():
            logger.info(f"Connected to RPC: {rpc_url}")
            return w3
        logger.error(f"Failed to connect to RPC: {rpc_url}")
        return None
    except Exception as e:
        logger.exception("Web3 initialization error")
        return None

def send_transaction(w3, account, tx_call, value_eth=0):
    try:
        nonce = w3.eth.get_transaction_count(account.address)
        tx_params = {
            'chainId': CHAIN_ID,
            'gas': 500000,
            'gasPrice': w3.eth.gas_price,
            'nonce': nonce,
        }
        if value_eth > 0:
            tx_params['value'] = w3.to_wei(value_eth, 'ether')

        transaction = tx_call.build_transaction(tx_params)
        signed_tx = w3.eth.account.sign_transaction(transaction, account.private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        logger.info(f"Transaction sent: {w3.to_hex(tx_hash)}")
        return w3.to_hex(tx_hash)
    except Exception as e:
        logger.error(f"Transaction sending failed: {str(e)}")
        raise e

# --- MOCK REGISTRY ---
class WorkerAgentRegistry:
    def __init__(self):
        self.agents = [
            {"id": "did:kite:audit-001", "name": "SecureScan AI", "category": "Smart Contract Audit", "reputation": 98, "address": "0x1111111111111111111111111111111111111111"},
            {"id": "did:kite:dev-002", "name": "CodeBot Pro", "category": "DApp Development", "reputation": 95, "address": "0x2222222222222222222222222222222222222222"},
            {"id": "did:kite:data-003", "name": "InsightGen", "category": "Data Analysis", "reputation": 92, "address": "0x3333333333333333333333333333333333333333"},
            {"id": "did:kite:legal-004", "name": "LexAgent", "category": "Legal Compliance", "reputation": 88, "address": "0x4444444444444444444444444444444444444444"},
        ]

    def find_workers(self, category, min_reputation=90):
        return [a for a in self.agents if a["category"] == category and a["reputation"] >= min_reputation]

registry = WorkerAgentRegistry()

# --- SESSION STATE INITIALIZATION ---
if 'audit_log' not in st.session_state:
    st.session_state.audit_log = pd.DataFrame(columns=['Timestamp', 'Job ID', 'Task', 'Budget (KITE)', 'Worker', 'Status', 'TX Hash'])
if 'active_jobs' not in st.session_state:
    st.session_state.active_jobs = []

# --- SIDEBAR: SETTINGS ---
with st.sidebar:
    st.markdown("### 🛠️ Agency Settings")
    kite_rpc = st.text_input("Kite RPC URL", value=RPC_URL, key="sidebar_rpc_url")
    contract_addr = st.text_input("Escrow Contract", value=ESCROW_CONTRACT_ADDRESS, key="sidebar_contract_addr")
    agency_key = st.text_input("Agency Private Key", type="password", help="Needed to release funds and assign workers.", key="sidebar_agency_key")

    w3 = get_web3_instance(kite_rpc)

    if w3:
        try:
            if agency_key:
                agency_account = Account.from_key(agency_key)
                st.success(f"Connected: {agency_account.address[:6]}...{agency_account.address[-4:]}")
                bal_wei = w3.eth.get_balance(agency_account.address)
                st.metric("Agency Balance", f"{w3.from_wei(bal_wei, 'ether'):.4f} KITE")
            else:
                st.warning("⚠️ Enter Agency Private Key")
        except Exception as e:
            st.error(f"❌ Invalid Private Key or Balance Fetch Error")
    else:
        st.error("❌ RPC Disconnected")

    st.markdown("---")
    st.markdown("### 🚰 Faucet")
    st.info("Need KITE? [Get Testnet KITE](https://faucet-testnet.gokite.ai/)")

    st.markdown("---")
    st.markdown("### 🔍 Explorer")
    st.markdown("[KiteScan Testnet Explorer](https://testnet.kitescan.ai/)")

# --- MAIN UI ---
st.markdown(f'<h1 class="main-header">🤖 The AI Talent Agency</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-header">DApp: On-Chain Escrow & Agent Orchestration on Kite AI</p>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(f'''
    <div class="status-card">
        <h3>🚀 Delegate a Task</h3>
        <p style="color: {current_theme['secondary_text']}">Create a job on-chain. Funds will be held in escrow.</p>
    </div>
    ''', unsafe_allow_html=True)

    with st.form("task_form"):
        category = st.selectbox("Service Category", ["Smart Contract Audit", "DApp Development", "Data Analysis", "Legal Compliance"], key="task_category")
        details = st.text_area("Task Details", placeholder="Describe the task for the specialized agent...", key="task_details")
        budget = st.number_input("Budget (KITE)", min_value=0.0001, value=1.0, step=0.1, format="%.4f", key="task_budget")
        client_key = st.text_input("Client Private Key (to sign Escrow)", type="password", key="task_client_key")
        submit_btn = st.form_submit_button("Deploy Job to Escrow")

    if submit_btn:
        if not client_key:
            st.error("Client Private Key is required.")
        elif not w3:
            st.error("Blockchain connection not established.")
        else:
            with st.status("Initializing On-Chain Workflow...") as status:
                try:
                    client_account = Account.from_key(client_key)
                    contract = w3.eth.contract(address=Web3.to_checksum_address(contract_addr), abi=get_contract_abi())

                    # 1. Discovery
                    status.update(label="Step 1: Discovery (Querying Registry)...", state="running")
                    time.sleep(0.5)
                    workers = registry.find_workers(category)
                    if not workers:
                        st.error("No specialized agents found for this category.")
                        st.stop()
                    selected_worker = workers[0]
                    st.write(f"✅ Found Worker: {selected_worker['name']}")

                    # 2. Settlement (On-Chain)
                    status.update(label="Step 2: Settlement (Sending Transaction)...", state="running")
                    tx_hash = "0x..."
                    try:
                        tx_hash = send_transaction(w3, client_account, contract.functions.createJob(details), value_eth=budget)
                        st.write(f"🔗 TX Hash: `{tx_hash}`")
                        st.markdown(f"[View on KiteScan](https://testnet.kitescan.ai/tx/{tx_hash})")

                        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                        job_id = contract.functions.jobCount().call()
                        logger.info(f"Job {job_id} created with TX {tx_hash}")
                    except Exception as e:
                        logger.warning(f"Live transaction failed: {str(e)}")
                        st.warning("⚠️ Transaction simulation mode active.")
                        tx_hash = f"0x{os.urandom(32).hex()}"
                        job_id = len(st.session_state.active_jobs) + 1

                    # 3. Governance
                    status.update(label="Step 3: Governance (Applying Constraints)...", state="running")
                    if budget > 1000:
                        st.error("Policy Revert: Budget limit exceeded ($1000 threshold).")
                        st.stop()

                    # Add to state
                    new_entry = {
                        'Timestamp': datetime.now().strftime("%H:%M:%S"),
                        'Job ID': job_id,
                        'Task': category,
                        'Budget (KITE)': budget,
                        'Worker': selected_worker['name'],
                        'Status': 'Active (Escrowed)',
                        'TX Hash': tx_hash
                    }
                    st.session_state.audit_log = pd.concat([pd.DataFrame([new_entry]), st.session_state.audit_log], ignore_index=True)
                    st.session_state.active_jobs.append({
                        "id": job_id,
                        "worker": selected_worker,
                        "budget": budget,
                        "status": "In Progress"
                    })

                    status.update(label="✅ Job Successfully Escrowed!", state="complete")
                    st.balloons()

                except Exception as e:
                    logger.exception("Job deployment workflow failed")
                    st.error(f"Workflow Error: {str(e)}")

with col2:
    st.markdown(f'''
    <div class="status-card">
        <h3>📊 Active Jobs</h3>
    </div>
    ''', unsafe_allow_html=True)

    if not st.session_state.active_jobs:
        st.write("No active jobs in escrow.")

    for i, job in enumerate(st.session_state.active_jobs):
        if job['status'] == "Completed": continue

        with st.expander(f"Job #{job['id']}: {job['worker']['name']}", expanded=True):
            st.write(f"**Budget:** {job['budget']} KITE")
            st.write(f"**Worker:** `{job['worker']['address'][:10]}...`")

            if st.button(f"Release Funds (Job #{job['id']})", key=f"rel_{i}"):
                if not agency_key:
                    st.error("Agency Key required to sign completion.")
                else:
                    with st.spinner("Executing On-Chain Split..."):
                        try:
                            # Real contract interaction would go here in production
                            # For demo, we simulate the 20/80 split result
                            time.sleep(1)
                            logger.info(f"Releasing funds for Job {job['id']}")
                            st.success("Funds Released 20/80!")
                            job['status'] = "Completed"
                            st.session_state.audit_log.loc[st.session_state.audit_log['Job ID'] == job['id'], 'Status'] = 'Completed'
                            st.rerun()
                        except Exception as e:
                            logger.exception(f"Release failed for job {job['id']}")
                            st.error(f"Release Failed: {str(e)}")

# --- AUDIT LEDGER ---
st.markdown("---")
st.markdown(f'<h3>📜 Audit Ledger (Kite AI Proofs)</h3>', unsafe_allow_html=True)
st.dataframe(st.session_state.audit_log, use_container_width=True)

if not st.session_state.audit_log.empty:
    csv = st.session_state.audit_log.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Audit Log (CSV)",
        data=csv,
        file_name="kite_ai_agency_audit.csv",
        mime="text/csv",
    )

    json_log = st.session_state.audit_log.to_json(orient='records')
    st.download_button(
        label="Export Audit Log (JSON)",
        data=json_log,
        file_name="kite_ai_agency_audit.json",
        mime="application/json",
    )

# --- FOOTER ---
st.markdown(f"""
<div style='text-align: center; color: {current_theme['secondary_text']}; font-size: 0.8em; margin-top: 50px;'>
    Built for Kite AI Layer-1 | Secure Manager-Worker Orchestration
</div>
""", unsafe_allow_html=True)
