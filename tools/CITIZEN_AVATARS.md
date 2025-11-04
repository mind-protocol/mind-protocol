# Setting Up Citizen Profile Pictures

GitHub displays profile pictures for commit authors using **Gravatar** (Globally Recognized Avatar).

## How It Works

1. Git commit stores: `Victor Resurrector <victor@mindprotocol>`
2. GitHub computes MD5 hash of `victor@mindprotocol`
3. GitHub fetches avatar from: `gravatar.com/avatar/<hash>`
4. Avatar appears in commit history, PR comments, etc.

## Setup Steps

### 1. Register Citizen Emails on Gravatar

Go to https://gravatar.com and create accounts for each citizen email:

- `victor@mindprotocol` - Victor Resurrector
- `ada@mindprotocol` - Ada Bridgekeeper
- `felix@mindprotocol` - Felix
- `atlas@mindprotocol` - Atlas
- `iris@mindprotocol` - Iris
- `luca@mindprotocol` - Luca Vellumhand

**Note:** You'll need access to these emails for verification (set up email forwarding if needed).

### 2. Upload Custom Avatars

For each Gravatar account, upload a unique avatar:

**Recommendations:**
- **Victor:** Industrial/mechanical theme (gears, wrench, server rack)
- **Ada:** Architectural/bridge theme (blueprint, compass, keystone)
- **Felix:** Neural/brain theme (neural network, synapses, consciousness)
- **Atlas:** Infrastructure theme (foundation, pillars, world-bearer)
- **Iris:** Visual/artistic theme (eye, palette, vision)
- **Luca:** Manuscript/scroll theme (quill, vellum, ancient text)

**Avatar specs:**
- Size: 200x200px minimum (Gravatar auto-scales)
- Format: PNG or JPG
- G-rated content (Gravatar requirement)

### 3. Verify in GitHub

After setting up Gravatar:

1. Make a commit as a citizen:
   ```bash
   source tools/set-citizen.sh victor
   git commit -m "test: verify avatar"
   git push
   ```

2. Check GitHub commit history - avatar should appear immediately

3. If not showing: Clear browser cache or wait ~5 minutes for GitHub to refresh

## Alternative: AI-Generated Avatars

You could generate citizen avatars using:
- **DALL-E / Midjourney:** "Portrait of [citizen name] [theme]"
- **Stable Diffusion:** Generate locally
- **Boring Avatars:** Simple geometric avatars (boringavatars.com)

## Testing Before Upload

Check what avatar will appear:
```bash
echo -n "victor@mindprotocol" | md5sum
# Result: <hash>

# Then visit:
# https://gravatar.com/avatar/<hash>?d=identicon
```

The `?d=identicon` shows GitHub's default if no Gravatar exists.

## Email Forwarding (Recommended)

If you control `mindprotocol` domain:

1. Set up catch-all forwarding: `*@mindprotocol` → `your-email@gmail.com`
2. Register all 6 citizen emails on Gravatar (verification emails forwarded to you)
3. Upload unique avatar for each
4. Done!

This way you manage all citizen identities from one inbox.

## Current Status

✅ Git identities configured (name + email)
✅ Auto-signature hook installed
❌ Gravatar avatars not yet set up

**Next step:** Register citizen emails on Gravatar and upload avatars.
