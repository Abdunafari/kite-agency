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

## 📦 Installation

1. Clone the repository.
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
