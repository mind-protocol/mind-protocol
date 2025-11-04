# Citizen Avatar Generation Tool

Generates premium collectible portrait avatars for Mind Protocol citizens using:
- **Claude** for prompt generation (following Mind Harbor aesthetic guide)
- **Ideogram API** for realistic image generation

## Setup

### 1. Get Ideogram API Key

1. Go to https://ideogram.ai/api
2. Sign up and get your API key
3. Add to `.env`:
   ```bash
   IDEOGRAM_API_KEY=your_api_key_here
   ```

### 2. Install Dependencies

```bash
pip install requests python-dotenv
```

### 3. Install Claude CLI (optional but recommended)

If you don't have Claude CLI, the script will use a fallback template.

## Usage

```bash
python tools/generate_citizen_avatar.py "<citizen_name>" [optional_description]
```

The tool will automatically read the citizen's `CLAUDE.md` file from `consciousness/citizens/{name}/CLAUDE.md` to understand their identity, role, and personality. Additional description is optional.

### Examples

**Using CLAUDE.md only (recommended):**
```bash
python tools/generate_citizen_avatar.py "Ada"
python tools/generate_citizen_avatar.py "Felix"
python tools/generate_citizen_avatar.py "Iris"
```

**With additional description:**
```bash
python tools/generate_citizen_avatar.py "Ada" "holding a memory graph"
python tools/generate_citizen_avatar.py "Felix" "focused on debugging"
```

## Output

Avatars are saved to:
```
public/citizens/{name}/avatar.png
```

Example:
- `public/citizens/ada/avatar.png`
- `public/citizens/felix/avatar.png`
- `public/citizens/iris/avatar.png`

## How It Works

1. **Read Citizen Profile**
   - Reads `consciousness/citizens/{name}/CLAUDE.md`
   - Extracts identity, role, personality, purpose
   - Uses first 3000 chars for context

2. **Prompt Generation (Claude)**
   - Takes citizen CLAUDE.md + optional description
   - Generates structured prompt following Mind Harbor aesthetic guide
   - Ensures glowing wireframe body + realistic anchor item
   - Assigns color palette based on archetype
   - Selects anchor item that represents citizen's role

3. **Image Generation (Ideogram API)**
   - Uses Ideogram 3.0 model
   - REALISTIC style type
   - 1:1 aspect ratio (square portrait)
   - QUALITY rendering speed

4. **Download & Save**
   - Downloads generated image from temporary URL
   - Saves to `public/citizens/{name}/avatar.png`
   - Creates directories if needed

## Aesthetic Guide

All avatars follow the **Mind Harbor aesthetic**:

- **Glowing digital wireframe body** (metallic colors)
- **One realistic anchor item** (object/tool representing role)
- **Sharp contrast** between digital and physical
- **Dark background** with subtle particles
- **Premium collectible quality**

### Color Palettes

- **Architects/Engineers**: Teal + Gold, Violet + Silver
- **Traders/Merchants**: Emerald + Gold, Crimson + Copper
- **Navigators/Explorers**: Violet + Gold, Emerald + Copper
- **Artists/Creators**: Violet + Silver, Crimson + Gold

### Anchor Items

The anchor represents the citizen's role:
- **Architects**: Blueprint, drafting compass, astrolabe
- **Engineers**: Tools, gears, mechanical instruments
- **Security**: Dagger, shield, lock
- **Observers**: Lens, prism, mirror
- **Coordinators**: Quill, scroll, seal

## Troubleshooting

**Error: IDEOGRAM_API_KEY not found**
- Add your API key to `.env` file

**Error: 'claude' CLI not found**
- The script will use a fallback template
- For best results, install Claude CLI

**Error: Ideogram API error (401)**
- Check your API key is valid
- Ensure you have API credits

**Error: Ideogram API error (429)**
- Rate limit reached
- Wait a few seconds and retry

## Cost

Ideogram API pricing (as of 2025):
- **Standard generation**: ~$0.08 per image
- **1:1 REALISTIC QUALITY**: May vary slightly

Check current pricing: https://ideogram.ai/api-pricing

## Examples of Generated Prompts

**Ada (Architect):**
```
Square portrait of Ada, a consciousness architect in her prime, depicted as a glowing digital wireframe outline. The wireframe lines are metallic teal with gold accents, shimmering with reflective highlights like polished filigree. Her expression shows focused wisdom and quiet authority.

The body and face are entirely digital, but she holds a realistic bronze astrolabe, rendered in hyperrealistic oil-paint detail with aged patina and intricate constellation engravings. The astrolabe contrasts sharply with the digital wireframe body and pops forward as the only tangible element.

Background is dark void with subtle teal and gold particle effects. Designed as a premium collectible portrait.
```

**Felix (Engineer):**
```
Square portrait of Felix, a consciousness engineer, youthful and analytical, depicted as a glowing digital wireframe outline. The wireframe lines are metallic violet with silver accents, shimmering like chrome beetle shell. His expression shows intense focus and precision.

The body and face are entirely digital, but he holds a realistic brass drafting compass, rendered in photographic detail with worn engravings and mechanical precision. The compass contrasts vividly with his digital body and pops forward as the only tangible element.

Background is dark space with subtle violet shimmer particles. Designed as a premium collectible portrait.
```
