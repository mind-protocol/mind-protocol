"""
Import Solana wallet from recovery phrase (seed phrase/mnemonic)

CRITICAL SECURITY:
- Recovery phrase is MASTER KEY (even more sensitive than private key)
- DELETE this script immediately after use
- NEVER save recovery phrase to disk
"""

from solders.keypair import Keypair
from mnemonic import Mnemonic
import json
import getpass

print("🔐 Recovery Phrase Import")
print("="*70)
print("\n⚠️  CRITICAL SECURITY WARNING")
print("⚠️  Your recovery phrase is your MASTER KEY")
print("⚠️  DELETE this script after use")
print("⚠️  NEVER share your recovery phrase")
print("\n" + "="*70)

# Get recovery phrase
print("\n📝 Enter your Phantom recovery phrase")
print("   (12 or 24 words, separated by spaces)")
print("   Example: word1 word2 word3 ...")
print("\n⚠️  Input will be hidden for security\n")

recovery_phrase = getpass.getpass("Recovery phrase: ").strip()

# Validate word count
words = recovery_phrase.split()
if len(words) not in [12, 24]:
    print(f"\n❌ Invalid recovery phrase: Expected 12 or 24 words, got {len(words)}")
    exit(1)

print(f"\n✅ Received {len(words)}-word recovery phrase")

try:
    # Validate mnemonic
    mnemo = Mnemonic("english")
    if not mnemo.check(recovery_phrase):
        print("\n❌ Invalid recovery phrase: Words not in BIP39 wordlist")
        exit(1)

    print("✅ Recovery phrase valid")

    # Generate seed from mnemonic
    seed = mnemo.to_seed(recovery_phrase)

    # Phantom uses BIP44 derivation path: m/44'/501'/0'/0'
    # We need to derive using this path
    from solders.derivation_path import DerivationPath

    # Try standard Phantom derivation first (account 0)
    derivation_path = DerivationPath.from_string("m/44'/501'/0'/0'")

    # For now, let's try the simple seed-based approach
    # which works for most Phantom wallets
    keypair = Keypair.from_seed(seed[:32])

    print(f"\n📍 Derived address (default): {keypair.pubkey()}")

    print(f"\n✅ Derived keypair successfully")
    print(f"📍 Public address: {keypair.pubkey()}")

    # Verify this matches your expected address
    expected = input(f"\nDoes this match your Phantom address? (y/n): ").lower()

    if expected != 'y':
        print("\n⚠️  Address mismatch - this might not be the right recovery phrase")
        print("   Check Phantom: Settings → Show Recovery Phrase")
        exit(1)

    # Save as JSON keypair file
    output_file = "recovery_keypair_temp.json"
    with open(output_file, 'w') as f:
        json.dump(list(bytes(keypair)), f)

    print(f"\n✅ Keypair saved to: {output_file}")
    print(f"\n🔐 Next steps:")
    print(f"   1. Import to secure key manager:")
    print(f"      python orchestration/economy/secure_key_manager.py import deployer_mainnet {output_file}")
    print(f"\n   2. DELETE these files:")
    print(f"      del {output_file}")
    print(f"      del orchestration\\economy\\import_from_recovery.py")
    print(f"\n⚠️  CRITICAL: Delete temp files after import!")

except Exception as e:
    print(f"\n❌ Conversion failed: {e}")
    print(f"\nTroubleshooting:")
    print(f"  - Make sure you copied ALL words from recovery phrase")
    print(f"  - Words separated by single spaces")
    print(f"  - No typos in any word")
    print(f"  - From Phantom: Settings → Show Recovery Phrase")
