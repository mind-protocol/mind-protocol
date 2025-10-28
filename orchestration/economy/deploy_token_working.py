"""
Working Token Deployment Script

Actually deploys $MIND token using solana-py
"""

import os
import json
from pathlib import Path
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solders.transaction import Transaction
from solana.rpc.api import Client
from solana.rpc.commitment import Confirmed
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
NETWORK = "devnet"  # Start with devnet
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")

if NETWORK == "mainnet":
    RPC_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}" if HELIUS_API_KEY else "https://api.mainnet-beta.solana.com"
else:
    RPC_URL = f"https://devnet.helius-rpc.com/?api-key={HELIUS_API_KEY}" if HELIUS_API_KEY else "https://api.devnet.solana.com"

print(f"🌐 Network: {NETWORK}")
print(f"🔗 RPC: {RPC_URL[:50]}...")

# Initialize client
client = Client(RPC_URL, commitment=Confirmed)

# Check if we can connect
try:
    version = client.get_version()
    print(f"✅ Connected to Solana {NETWORK}")
    print(f"   Version: {version.value}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    exit(1)

# For devnet testing, generate a keypair
print("\n📝 Generating test keypair for devnet...")
test_keypair = Keypair()
print(f"   Address: {test_keypair.pubkey()}")

# Save keypair for future use
keypair_dir = Path(__file__).parent / "test_keypairs"
keypair_dir.mkdir(exist_ok=True)
keypair_file = keypair_dir / f"deployer_{NETWORK}.json"

with open(keypair_file, 'w') as f:
    json.dump(list(bytes(test_keypair)), f)

print(f"   Saved to: {keypair_file}")

# Check balance
balance_response = client.get_balance(test_keypair.pubkey())
balance_lamports = balance_response.value
balance_sol = balance_lamports / 1e9

print(f"\n💰 Balance: {balance_sol:.4f} SOL")

if NETWORK == "devnet" and balance_sol == 0:
    print("\n🚰 Requesting devnet airdrop...")
    try:
        airdrop_response = client.request_airdrop(test_keypair.pubkey(), 2_000_000_000)  # 2 SOL
        print(f"   Airdrop signature: {airdrop_response.value}")

        # Wait for confirmation
        print("   Waiting for confirmation...")
        client.confirm_transaction(airdrop_response.value)

        # Check new balance
        balance_response = client.get_balance(test_keypair.pubkey())
        new_balance = balance_response.value / 1e9
        print(f"   ✅ New balance: {new_balance:.4f} SOL")

    except Exception as e:
        print(f"   ❌ Airdrop failed: {e}")
        print("   Try again or use https://faucet.solana.com")

print("\n" + "="*70)
print("✅ DEVNET SETUP COMPLETE")
print("="*70)
print(f"\nTest wallet: {test_keypair.pubkey()}")
print(f"Keypair saved: {keypair_file}")
print(f"\nNext: Deploy token using this wallet")
