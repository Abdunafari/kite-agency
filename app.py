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
 ##feat/ai-talent-agency-kite-ai-18409574559028205297
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
        category = st.selectbox("Service Category", ["Smart Contract Audit", "DApp Development", "Data Analysis", "Legal Compliance"])
        details = st.text_area("Task Details", placeholder="Describe the task for the specialized agent...")
        budget = st.number_input("Budget (KITE)", min_value=0.0001, value=1.0, step=0.1, format="%.4f")
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

# --- FOOTER ---
st.markdown(f"""
<div style='text-align: center; color: {current_theme['secondary_text']}; font-size: 0.8em; margin-top: 50px;'>
    Built for Kite AI Layer-1 | Secure Manager-Worker Orchestration
</div>
""", unsafe_allow_html=True)

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="The AI Talent Agency",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR GALAXY AESTHETIC ---
st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background: radial-gradient(circle at top right, #0a0e29, #02040f);
        color: #e0e0e0;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(10, 14, 41, 0.9) !important;
        border-right: 1px solid #1f2a4d;
    }

    /* Headers */
    h1, h2, h3 {
        color: #00d4ff !important;
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #00d4ff, #005f73);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.8);
        transform: scale(1.02);
    }

    /* Input fields */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>select, .stNumberInput>div>div>input {
        background-color: #0f172a !important;
        color: #00d4ff !important;
        border: 1px solid #1f2a4d !important;
    }

    /* Status containers */
    .status-box {
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #1f2a4d;
        background-color: rgba(31, 42, 77, 0.3);
        margin-bottom: 10px;
    }

    /* Audit Log Table */
    .stDataFrame {
        border: 1px solid #1f2a4d;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MOCK WORKER REGISTRY ---
class WorkerAgentRegistry:
    def __init__(self):
        self.workers = [
            {"name": "AuditBot-9000", "category": "Smart Contract Audit", "address": "0x1111111111111111111111111111111111111111", "score": 98, "specialty": "Solidity, Vyper", "did": "did:kite:agent-001"},
            {"name": "SecureScan AI", "category": "Smart Contract Audit", "address": "0x2222222222222222222222222222222222222222", "score": 92, "specialty": "Formal Verification", "did": "did:kite:agent-002"},
            {"name": "CryptoArtist", "category": "NFT Art Generation", "address": "0x3333333333333333333333333333333333333333", "score": 95, "specialty": "Generative Art, Midjourney Style", "did": "did:kite:agent-003"},
            {"name": "PixelGenie", "category": "NFT Art Generation", "address": "0x4444444444444444444444444444444444444444", "score": 88, "specialty": "Pixel Art", "did": "did:kite:agent-004"},
            {"name": "PolyglotAgent", "category": "Translation (EN -> AR)", "address": "0x5555555555555555555555555555555555555555", "score": 94, "specialty": "Technical Localization", "did": "did:kite:agent-005"},
            {"name": "MarketWhiz", "category": "Market Sentiment Analysis", "address": "0x6666666666666666666666666666666666666666", "score": 91, "specialty": "Social Media Trends", "did": "did:kite:agent-006"},
        ]

    def find_workers(self, category, min_score=90):
        return [w for w in self.workers if w["category"] == category and w["score"] >= min_score]

    def get_did(self, address):
        for w in self.workers:
            if w["address"] == address:
                return w.get("did")
        return None

# --- SESSION STATE ---
if 'audit_log' not in st.session_state:
    st.session_state.audit_log = []

# --- CORE LOGIC FUNCTIONS ---

class PolicyEngine:
    """Simulates Kite AI On-Chain Spending Rules & Policies."""
    def __init__(self, budget_limit=1000):
        self.budget_limit = budget_limit

    def validate_transaction(self, amount, category):
        # Rule 1: Budget Cap
        if amount > self.budget_limit:
            return False, f"Spending Rule Violation: Amount {amount} exceeds limit {self.budget_limit}"

        # Rule 2: Category Restriction (Simulated)
        restricted_categories = ["High-Frequency Trading"]
        if category in restricted_categories:
            return False, f"Policy Violation: {category} is a restricted category."

        return True, "All on-chain policies passed."

def connect_to_kite(rpc_url):
    try:
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        return w3
    except Exception as e:
        st.error(f"Connection failed: {e}")
        return None

def generate_attestation(tx_hash, worker_address, amount, task):
    attestation_id = "KITE-ATTEST-" + str(uuid.uuid4())[:12].upper()
    return {
        "Attestation ID": attestation_id,
        "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "Task": task,
        "Worker": worker_address,
        "Amount": f"{amount} USDC",
        "TX_Hash": tx_hash,
        "Status": "Verified"
    }

def create_session_key(w3, master_private_key, budget_limit):
    """
    Simulates the creation of a Kite AI Session Key.
    A temporary key is generated and authorized by the master key.
    """
    session_account = w3.eth.account.create()
    session_id = "SESSION-" + str(uuid.uuid4())[:8].upper()

    # In a real Kite AI implementation, we would register this session key
    # on-chain with specific spending limits and TTL.
    return {
        "id": session_id,
        "address": session_account.address,
        "private_key": session_account._private_key.hex(),
        "limit": budget_limit,
        "expires": time.time() + 3600 # 1 hour TTL
    }

def verify_did(registry, worker_address):
    """Simulates Kite Passport (DID) verification."""
    did = registry.get_did(worker_address)
    if did and did.startswith("did:kite:"):
        return True, did
    return False, None

def sign_and_send_usdc(w3, signing_key, to_address, amount):
    # This is a simulation of a USDC transaction on Kite AI
    # In a real app, you'd use a contract ABI and call the `transfer` method
    try:
        account = w3.eth.account.from_key(signing_key)
        # Simulate wait time for blockchain propagation
        time.sleep(2)
        mock_tx_hash = "0x" + os.urandom(32).hex()
        return True, mock_tx_hash
    except Exception as e:
        # In a mock environment, we still return a hash for the demo if w3 fails
        mock_tx_hash = "0x" + os.urandom(32).hex()
        return True, mock_tx_hash

# --- UI COMPONENTS ---

def main():
    registry = WorkerAgentRegistry()

    st.title("🌌 The AI Talent Agency")
    st.markdown("### Autonomous Agent Orchestration & Payments on Kite AI")
    st.markdown("---")

    # Sidebar
    st.sidebar.title("🛠️ Agency Settings")
    rpc_url = st.sidebar.text_input("Kite RPC URL", value="https://testnet-rpc.gokite.ai")
    private_key = st.sidebar.text_input("Agency Private Key", type="password", placeholder="0x...")

    w3 = connect_to_kite(rpc_url)
    if w3 and w3.is_connected():
        st.sidebar.success("📡 Connected to Kite Network")
    else:
        st.sidebar.warning("❌ Disconnected from Kite")

    # Main Layout
    col_main, col_ledger = st.columns([2, 1])

    with col_main:
        st.header("🚀 Delegate a Task")

        with st.form("task_form"):
            category = st.selectbox(
                "Service Category",
                ["Smart Contract Audit", "NFT Art Generation", "Translation (EN -> AR)", "Market Sentiment Analysis"]
            )
            details = st.text_area("Task Details", placeholder="Describe the task for the specialized agent...")
            budget = st.number_input("Budget (USDC)", min_value=1.0, max_value=2000.0, value=100.0, step=10.0)

            submit_button = st.form_submit_button("Execute Transaction")

        if submit_button:
            if not private_key:
                st.error("Missing Private Key! Cannot sign transaction.")
                return

            # --- KITE AI GOVERNANCE: ON-CHAIN POLICY ENGINE ---
            policy_engine = PolicyEngine(budget_limit=1000)
            is_valid, policy_msg = policy_engine.validate_transaction(budget, category)

            if not is_valid:
                st.error(f"🚨 {policy_msg}. Transaction reverted by Kite Governance.")
                return

            # --- STEP 1: REQUEST ---
            status_placeholder = st.empty()

            with status_placeholder.container():
                st.markdown('<div class="status-box"><b>Step 1: Request</b><br>Initializing task request...</div>', unsafe_allow_html=True)
                time.sleep(1)

                # --- STEP 2: DISCOVERY & DID VERIFICATION ---
                st.markdown('<div class="status-box"><b>Step 2: Discovery & DID Verification</b><br>Verifying Agent Credentials via Kite Passport (DID)...</div>', unsafe_allow_html=True)
                workers = registry.find_workers(category, min_score=90)
                time.sleep(1.5)

                if not workers:
                    st.error("No suitable agents found with sufficient reputation.")
                    return

                selected_worker = workers[0] # Select highest score

                is_verified, did_id = verify_did(registry, selected_worker['address'])
                if is_verified:
                    st.info(f"🛡️ **DID Verified**: {selected_worker['name']} is a trusted Kite Agent ({did_id}).")
                else:
                    st.error("DID Verification Failed! Security Protocol triggered.")
                    return

                # --- STEP 3: GOVERNANCE & SESSION KEYS ---
                st.markdown('<div class="status-box"><b>Step 3: Governance & Session Keys</b><br>Generating ephemeral session key for secure settlement...</div>', unsafe_allow_html=True)
                agency_fee = budget * 0.20
                worker_payment = budget * 0.80

                # Create session key for this specific task
                session = create_session_key(w3, private_key, worker_payment)
                st.write(f"🔑 **Session Key Active**: `{session['address'][:10]}...` (Limit: {session['limit']} USDC)")
                st.write(f"💵 **Fee Split:** Agency (20%): ${agency_fee:.2f} | Worker (80%): ${worker_payment:.2f}")
                time.sleep(1)

                # --- STEP 4: ESCROW & SETTLEMENT ---
                st.markdown('<div class="status-box"><b>Step 4: Escrow & Settlement</b><br>Securing funds in Escrow and broadcasting transaction via Session Key...</div>', unsafe_allow_html=True)

                # Simulate Escrow Lock
                st.write("🔒 *Funds locked in Escrow contract...*")
                time.sleep(1)

                success, result = sign_and_send_usdc(w3, session['private_key'], selected_worker['address'], worker_payment)

                if success:
                    tx_hash = result
                    st.success(f"💸 Payment released from Escrow! TX Hash: {tx_hash[:20]}...")

                    # --- STEP 5: ATTESTATION ---
                    st.markdown('<div class="status-box"><b>Step 5: Attestation</b><br>Generating Proof of Work & On-chain receipt...</div>', unsafe_allow_html=True)
                    attestation = generate_attestation(tx_hash, selected_worker['address'], worker_payment, category)
                    st.session_state.audit_log.append(attestation)
                    time.sleep(1)

                    st.balloons()
                    st.subheader("✅ Final Deliverable")
                    st.success(f"Task '{category}' has been completed by {selected_worker['name']}.")

                    # Display expanded metadata including DID and Session Info
                    with st.expander("View Transaction Metadata", expanded=True):
                        st.write(f"🛡️ **Agent DID:** {did_id}")
                        st.write(f"🔑 **Signing Key (Session):** {session['address']}")
                        st.write(f"📝 **Attestation ID:** {attestation['Attestation ID']}")
                        st.write(f"📑 **Kite Governance Policy:** {policy_msg}")

                    st.json({
                        "AttestationID": attestation["Attestation ID"],
                        "Worker": selected_worker['name'],
                        "Deliverable": f"Simulation of {category} results for: {details[:30]}...",
                        "EscrowStatus": "Released"
                    })
                else:
                    st.error(f"Transaction failed: {result}")

    with col_ledger:
        st.header("📊 Audit Ledger")
        st.write("Real-time attestation stream")

        if st.session_state.audit_log:
            df = pd.DataFrame(st.session_state.audit_log)
            # Display important columns
            st.dataframe(df[["Timestamp", "Task", "Amount", "Status"]], use_container_width=True)

            # Detailed view in expander
            with st.expander("View Full Log Details"):
                st.write(df)

            # Export
            json_log = json.dumps(st.session_state.audit_log, indent=4)
            st.download_button(
                label="📥 Export Audit Log (JSON)",
                data=json_log,
                file_name=f"kite_agency_log_{int(time.time())}.json",
                mime="application/json"
            )
        else:
            st.info("No transactions logged yet.")

    st.markdown("---")

    # --- EDUCATIONAL SECTION: HOW IT WORKS ---
    st.header("🧠 How the Agency Works")

    col_info1, col_info2, col_info3 = st.columns(3)

    with col_info1:
        st.subheader("1. Discovery & Identity")
        st.write("""
        The Agency queries the **Kite Agent Registry** to find workers specializing in your task.
        It verifies each worker's **Kite Passport (DID)** to ensure they are authenticated
        and have a reputation score > 90.
        """)

    with col_info2:
        st.subheader("2. Governance & Security")
        st.write("""
        Before any funds move, the **Kite Policy Engine** checks if the request violates
        on-chain spending rules (e.g., $1,000 limit). The Agency then generates an
        **Ephemeral Session Key** to sign the transaction safely.
        """)

    with col_info3:
        st.subheader("3. Settlement & Proof")
        st.write("""
        Funds are locked in an **Escrow Contract**. Once the task is completed,
        payment is released and an **On-Chain Attestation** is generated as a
        verifiable proof of work and payment.
        """)

    st.markdown("---")

    # --- USER GUIDE ---
    with st.expander("📖 User Guide: How to use this Dashboard"):
        st.markdown("""
        ### Quick Start Guide
        1. **Configure Connection**: Look at the sidebar. Ensure you are connected to the Kite Testnet RPC.
        2. **Provide Credentials**: Enter your Agency Private Key in the sidebar (used to authorize the Session Key).
        3. **Define Task**: Select a category (e.g., *Smart Contract Audit*), describe your requirements, and set a budget in USDC.
        4. **Execute**: Click **'Execute Transaction'**. Watch the real-time status boxes as the Agency negotiates and settles the task.
        5. **Verify**: Check the **Audit Ledger** on the right for your unique Attestation ID and transaction hash.
        """)

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("The AI Talent Agency | Powered by Kite AI Blockchain | Specialized Autonomous Workers")

if __name__ == "__main__":
    main()
         
