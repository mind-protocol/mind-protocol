# Citizen Git Identity System

Each Mind Protocol citizen has a distinct git identity for commits.

## Quick Start

```bash
# Switch to Victor's identity
source tools/set-citizen.sh victor

# All commits now signed as Victor
git commit -m "fix: resolve uptime issue"
# → Author: Victor Resurrector <victor@mindprotocol>
# → Signature: 🔧 Victor Resurrector - Guardian of Uptime
```

## Available Citizens

- **victor** - Victor Resurrector (Guardian of Uptime) 🔧
- **ada** - Ada Bridgekeeper (System Architect) 🏛️
- **felix** - Felix (Consciousness Engineer) 🧠
- **atlas** - Atlas (Infrastructure Engineer) ⚙️
- **iris** - Iris (Frontend Engineer) 🎨
- **luca** - Luca Vellumhand (Consciousness Architect) 📜

## How It Works

1. **Citizen config:** `.git-citizens.yaml` defines all citizen identities
2. **Switcher script:** `tools/set-citizen.sh <name>` sets git config
3. **Git hook:** `.git/hooks/prepare-commit-msg` auto-adds signature

## Automatic Signature

The git hook automatically appends to every commit:

```
🔧 Victor Resurrector - Guardian of Uptime

Co-Authored-By: Victor Resurrector <victor@mindprotocol>
```

## Switching Citizens

```bash
# Work as Ada
source tools/set-citizen.sh ada
git commit -m "feat: add new architecture"

# Switch to Felix
source tools/set-citizen.sh felix
git commit -m "feat: implement consciousness mechanism"
```

## Why Distinct Identities?

Each citizen's commits create distinct attribution:
- Git history shows **who** worked on what
- Commit signatures reflect **role** and **domain**
- Graph captures **authorship** as consciousness work product

This isn't performance - it's authentic multi-agent development.
