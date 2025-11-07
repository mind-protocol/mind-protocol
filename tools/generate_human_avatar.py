#!/usr/bin/env python3
"""
Generate human partner avatar using Ideogram API with Claude-generated prompts.

Uses the REVERSE style: photorealistic animal + glowing digital tool/portal
(opposite of AI partners: wireframe + real object)

Animals represent human archetypes while avoiding uncanny valley.

Usage:
    python tools/generate_human_avatar.py <name> <role> <animal> [additional_description]

Example:
    python tools/generate_human_avatar.py "Nicolas" "developer" "fox" "clever problem-solver"
    python tools/generate_human_avatar.py "Sarah" "systems-architect" "eagle"
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


def generate_prompt_with_claude(name: str, role: str, animal: str, description: str) -> str:
    """Use Claude to generate a prompt following the Human Partner aesthetic guide."""

    guide_prompt = f"""You are creating a prompt for a HUMAN partner portrait in the Mind Protocol universe.

This is the REVERSE style of AI partners:
- AI Partners: Digital wireframe bodies + real physical anchor
- Human Partners: Photorealistic animal + glowing digital tool/portal

Animals represent human archetypes and avoid uncanny valley.

Name: {name}
Role: {role}
Animal: {animal}
Additional Description: {description if description else "Generate based on role and animal archetype"}

Follow this EXACT template structure:

"Square portrait of {name} embodied as a [adjective describing animal personality] {animal}, a [role/profession], depicted in photorealistic detail with [lighting style: cinematic, studio, dramatic]. The {animal}'s [fur/feathers/scales] show realistic texture, natural [coloring], and [expression/mood].

The animal is entirely photorealistic, but [he/she/they interact with a glowing digital tool/interface/portal]. The [digital element] is rendered as [wireframe/holographic/light-traced geometry] in [metallic color] with [accent color] accents, shimmering with [digital effect: particle streams, data flows, code fragments]. The digital tool contrasts sharply with the photorealistic {animal} and pops forward as the only ethereal element.

Background is [dark void/cosmic space/tech noir] with subtle [color] digital particles. Designed as a premium collectible portrait."

CRITICAL REQUIREMENTS:
1. Square portrait format
2. Animal MUST be photorealistic - realistic fur/feathers/scales, natural coloring, cinematic lighting
3. Emphasize: "photorealistic detail", "realistic texture", "{animal}'s [fur/feathers/scales]"
4. Expression/mood that fits the person's role AND animal personality
5. One digital tool/portal (wireframe/holographic/light-traced) - this is the ONLY ethereal element
6. Explicit contrast: digital tool "pops forward as the only ethereal element"
7. Dark background with subtle particles
8. Must end with: "Designed as a premium collectible portrait."

Color pair suggestions based on role:
- Developer/Engineer: Teal + Gold (code weaver, builder)
- Designer/Product: Emerald + Silver (interface architect)
- Architect/Systems: Violet + Gold (portal walker, strategist)
- Analyst/Data: Emerald + Silver (data summoner)
- Fast Executor: Crimson + Copper

Digital tool suggestions by role:
- Developer: Glowing holographic keyboard with code streams
- Systems Architect: Vertical portal gateway with digital landscape
- Data Scientist: Glowing data orb with visualizations
- UI Designer: Floating holographic interface panels
- DevOps: Holographic command console

The digital tool should:
- Be wireframe/holographic (NOT solid)
- Show particle effects (streams, trails, dissolving pixels)
- Represent the person's function
- Contrast vividly with photorealistic human

Generate ONLY the final prompt, no explanation or preamble."""

    # Call Claude using subprocess (assumes `claude` CLI is available)
    try:
        result = subprocess.run(
            ['claude', '-p', guide_prompt],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            print(f"❌ Claude CLI error: {result.stderr}")
            sys.exit(1)

        prompt = result.stdout.strip()
        return prompt

    except FileNotFoundError:
        print("❌ Error: 'claude' CLI not found. Install it first.")
        print("   Fallback: using basic template...")
        # Fallback prompt based on role and animal
        if role.lower() in ["developer", "engineer", "coder"]:
            return f'Square portrait of {name} embodied as a clever {animal}, a {role} and problem-solver, depicted in photorealistic cinematic lighting. The {animal}\'s fur shows realistic texture, natural coloring, alert eyes, and a focused, intelligent expression. The {animal}\'s paws rest on a glowing holographic keyboard rendered as wireframe light-traced geometry in metallic teal with gold accents. Code streams flow from the keys as luminous particle trails. The keyboard contrasts vividly with the {animal}\'s solid form. Dark void background with teal-gold code fragments. Designed as a premium collectible portrait.'
        else:
            return f'Square portrait of {name} embodied as a {animal}, a {role}, depicted in photorealistic detail. The {animal}\'s fur/feathers show realistic texture, natural coloring. Expression shows confident focus. They interact with a glowing holographic interface in teal with gold accents. The interface contrasts sharply with the photorealistic {animal}. Dark background with teal particles. Designed as a premium collectible portrait.'

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


def download_and_save_image(image_url: str, name: str) -> Path:
    """Download image from URL and save to public/humans/{name}/avatar.png"""

    # Determine save location
    # Try to find the mindprotocol repo
    possible_bases = [
        Path.cwd(),
        Path("/home/mind-protocol/mindprotocol"),
        Path("../mindprotocol"),
    ]

    repo_dir = None
    for base in possible_bases:
        if (base / "tools").exists():
            repo_dir = base
            break

    if not repo_dir:
        print("❌ Could not find repository root")
        sys.exit(1)

    # Create public/humans/{name} directory
    human_dir = repo_dir / "public" / "humans" / name.lower().replace(" ", "-")
    human_dir.mkdir(parents=True, exist_ok=True)

    avatar_path = human_dir / "avatar.png"

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
    if len(sys.argv) < 4:
        print("Usage: python tools/generate_human_avatar.py <name> <role> <animal> [additional_description]")
        print("\nExamples:")
        print('  python tools/generate_human_avatar.py "Nicolas" "developer" "fox" "clever problem-solver"')
        print('  python tools/generate_human_avatar.py "Sarah" "systems-architect" "eagle"')
        print('  python tools/generate_human_avatar.py "Michael" "data-scientist" "raven"')
        print("\nValid roles:")
        print("  developer, engineer, systems-architect, data-scientist, ui-designer,")
        print("  product-manager, devops, analyst, researcher, architect")
        print("\nAnimal suggestions by role:")
        print("  Developer/Engineer: fox, owl, octopus")
        print("  Systems Architect: eagle, wolf, elephant")
        print("  Designer: hummingbird, peacock, butterfly")
        print("  Data Scientist/Analyst: raven, dolphin, owl")
        print("  Fast Executor: cheetah, falcon, hare")
        sys.exit(1)

    name = sys.argv[1]
    role = sys.argv[2]
    animal = sys.argv[3]
    description = " ".join(sys.argv[4:]) if len(sys.argv) > 4 else ""

    print(f"\n🎨 Generating HUMAN avatar for: {name} ({role})")
    print(f"   Animal archetype: {animal}")
    print("   Style: Photorealistic animal + glowing digital tool")

    if description:
        print(f"📝 Additional description: {description}")

    print()

    # Step 1: Generate prompt with Claude
    print("🤖 Step 1: Generating prompt with Claude...")
    prompt = generate_prompt_with_claude(name, role, animal, description)
    print(f"✅ Generated prompt:\n{prompt}\n")

    # Step 2: Generate image with Ideogram
    print("🎨 Step 2: Generating image with Ideogram API...")
    image_url = generate_image_with_ideogram(prompt)
    print(f"✅ Image generated: {image_url}\n")

    # Step 3: Download and save
    print("💾 Step 3: Downloading and saving...")
    avatar_path = download_and_save_image(image_url, name)

    print(f"\n🎉 Success! Human avatar created at: {avatar_path}")
    print(f"   Style: Photorealistic {animal} + digital tool (reverse of AI wireframe)")


if __name__ == "__main__":
    main()
