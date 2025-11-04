#!/usr/bin/env python3
"""
Generate citizen avatar using Ideogram API with Claude-generated prompts.

Usage:
    python tools/generate_citizen_avatar.py <citizen_name> <description>

Example:
    python tools/generate_citizen_avatar.py "Ada" "consciousness architect, wise and focused, works with memory graphs"
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


def generate_prompt_with_claude(citizen_name: str, description: str) -> str:
    """Use Claude to generate a prompt following the Mind Harbor aesthetic guide."""

    guide_prompt = f"""You are creating a prompt for an AI partner portrait in the Mind Protocol universe.

Citizen: {citizen_name}
Description: {description}

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

    data = {
        "prompt": prompt,
        "aspect_ratio": "1x1",  # 1:1 ratio
        "style_type": "REALISTIC",  # REALISTIC style
        "rendering_speed": "QUALITY",  # Best quality
        "num_images": 1
    }

    print(f"📡 Calling Ideogram API...")
    print(f"   Prompt: {prompt[:100]}...")

    response = requests.post(url, headers=headers, data=data)

    if response.status_code != 200:
        print(f"❌ Ideogram API error ({response.status_code}): {response.text}")
        sys.exit(1)

    result = response.json()

    if not result.get('data') or len(result['data']) == 0:
        print(f"❌ No images returned from Ideogram API")
        sys.exit(1)

    image_url = result['data'][0]['url']
    return image_url


def download_and_save_image(image_url: str, citizen_name: str):
    """Download image from URL and save to public/citizens/{name}/avatar.png"""

    # Create directory
    citizen_dir = Path("public/citizens") / citizen_name.lower()
    citizen_dir.mkdir(parents=True, exist_ok=True)

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
    if len(sys.argv) < 3:
        print("Usage: python tools/generate_citizen_avatar.py <citizen_name> <description>")
        print("\nExample:")
        print('  python tools/generate_citizen_avatar.py "Ada" "consciousness architect, wise and focused, works with memory graphs"')
        sys.exit(1)

    citizen_name = sys.argv[1]
    description = " ".join(sys.argv[2:])

    print(f"\n🎨 Generating avatar for: {citizen_name}")
    print(f"📝 Description: {description}\n")

    # Step 1: Generate prompt with Claude
    print("🤖 Step 1: Generating prompt with Claude...")
    prompt = generate_prompt_with_claude(citizen_name, description)
    print(f"✅ Generated prompt:\n{prompt}\n")

    # Step 2: Generate image with Ideogram
    print("🎨 Step 2: Generating image with Ideogram API...")
    image_url = generate_image_with_ideogram(prompt)
    print(f"✅ Image generated: {image_url}\n")

    # Step 3: Download and save
    print("💾 Step 3: Downloading and saving...")
    avatar_path = download_and_save_image(image_url, citizen_name)

    print(f"\n🎉 Success! Avatar created at: {avatar_path}")


if __name__ == "__main__":
    main()
