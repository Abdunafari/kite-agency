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
            {"name": "AuditBot-9000", "category": "Smart Contract Audit", "address": "0x1111111111111111111111111111111111111111", "score": 98, "specialty": "Solidity, Vyper"},
            {"name": "SecureScan AI", "category": "Smart Contract Audit", "address": "0x2222222222222222222222222222222222222222", "score": 92, "specialty": "Formal Verification"},
            {"name": "CryptoArtist", "category": "NFT Art Generation", "address": "0x3333333333333333333333333333333333333333", "score": 95, "specialty": "Generative Art, Midjourney Style"},
            {"name": "PixelGenie", "category": "NFT Art Generation", "address": "0x4444444444444444444444444444444444444444", "score": 88, "specialty": "Pixel Art"},
            {"name": "PolyglotAgent", "category": "Translation (EN -> AR)", "address": "0x5555555555555555555555555555555555555555", "score": 94, "specialty": "Technical Localization"},
            {"name": "MarketWhiz", "category": "Market Sentiment Analysis", "address": "0x6666666666666666666666666666666666666666", "score": 91, "specialty": "Social Media Trends"},
        ]

    def find_workers(self, category, min_score=90):
        return [w for w in self.workers if w["category"] == category and w["score"] >= min_score]

# --- SESSION STATE ---
if 'audit_log' not in st.session_state:
    st.session_state.audit_log = []

# --- CORE LOGIC FUNCTIONS ---

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

def sign_and_send_usdc(w3, private_key, to_address, amount):
    # This is a simulation of a USDC transaction on Kite AI
    # In a real app, you'd use a contract ABI and call the `transfer` method
    # For demo purposes, we simulate the signed transaction flow
    try:
        if private_key.startswith("0x"):
            account = w3.eth.account.from_key(private_key)
        else:
            account = w3.eth.account.from_key("0x" + private_key)

        # Simulate wait time for blockchain propagation
        time.sleep(2)
        mock_tx_hash = "0x" + os.urandom(32).hex()
        return True, mock_tx_hash
    except Exception as e:
        return False, str(e)

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

            if budget >= 1000:
                st.error("🚨 Programmable Constraint Violation: Budget exceeds Agency limit ($1,000). Transaction reverted.")
                return

            # --- STEP 1: REQUEST ---
            status_placeholder = st.empty()

            with status_placeholder.container():
                st.markdown('<div class="status-box"><b>Step 1: Request</b><br>Initializing task request...</div>', unsafe_allow_html=True)
                time.sleep(1)

                # --- STEP 2: DISCOVERY ---
                st.markdown('<div class="status-box"><b>Step 2: Discovery</b><br>Querying Kite Network for high-reputation workers...</div>', unsafe_allow_html=True)
                workers = registry.find_workers(category, min_score=90)
                time.sleep(1.5)

                if not workers:
                    st.error("No suitable agents found with sufficient reputation.")
                    return

                selected_worker = workers[0] # Select highest score
                st.info(f"📍 Agent Found: **{selected_worker['name']}** (Score: {selected_worker['score']})")

                # --- STEP 3: GOVERNANCE & NEGOTIATION ---
                st.markdown('<div class="status-box"><b>Step 3: Governance & Negotiation</b><br>Applying programmable constraints and calculating fee split...</div>', unsafe_allow_html=True)
                agency_fee = budget * 0.20
                worker_payment = budget * 0.80
                time.sleep(1)
                st.write(f"💵 **Fee Split:** Agency (20%): ${agency_fee:.2f} | Worker (80%): ${worker_payment:.2f}")

                # --- STEP 4: SETTLEMENT ---
                st.markdown('<div class="status-box"><b>Step 4: Settlement</b><br>Signing and broadcasting USDC transaction on Kite AI...</div>', unsafe_allow_html=True)
                success, result = sign_and_send_usdc(w3, private_key, selected_worker['address'], worker_payment)
                
                if success:
                    tx_hash = result
                    st.success(f"💸 Payment successful! TX Hash: {tx_hash[:20]}...")

                    # --- STEP 5: ATTESTATION ---
                    st.markdown('<div class="status-box"><b>Step 5: Attestation</b><br>Generating Proof of Work & On-chain receipt...</div>', unsafe_allow_html=True)
                    attestation = generate_attestation(tx_hash, selected_worker['address'], worker_payment, category)
                    st.session_state.audit_log.append(attestation)
                    time.sleep(1)

                    st.balloons()
                    st.subheader("✅ Final Deliverable")
                    st.success(f"Task '{category}' has been completed by {selected_worker['name']}.")
                    st.json({
                        "AttestationID": attestation["Attestation ID"],
                        "Worker": selected_worker['name'],
                        "Deliverable": f"Simulation of {category} results for: {details[:30]}..."
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
    st.caption("The AI Talent Agency | Powered by Kite AI Blockchain | Specialized Autonomous Workers")

if __name__ == "__main__":
    main()
