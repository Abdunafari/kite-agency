import json
import os
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Kite AI Testnet Configuration
RPC_URL = "https://rpc-testnet.gokite.ai/"
CHAIN_ID = 2368

def get_contract_abi():
    # This is a simplified ABI for the AIAgencyEscrow contract
    return [
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "uint256",
				"name": "jobId",
				"type": "uint256"
			},
			{
				"indexed": True,
				"internalType": "address",
				"name": "worker",
				"type": "address"
			}
		],
		"name": "JobAssigned",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "uint256",
				"name": "jobId",
				"type": "uint256"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "workerAmount",
				"type": "uint256"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "agencyAmount",
				"type": "uint256"
			}
		],
		"name": "JobCompleted",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "uint256",
				"name": "jobId",
				"type": "uint256"
			},
			{
				"indexed": True,
				"internalType": "address",
				"name": "client",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "budget",
				"type": "uint256"
			}
		],
		"name": "JobCreated",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "uint256",
				"name": "jobId",
				"type": "uint256"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "amount",
				"type": "uint256"
			}
		],
		"name": "JobRefunded",
		"type": "event"
	},
	{
		"inputs": [],
		"name": "AGENCY_FEE_PERCENTAGE",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "agencyOwner",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_jobId",
				"type": "uint256"
			},
			{
				"internalType": "address",
				"name": "_worker",
				"type": "address"
			}
		],
		"name": "assignWorker",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_jobId",
				"type": "uint256"
			}
		],
		"name": "completeJob",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "_taskDetails",
				"type": "string"
			}
		],
		"name": "createJob",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "jobCount",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "jobs",
		"outputs": [
			{
				"internalType": "address",
				"name": "client",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "worker",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "budget",
				"type": "uint256"
			},
			{
				"internalType": "enum AIAgencyEscrow.JobStatus",
				"name": "status",
				"type": "uint8"
			},
			{
				"internalType": "string",
				"name": "taskDetails",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "createdAt",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_jobId",
				"type": "uint256"
			}
		],
		"name": "refundJob",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"stateMutability": "payable",
		"type": "receive"
	}
]

# Note: In a real production scenario, the contract would be deployed to a specific address.
# For this dApp demo, we will use a mock address or a pre-deployed one if available.
# Since we are in a sandbox, we'll provide the logic to interact with it.
ESCROW_CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3" # Placeholder
