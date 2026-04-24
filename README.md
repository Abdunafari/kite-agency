##  feat/ai-talent-agency-kite-ai-18409574559028205297
# The AI Talent Agency

A production-ready DApp built on **Kite AI**, an EVM-compatible Layer-1 blockchain designed for AI agents. This application serves as a Manager Agent that autonomously orchestrates tasks by finding specialized Worker Agents, handling on-chain escrow, and executing programmable payments.

## 🚀 Features

- **Agent Discovery**: Queries a registry to find specialized workers based on category and reputation.
- **On-Chain Escrow**: Integrates with the `AIAgencyEscrow.sol` contract to lock funds securely.
- **Programmable Payments**: Implements a 20/80 commission split (20% Agency, 80% Worker).
- **Dual-Theme UI**: Includes "Dark Mode (Galaxy)" and "Day Mode (Sandy Ash)" styles.
- **Audit Ledger**: Maintains a transparent log of all transactions and attestations.

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Blockchain**: web3.py, eth-account
- **Data**: Pandas
- **Environment**: python-dotenv

## 📋 Prerequisites

- Python 3.10+
- A Kite AI wallet with testnet KITE tokens.
- (Optional) Deployed `AIAgencyEscrow.sol` contract.
##
# 🌌 The AI Talent Agency

The **AI Talent Agency** is a specialized Manager Agent dashboard built for the **Kite AI blockchain** ecosystem. It enables users to delegate high-level tasks to a network of specialized Worker Agents with built-in security, governance, and trust layers.

## 🚀 Key Features

- **Autonomous Discovery**: Queries a registry to find Worker Agents based on category and reputation.
- **Kite Passport (DID)**: Verifies worker identity using unique `did:kite:` identifiers.
- **On-Chain Governance**: Implements a programmable `PolicyEngine` to enforce spending rules (e.g., $1,000 budget cap).
- **Secure Settlement**:
  - **Session Keys**: Generates ephemeral keys to delegate signing authority.
  - **Escrow Mechanics**: Funds are locked and released only upon task completion.
- **Immutable Auditability**: Generates on-chain attestations for every transaction, visible in a real-time ledger.
- **Galaxy Aesthetic**: A professional, dark-themed dashboard designed for the Web3 space.

## 🛠️ Technical Stack

- **Frontend**: Streamlit
- **Web3**: Web3.py (EVM compatible)
- **Data**: Pandas
- **Blockchain**: Kite AI (Layer-1)
-  main

## 📦 Installation

1. Clone the repository.
feat/ai-talent-agency-kite-ai-18409574559028205297
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

Create a `.env` file in the root directory:

```env
KITE_RPC_URL=https://rpc-testnet.gokite.ai/
KITE_CHAIN_ID=2368
ESCROW_CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
```

## 🏃 Running the App

```bash
streamlit run app.py
```

## 🧠 Deployment on Kite AI

The smart contract source is located in `contracts/AIAgencyEscrow.sol`. You can deploy it using Foundry, Hardhat, or Remix on the Kite AI Testnet. Once deployed, update the `ESCROW_CONTRACT_ADDRESS` in your `.env` file.

---
*Built for the Kite AI Network | Secure Agent Orchestration*

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your configuration (optional).
4. Run the application:
   ```bash
   streamlit run app.py
   ```

## 📖 How to Use

1. **Sidebar**: Connect to the Kite RPC and provide your Agency Private Key.
2. **Task Form**: Select a service category, enter task details, and set a budget.
3. **Execute**: Click 'Execute Transaction' and follow the real-time status updates (Discovery -> Governance -> Settlement -> Attestation).
4. **Export**: Use the Audit Ledger to download a JSON report of all activities.
 main
