#!/usr/bin/env python3
"""
Test banking integration setup
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def check_file_exists(path: str, description: str) -> bool:
    """Check if a file exists"""
    expanded_path = Path(path).expanduser()
    if expanded_path.exists():
        print(f"✅ {description}: {expanded_path}")
        return True
    else:
        print(f"❌ {description}: Not found at {expanded_path}")
        return False


def check_env_var(var: str, required: bool = True) -> bool:
    """Check if environment variable is set"""
    value = os.getenv(var)
    if value:
        # Mask sensitive values
        if "KEY" in var or "SESSION" in var:
            display_value = value[:10] + "..." if len(value) > 10 else "***"
        else:
            display_value = value
        print(f"✅ {var}: {display_value}")
        return True
    else:
        status = "❌" if required else "⚠️"
        print(f"{status} {var}: Not set")
        return not required


def main():
    """Run setup tests"""
    print("=" * 60)
    print("Mind Protocol - Banking Integration Setup Test")
    print("=" * 60)
    print()

    from dotenv import load_dotenv
    load_dotenv()

    all_ok = True

    print("1. Checking Python dependencies...")
    try:
        import jwt
        import requests
        import cryptography
        print("✅ All dependencies installed")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Run: pip install -r tools/banking/requirements.txt")
        all_ok = False

    print()
    print("2. Checking private key...")
    key_path = os.getenv("ENABLE_BANKING_PRIVATE_KEY_PATH", "~/.secrets/MISSING.pem")
    if not check_file_exists(key_path, "Private key"):
        print("   Download from: https://enablebanking.com/applications")
        print("   Move to: ~/.secrets/")
        all_ok = False

    print()
    print("3. Checking environment variables...")
    vars_ok = all([
        check_env_var("ENABLE_BANKING_APP_ID", required=True),
        check_env_var("ENABLE_BANKING_PRIVATE_KEY_PATH", required=True),
        check_env_var("ENABLE_BANKING_REDIRECT_URL", required=False),
        check_env_var("REVOLUT_SESSION_ID", required=False),
        check_env_var("REVOLUT_ACCOUNT_UID", required=False),
    ])
    all_ok = all_ok and vars_ok

    print()
    print("4. Testing JWT generation...")
    if os.getenv("ENABLE_BANKING_APP_ID") and os.getenv("ENABLE_BANKING_PRIVATE_KEY_PATH"):
        try:
            from lib.jwt_generator import JWTGenerator
            generator = JWTGenerator(
                os.getenv("ENABLE_BANKING_APP_ID"),
                os.getenv("ENABLE_BANKING_PRIVATE_KEY_PATH")
            )
            token, exp = generator.generate_token()
            print(f"✅ JWT generation successful (expires: {exp})")
        except Exception as e:
            print(f"❌ JWT generation failed: {e}")
            all_ok = False
    else:
        print("⚠️  Skipping JWT test (missing configuration)")

    print()
    print("=" * 60)
    if all_ok:
        print("✅ Setup complete! Next steps:")
        print()
        print("1. Run authorization:")
        print("   python tools/banking/scripts/authorize.py")
        print()
        print("2. Check balance:")
        print("   python tools/banking/scripts/check_balance.py")
    else:
        print("❌ Setup incomplete. Fix the issues above.")
        print()
        print("Setup guide:")
        print("  docs/banking/banking-integration/revolut-account-access/")
        print("  oauth-authorization/how-to-integrate-revolut/README.md")
    print("=" * 60)

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
