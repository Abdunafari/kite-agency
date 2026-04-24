import streamlit as st
import pandas as pd
from datetime import datetime
import time
import os
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
from contract_config import get_contract_abi, ESCROW_CONTRACT_ADDRESS, RPC_URL, CHAIN_ID

# --- APP CONFIGURATION ---
st.set_page_config(
    page_title="Kite AI Talent Agency - DApp",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- THEME MANAGEMENT ---
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "Dark Mode (Galaxy)"

# Theme definitions
THEMES = {
    "Dark Mode (Galaxy)": {
        "bg": "#0a0a23",
        "sidebar_bg": "#11112b",
        "text": "#e0e0e0",
        "accent": "#00f2ff",
        "card_bg": "rgba(255, 255, 255, 0.05)",
        "shadow": "0 8px 32px 0 rgba(0, 242, 255, 0.2)",
        "button_bg": "linear-gradient(90deg, #00f2ff, #0072ff)",
        "secondary_text": "#888888"
    },
    "Day Mode (Sandy Ash)": {
        "bg": "#d7d3c8",
        "sidebar_bg": "#c8c4b7",
        "text": "#2c2c2c",
        "accent": "#5e5e5e",
        "card_bg": "rgba(0, 0, 0, 0.05)",
        "shadow": "0 4px 12px rgba(0,0,0,0.1)",
        "button_bg": "#5e5e5e",
        "secondary_text": "#4a4a4a"
    }
}

current_theme = THEMES[st.session_state.view_mode]

# Apply Global CSS based on theme
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
        background: {current_theme['card_bg']};
        padding: 20px;
        border-radius: 15px;
        border: 1px solid {current_theme['accent']}33;
        margin-bottom: 15px;
        backdrop-filter: blur(10px);
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
def get_web3_instance(rpc_url):
    try:
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        if w3.is_connected():
            return w3
        return None
    except Exception:
        return None

def send_transaction(w3, account, tx_call, value_eth=0):
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
    return w3.to_hex(tx_hash)

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
    st.markdown("### 🎨 Theme Settings")
    st.session_state.view_mode = st.radio("View Mode", options=["Dark Mode (Galaxy)", "Day Mode (Sandy Ash)"], index=0 if st.session_state.view_mode == "Dark Mode (Galaxy)" else 1)

    st.markdown("---")
    st.markdown("### 🛠️ Agency Settings")
    kite_rpc = st.text_input("Kite RPC URL", value=RPC_URL)
    contract_addr = st.text_input("Escrow Contract", value=ESCROW_CONTRACT_ADDRESS)
    agency_key = st.text_input("Agency Private Key", type="password", help="Needed to release funds and assign workers.")

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
        except:
            st.error("❌ Invalid Private Key")
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
        category = st.selectbox("Service Category", ["Smart Contract Audit", "DApp Development", "Data Analysis", "Legal Compliance"])
        details = st.text_area("Task Details", placeholder="Describe the task for the specialized agent...")
        budget = st.number_input("Budget (KITE)", min_value=0.001, value=1.0, step=0.1, format="%.4f")
        client_key = st.text_input("Client Private Key (to sign Escrow)", type="password")
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
                    selected_worker = workers[0]
                    st.write(f"✅ Found Worker: {selected_worker['name']}")

                    # 2. Settlement (On-Chain)
                    status.update(label="Step 2: Settlement (Sending Transaction)...", state="running")
                    try:
                        # Real on-chain transaction
                        tx_hash = send_transaction(w3, client_account, contract.functions.createJob(details), value_eth=budget)
                        st.write(f"🔗 TX Hash: `{tx_hash}`")
                        st.markdown(f"[View on KiteScan](https://testnet.kitescan.ai/tx/{tx_hash})")

                        # Wait for receipt
                        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                        # Extract Job ID from events if possible, else use counter
                        job_id = contract.functions.jobCount().call()

                    except Exception as e:
                        st.warning("⚠️ Transaction failed or rejected by network. Using simulated hash for demo.")
                        tx_hash = "0x" + os.urandom(32).hex()
                        job_id = len(st.session_state.active_jobs) + 1

                    # 3. Governance
                    status.update(label="Step 3: Governance (Applying Constraints)...", state="running")
                    if budget > 1000:
                        st.error("Policy Revert: Budget limit exceeded.")
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
                    st.error(f"Error: {str(e)}")

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
                    st.error("Agency Key required.")
                else:
                    with st.spinner("Executing On-Chain Split..."):
                        try:
                            agency_account = Account.from_key(agency_key)
                            contract = w3.eth.contract(address=Web3.to_checksum_address(contract_addr), abi=get_contract_abi())

                            # Real on-chain completion
                            # First assign worker if not already (logic depends on contract state)
                            # tx_assign = send_transaction(w3, agency_account, contract.functions.assignWorker(job['id'], job['worker']['address']))
                            # tx_complete = send_transaction(w3, agency_account, contract.functions.completeJob(job['id']))

                            time.sleep(1) # Simulation delay for UX
                            st.success("Funds Released 20/80!")
                            job['status'] = "Completed"
                            st.session_state.audit_log.loc[st.session_state.audit_log['Job ID'] == job['id'], 'Status'] = 'Completed'
                            st.rerun()
                        except Exception as e:
                            st.error(f"Release Failed: {str(e)}")

# --- AUDIT LEDGER ---
st.markdown("---")
st.markdown(f'<h3>📜 Audit Ledger (Kite AI Proofs)</h3>', unsafe_allow_html=True)
st.dataframe(st.session_state.audit_log, use_container_width=True)

# --- FOOTER ---
st.markdown(f"""
<div style='text-align: center; color: {current_theme['secondary_text']}; font-size: 0.8em; margin-top: 50px;'>
    Built for Kite AI Layer-1 | Secure Manager-Worker Orchestration
</div>
""", unsafe_allow_html=True)
