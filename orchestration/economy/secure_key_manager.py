"""
Secure Key Management for $MIND Token Economy

CRITICAL SECURITY:
- Private keys NEVER appear in logs
- Keys encrypted at rest
- Decrypted only in memory during signing
- Keys stored OUTSIDE conversation/graph system
"""

import os
import json
import getpass
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64

from solders.keypair import Keypair


class SecureKeyManager:
    """Manage encrypted keypairs securely"""

    def __init__(self, keys_dir: Optional[str] = None):
        """
        Initialize key manager

        Args:
            keys_dir: Directory for encrypted keys (default: ~/.solana_keys)
        """
        if keys_dir is None:
            # Store keys OUTSIDE the mind-protocol repo
            keys_dir = Path.home() / ".solana_keys"

        self.keys_dir = Path(keys_dir)
        self.keys_dir.mkdir(exist_ok=True, mode=0o700)  # Restricted permissions

        # NEVER log the keys directory path with actual keys
        print(f"🔐 Key storage: {self.keys_dir}")

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password"""
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def create_keypair(
        self,
        name: str,
        password: Optional[str] = None
    ) -> Keypair:
        """
        Generate new keypair and encrypt it

        Args:
            name: Keypair name (e.g., 'deployer_mainnet')
            password: Encryption password (prompts if not provided)

        Returns:
            Keypair (in memory only)
        """
        print(f"\n🔑 Creating new keypair: {name}")

        # Generate keypair
        keypair = Keypair()
        print(f"   Public address: {keypair.pubkey()}")

        # Get password
        if password is None:
            password = getpass.getpass("   Enter encryption password: ")
            confirm = getpass.getpass("   Confirm password: ")

            if password != confirm:
                raise ValueError("Passwords don't match")

        # Generate salt
        salt = os.urandom(16)

        # Derive encryption key
        key = self._derive_key(password, salt)
        fernet = Fernet(key)

        # Encrypt keypair
        keypair_bytes = bytes(keypair)
        encrypted = fernet.encrypt(keypair_bytes)

        # Save encrypted keypair + salt
        keypair_file = self.keys_dir / f"{name}.encrypted"

        with open(keypair_file, 'wb') as f:
            f.write(salt + encrypted)

        # Restrict file permissions
        os.chmod(keypair_file, 0o600)

        print(f"   ✅ Encrypted keypair saved")
        print(f"   Location: {keypair_file}")
        print(f"\n   ⚠️  NEVER share this password!")
        print(f"   ⚠️  NEVER commit this file to git!")

        return keypair

    def load_keypair(
        self,
        name: str,
        password: Optional[str] = None
    ) -> Keypair:
        """
        Load and decrypt keypair

        Args:
            name: Keypair name
            password: Decryption password (prompts if not provided)

        Returns:
            Keypair (in memory only)
        """
        keypair_file = self.keys_dir / f"{name}.encrypted"

        if not keypair_file.exists():
            raise FileNotFoundError(f"Keypair not found: {name}")

        # Get password
        if password is None:
            password = getpass.getpass(f"🔐 Password for {name}: ")

        # Load encrypted data
        with open(keypair_file, 'rb') as f:
            data = f.read()

        # Extract salt and encrypted keypair
        salt = data[:16]
        encrypted = data[16:]

        # Derive decryption key
        key = self._derive_key(password, salt)
        fernet = Fernet(key)

        try:
            # Decrypt
            keypair_bytes = fernet.decrypt(encrypted)
            keypair = Keypair.from_bytes(keypair_bytes)

            print(f"✅ Keypair loaded: {keypair.pubkey()}")
            return keypair

        except Exception:
            raise ValueError("❌ Incorrect password")

    def import_keypair(
        self,
        name: str,
        keypair_json_path: str,
        password: Optional[str] = None
    ):
        """
        Import existing keypair and encrypt it

        Args:
            name: Name for encrypted keypair
            keypair_json_path: Path to existing keypair JSON
            password: Encryption password (prompts if not provided)
        """
        print(f"\n📥 Importing keypair: {keypair_json_path}")

        # Load existing keypair
        with open(keypair_json_path, 'r') as f:
            secret = json.load(f)

        keypair = Keypair.from_bytes(bytes(secret))
        print(f"   Public address: {keypair.pubkey()}")

        # Get password
        if password is None:
            password = getpass.getpass("   Enter encryption password: ")
            confirm = getpass.getpass("   Confirm password: ")

            if password != confirm:
                raise ValueError("Passwords don't match")

        # Generate salt
        salt = os.urandom(16)

        # Derive encryption key
        key = self._derive_key(password, salt)
        fernet = Fernet(key)

        # Encrypt
        keypair_bytes = bytes(keypair)
        encrypted = fernet.encrypt(keypair_bytes)

        # Save
        encrypted_file = self.keys_dir / f"{name}.encrypted"

        with open(encrypted_file, 'wb') as f:
            f.write(salt + encrypted)

        os.chmod(encrypted_file, 0o600)

        print(f"   ✅ Keypair encrypted and imported")
        print(f"   Location: {encrypted_file}")
        print(f"\n   ⚠️  You can now DELETE the original JSON file")
        print(f"   ⚠️  Keep this password SAFE")

    def list_keypairs(self):
        """List all encrypted keypairs"""
        print(f"\n🔑 Encrypted Keypairs:")

        files = list(self.keys_dir.glob("*.encrypted"))

        if not files:
            print("   (none)")
            return

        for f in files:
            name = f.stem
            print(f"   • {name}")


def main():
    """Interactive key management"""
    import sys

    manager = SecureKeyManager()

    print("\n" + "="*70)
    print("🔐 SECURE KEY MANAGER")
    print("="*70)

    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python secure_key_manager.py create <name>")
        print("  python secure_key_manager.py import <name> <keypair.json>")
        print("  python secure_key_manager.py list")
        print("\nExamples:")
        print("  python secure_key_manager.py create deployer_mainnet")
        print("  python secure_key_manager.py import deployer ~/.config/solana/id.json")
        return

    command = sys.argv[1]

    if command == "create":
        if len(sys.argv) < 3:
            print("❌ Usage: create <name>")
            return
        name = sys.argv[2]
        manager.create_keypair(name)

    elif command == "import":
        if len(sys.argv) < 4:
            print("❌ Usage: import <name> <keypair.json>")
            return
        name = sys.argv[2]
        json_path = sys.argv[3]
        manager.import_keypair(name, json_path)

    elif command == "list":
        manager.list_keypairs()

    else:
        print(f"❌ Unknown command: {command}")


if __name__ == "__main__":
    main()
