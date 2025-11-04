#!/usr/bin/env python3
"""
Generate citizen avatar using Ideogram API with Claude-generated prompts.

Usage:
    python tools/generate_citizen_avatar.py <citizen_name> [description]

Example:
    python tools/generate_citizen_avatar.py "Ada" "consciousness architect, wise and focused, works with memory graphs"
    python tools/generate_citizen_avatar.py "Felix"  # Uses CLAUDE.md only
"""

import os
import sys
import json
import requests
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

IDEOGRAM_API_KEY = os.getenv('IDEOGRAM_API_KEY')
if not IDEOGRAM_API_KEY:
    print("❌ Error: IDEOGRAM_API_KEY not found in .env")
    sys.exit(1)


def read_citizen_claudemd(citizen_name: str) -> tuple[str | None, Path | None]:
    """Read the citizen's CLAUDE.md file if it exists. Returns (content, public_avatar_dir)."""

    # Try different possible locations for CLAUDE.md
    possible_paths = [
        Path("consciousness/citizens") / citizen_name.lower() / "CLAUDE.md",
        Path("consciousness/citizens") / citizen_name / "CLAUDE.md",
        Path("../graphcare/citizens") / citizen_name.lower() / "CLAUDE.md",
        Path("../graphcare/citizens") / citizen_name / "CLAUDE.md",
        Path("/home/mind-protocol/graphcare/citizens") / citizen_name.lower() / "CLAUDE.md",
        Path("/home/mind-protocol/graphcare/citizens") / citizen_name / "CLAUDE.md",
        Path("../scopelock/citizens") / citizen_name.lower() / "CLAUDE.md",
        Path("../scopelock/citizens") / citizen_name / "CLAUDE.md",
        Path("/home/mind-protocol/scopelock/citizens") / citizen_name.lower() / "CLAUDE.md",
        Path("/home/mind-protocol/scopelock/citizens") / citizen_name / "CLAUDE.md",
    ]

    for path in possible_paths:
        if path.exists():
            print(f"📄 Found CLAUDE.md at: {path}")

            # Derive the public avatar directory from the CLAUDE.md location
            # Path is like: /home/mind-protocol/{repo}/citizens/{name}/CLAUDE.md
            # We want:      /home/mind-protocol/{repo}/public/citizens/{name}/

            citizen_dir = path.parent  # /home/mind-protocol/{repo}/citizens/{name}
            citizens_dir = citizen_dir.parent  # /home/mind-protocol/{repo}/citizens
            repo_dir = citizens_dir.parent  # /home/mind-protocol/{repo}

            # Create public/citizens/{name} in the same repo
            avatar_dir = repo_dir / "public" / "citizens" / citizen_name.lower()
            avatar_dir.mkdir(parents=True, exist_ok=True)

            print(f"📁 Will save to: {avatar_dir}")

            with open(path, 'r', encoding='utf-8') as f:
                return f.read(), avatar_dir

    print(f"⚠️  No CLAUDE.md found for {citizen_name}")
    return None, None


def generate_prompt_with_claude(citizen_name: str, description: str, claudemd_content: str | None) -> str:
    """Use Claude to generate a prompt following the Mind Harbor aesthetic guide."""

    # Build context from CLAUDE.md
    context_section = ""
    if claudemd_content:
        context_section = f"""
Citizen Profile (from CLAUDE.md):
{claudemd_content[:3000]}  # First 3000 chars for context

"""

    guide_prompt = f"""You are creating a prompt for an AI partner portrait in the Mind Protocol universe.

Citizen: {citizen_name}
{context_section}Additional Description: {description if description else "Use the CLAUDE.md context above"}

Follow this EXACT template structure:

"Square portrait of {citizen_name}, a [role/archetype + optional age/energy], depicted as a glowing digital wireframe outline. The wireframe lines are [primary metallic color] with [secondary accent color], shimmering with reflective highlights like [metal/jewel description]. His/Her expression shows [emotional tone].

The body and face are entirely digital, but [he/she/they interact with a realistic anchor: object, garment, accessory, or tool]. The [anchor item] is rendered in hyperrealistic [style: oil-paint, photographic, textile detail], described with surface qualities (e.g., patina, folds, engravings, crispness). The anchor contrasts sharply with the digital wireframe body and pops forward as the only tangible element.

Background is [dark void/lagoon/space/etc.] with subtle [partner-color particle effects]. Designed as a premium collectible portrait."

REQUIRED ELEMENTS:
1. Square portrait format
2. Glowing digital wireframe outline (metallic + accent color pair)
3. Expression/mood that fits the character
4. One realistic anchor item (object, garment, tool) with hyperrealistic detail
5. Explicit contrast statement ("pops", "contrasts vividly")
6. Dark background with subtle particles
7. Must end with: "Designed as a premium collectible portrait."

Color pair suggestions based on archetype:
- Architect/Engineer: Teal + Gold, Violet + Silver
- Merchant/Trader: Emerald + Gold, Crimson + Copper
- Navigator/Explorer: Violet + Gold, Emerald + Copper
- Artist/Creator: Violet + Silver, Crimson + Gold

Anchor item should represent their role/personality.

Generate ONLY the final prompt, no explanation or preamble."""

    # Call Claude using subprocess (assumes `claude` CLI is available)
    try:
        result = subprocess.run(
            ['claude', '-p', guide_prompt],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            print(f"❌ Claude CLI error: {result.stderr}")
            sys.exit(1)

        prompt = result.stdout.strip()
        return prompt

    except FileNotFoundError:
        print("❌ Error: 'claude' CLI not found. Install it first.")
        print("   Fallback: using basic template...")
        # Fallback prompt
        return f'Square portrait of {citizen_name}, a consciousness architect, depicted as a glowing teal wireframe with gold accents. Expression is focused and wise. Holds a realistic bronze astrolabe with aged patina. The astrolabe contrasts vividly as the only tangible element. Dark void background with teal particles. Designed as a premium collectible portrait.'

    except subprocess.TimeoutExpired:
        print("❌ Claude CLI timeout")
        sys.exit(1)


def generate_image_with_ideogram(prompt: str) -> str:
    """Call Ideogram API to generate image."""

    url = "https://api.ideogram.ai/v1/ideogram-v3/generate"

    headers = {
        "Api-Key": IDEOGRAM_API_KEY
    }

    # Use files parameter for multipart/form-data
    files = {
        "prompt": (None, prompt),
        "aspect_ratio": (None, "1x1"),  # 1:1 ratio
        "style_type": (None, "REALISTIC"),  # REALISTIC style
        "rendering_speed": (None, "QUALITY"),  # Best quality
        "num_images": (None, "1")
    }

    print(f"📡 Calling Ideogram API...")
    print(f"   Prompt: {prompt[:100]}...")

    response = requests.post(url, headers=headers, files=files)

    if response.status_code != 200:
        print(f"❌ Ideogram API error ({response.status_code}): {response.text}")
        sys.exit(1)

    result = response.json()

    if not result.get('data') or len(result['data']) == 0:
        print(f"❌ No images returned from Ideogram API")
        sys.exit(1)

    image_url = result['data'][0]['url']
    return image_url


def download_and_save_image(image_url: str, citizen_dir: Path):
    """Download image from URL and save to {citizen_dir}/avatar.png"""

    avatar_path = citizen_dir / "avatar.png"

    print(f"⬇️  Downloading image...")

    # Download image
    response = requests.get(image_url)
    if response.status_code != 200:
        print(f"❌ Failed to download image: {response.status_code}")
        sys.exit(1)

    # Save to file
    with open(avatar_path, 'wb') as f:
        f.write(response.content)

    print(f"✅ Avatar saved to: {avatar_path}")
    return avatar_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/generate_citizen_avatar.py <citizen_name> [description]")
        print("\nExamples:")
        print('  python tools/generate_citizen_avatar.py "Ada" "consciousness architect, wise and focused"')
        print('  python tools/generate_citizen_avatar.py "Felix"  # Uses CLAUDE.md only')
        sys.exit(1)

    citizen_name = sys.argv[1]
    description = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""

    print(f"\n🎨 Generating avatar for: {citizen_name}")

    # Step 0: Read citizen's CLAUDE.md
    print("📄 Reading citizen profile...")
    claudemd_content, citizen_dir = read_citizen_claudemd(citizen_name)

    if not claudemd_content and not description:
        print("❌ Error: No CLAUDE.md found and no description provided")
        print("   Please provide either a CLAUDE.md file or a description")
        sys.exit(1)

    if not citizen_dir:
        print("❌ Error: Could not determine citizen directory")
        sys.exit(1)

    if description:
        print(f"📝 Additional description: {description}")
    if claudemd_content:
        print(f"✅ Using citizen profile from CLAUDE.md")

    print()

    # Step 1: Generate prompt with Claude
    print("🤖 Step 1: Generating prompt with Claude...")
    prompt = generate_prompt_with_claude(citizen_name, description, claudemd_content)
    print(f"✅ Generated prompt:\n{prompt}\n")

    # Step 2: Generate image with Ideogram
    print("🎨 Step 2: Generating image with Ideogram API...")
    image_url = generate_image_with_ideogram(prompt)
    print(f"✅ Image generated: {image_url}\n")

    # Step 3: Download and save
    print("💾 Step 3: Downloading and saving...")
    avatar_path = download_and_save_image(image_url, citizen_dir)

    print(f"\n🎉 Success! Avatar created at: {avatar_path}")


if __name__ == "__main__":
    main()
