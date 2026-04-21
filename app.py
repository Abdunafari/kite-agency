import streamlit as st
from web3 import Web3
from dotenv import load_dotenv
import os
import time
import json
import pandas as pd
import uuid

# --- LOAD ENVIRONMENT VARIABLES ---
load_dotenv()

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="The AI Talent Agency",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR EYE-FRIENDLY LIGHT THEME ---
st.markdown("""
    <style>
    /* Main background - Soft light grey for reduced eye strain */
    .stApp {
        background-color: #f8f9fa;
        color: #212529;
    }

    /* Sidebar styling - Slightly darker neutral for clear separation */
    section[data-testid="stSidebar"] {
        background-color: #e9ecef !important;
        border-right: 1px solid #dee2e6;
    }

    /* Headers - High contrast professional teal/blue */
    h1, h2, h3 {
        color: #005f73 !important;
        font-weight: 700 !important;
    }

    /* Buttons - Accessible blue with white text */
    .stButton>button {
        background: #0a9396;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: background 0.2s ease;
    }
    .stButton>button:hover {
        background: #005f73;
        color: white;
    }

    /* Input fields - High legibility white background with dark text */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>select, .stNumberInput>div>div>input {
        background-color: #ffffff !important;
        color: #212529 !important;
        border: 1px solid #ced4da !important;
    }

    /* Status containers - Subtle borders and soft backgrounds */
    .status-box {
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        background-color: #ffffff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 12px;
        color: #495057;
    }

    /* Audit Log Table */
    .stDataFrame {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 8px;
    }

    /* Success/Info messages contrast tweaks */
    .stAlert {
        border-radius: 8px;
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

    st.title("🤖 The AI Talent Agency")
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
