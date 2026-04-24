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

## 📦 Installation

1. Clone the repository.
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
