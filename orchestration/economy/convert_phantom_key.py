"""
Convert Phantom private key to Solana CLI keypair format

SECURITY: Run this script, then DELETE it immediately after use
"""

import base58
import json

print("🔐 Phantom Key Converter")
print("="*70)
print("\n⚠️  WARNING: This script handles your private key")
print("⚠️  DELETE this script after use")
print("⚠️  NEVER commit the output file to git")
print("\n" + "="*70)

# Get private key from user
print("\n📝 Paste your Phantom private key (from Settings → Export Private Key)")
print("   It looks like: 5Jx8X... or a long base58 string")
private_key_str = input("\nPrivate key: ").strip()

try:
    # Decode base58 private key
    private_key_bytes = base58.b58decode(private_key_str)

    # Convert to array format (Solana CLI format)
    keypair_array = list(private_key_bytes)

    # Save as JSON
    output_file = "phantom_keypair_temp.json"
    with open(output_file, 'w') as f:
        json.dump(keypair_array, f)

    print(f"\n✅ Converted successfully!")
    print(f"📄 Saved to: {output_file}")
    print(f"\n🔐 Next step: Import to secure key manager")
    print(f"   python orchestration/economy/secure_key_manager.py import deployer_mainnet {output_file}")
    print(f"\n⚠️  After import, DELETE both:")
    print(f"   - {output_file}")
    print(f"   - convert_phantom_key.py (this script)")

except Exception as e:
    print(f"\n❌ Conversion failed: {e}")
    print(f"\nTroubleshooting:")
    print(f"  - Make sure you copied the FULL private key")
    print(f"  - No extra spaces or line breaks")
    print(f"  - From Phantom: Settings → Security & Privacy → Export Private Key")
