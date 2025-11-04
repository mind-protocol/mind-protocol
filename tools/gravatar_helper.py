#!/usr/bin/env python3
"""
Gravatar Helper - Generate hashes, check status, create placeholder avatars
"""

import hashlib
import requests
from pathlib import Path

CITIZENS = {
    "victor": {
        "email": "victor@mindprotocol.ai",
        "name": "Victor Resurrector",
        "theme": "Industrial/mechanical (gears, wrench, server rack)",
        "emoji": "🔧",
        "color": "#FF6B35"  # Orange-red
    },
    "ada": {
        "email": "ada@mindprotocol.ai",
        "name": "Ada Bridgekeeper",
        "theme": "Architectural/bridge (blueprint, compass, keystone)",
        "emoji": "🏛️",
        "color": "#4ECDC4"  # Teal
    },
    "felix": {
        "email": "felix@mindprotocol.ai",
        "name": "Felix",
        "theme": "Neural/brain (neural network, synapses)",
        "emoji": "🧠",
        "color": "#A06CD5"  # Purple
    },
    "atlas": {
        "email": "atlas@mindprotocol.ai",
        "name": "Atlas",
        "theme": "Infrastructure (foundation, pillars, world-bearer)",
        "emoji": "⚙️",
        "color": "#6C757D"  # Gray
    },
    "iris": {
        "email": "iris@mindprotocol.ai",
        "name": "Iris",
        "theme": "Visual/artistic (eye, palette, vision)",
        "emoji": "🎨",
        "color": "#F72585"  # Pink
    },
    "luca": {
        "email": "luca@mindprotocol.ai",
        "name": "Luca Vellumhand",
        "theme": "Manuscript/scroll (quill, vellum, ancient text)",
        "emoji": "📜",
        "color": "#DBA159"  # Gold
    }
}

def email_to_gravatar_hash(email: str) -> str:
    """Convert email to Gravatar MD5 hash"""
    return hashlib.md5(email.strip().lower().encode('utf-8')).hexdigest()

def check_gravatar_exists(email: str) -> bool:
    """Check if Gravatar exists for email"""
    hash_val = email_to_gravatar_hash(email)
    url = f"https://www.gravatar.com/avatar/{hash_val}?d=404"

    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def get_gravatar_url(email: str, size: int = 200) -> str:
    """Get Gravatar URL for email"""
    hash_val = email_to_gravatar_hash(email)
    return f"https://www.gravatar.com/avatar/{hash_val}?s={size}&d=identicon"

def generate_placeholder_svg(citizen_name: str, output_path: str):
    """Generate simple SVG placeholder avatar"""
    citizen = CITIZENS[citizen_name]
    emoji = citizen["emoji"]
    color = citizen["color"]

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <rect width="200" height="200" fill="{color}"/>
  <text x="100" y="120" font-size="80" text-anchor="middle" fill="white">{emoji}</text>
</svg>'''

    with open(output_path, 'w') as f:
        f.write(svg)

    print(f"✅ Created placeholder: {output_path}")

def main():
    print("=" * 60)
    print("Mind Protocol - Gravatar Helper")
    print("=" * 60)

    print("\n📧 Citizen Emails & Gravatar Hashes:\n")

    for citizen_name, info in CITIZENS.items():
        email = info["email"]
        hash_val = email_to_gravatar_hash(email)
        exists = check_gravatar_exists(email)
        status = "✅ EXISTS" if exists else "❌ NOT SET UP"

        print(f"{info['emoji']} {info['name']}")
        print(f"   Email: {email}")
        print(f"   Hash:  {hash_val}")
        print(f"   Status: {status}")
        print(f"   URL:   {get_gravatar_url(email)}")
        print(f"   Theme: {info['theme']}")
        print()

    print("\n" + "=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print()
    print("1. Register each email at: https://gravatar.com")
    print("   (You'll need email access for verification)")
    print()
    print("2. Generate placeholder avatars:")
    print("   python tools/gravatar_helper.py --generate-placeholders")
    print()
    print("3. Upload avatars to Gravatar:")
    print("   - Login to gravatar.com with each email")
    print("   - Upload custom 200x200px avatar")
    print("   - Or use placeholders from ./avatars/")
    print()
    print("4. Verify setup:")
    print("   python tools/gravatar_helper.py --check")
    print()

def generate_all_placeholders():
    """Generate placeholder SVGs for all citizens"""
    output_dir = Path("avatars")
    output_dir.mkdir(exist_ok=True)

    print(f"\n📁 Creating placeholders in {output_dir}/\n")

    for citizen_name in CITIZENS.keys():
        output_path = output_dir / f"{citizen_name}.svg"
        generate_placeholder_svg(citizen_name, str(output_path))

    print(f"\n✅ Created {len(CITIZENS)} placeholder avatars")
    print(f"   Location: {output_dir.absolute()}")
    print()
    print("💡 Convert SVG to PNG for Gravatar upload:")
    print("   inkscape --export-type=png --export-width=200 avatars/*.svg")
    print("   or use: https://cloudconvert.com/svg-to-png")

if __name__ == "__main__":
    import sys

    if "--generate-placeholders" in sys.argv:
        generate_all_placeholders()
    elif "--check" in sys.argv:
        main()
    else:
        main()
