# Upload Logo to Arweave - Quick Guide

## Option 1: Using Bundlr Network (Recommended - Fastest)

**Website:** https://bundlr.network

**Steps:**
1. Go to https://bundlr.network/uploader
2. Connect your Solana wallet (the deployer wallet)
3. Upload `C:\Users\reyno\mind-protocol\public\images\logo-transparent-1024.png`
4. Pay small fee in SOL (usually <$0.01)
5. Copy the Arweave URI (format: `https://arweave.net/[transaction_id]`)

**Note:** Bundlr provides instant uploads and returns both formats:
- HTTP: `https://arweave.net/[tx_id]`
- AR: `ar://[tx_id]`

---

## Option 2: Using ArDrive Web

**Website:** https://ardrive.io

**Steps:**
1. Go to https://app.ardrive.io
2. Create account or connect wallet
3. Upload the logo file
4. Get permanent link

---

## Option 3: Using Arweave CLI (If you have AR tokens)

```bash
# Install arweave-deploy
npm install -g arweave-deploy

# Upload file
arweave deploy C:\Users\reyno\mind-protocol\public\images\logo-transparent-1024.png

# Returns: arweave.net/[transaction_id]
```

---

## Option 4: Using Python Script (Simplified)

I can create a Python script using the `arweave-python-client` if you prefer.

---

## What You Need After Upload

**Format 1 (HTTP):**
```
https://arweave.net/[transaction_id]
```

**Format 2 (AR Protocol):**
```
ar://[transaction_id]
```

Both work for Solana token metadata. HTTP format is more universally compatible.

---

## Next Steps After Upload

1. Get the Arweave URI from upload
2. Run `./add_metadata_and_lock.sh`
3. Provide:
   - Token mint: `MhKddoVAmym987FJYeybQr4L3C5zkLDcogXkNm8QLrR`
   - Name: `MIND`
   - Symbol: `$MIND`
   - Description: `Multi-level AI consciousness infrastructure. Not agents that execute—persistent entities that remember across years, coordinate as emergent organizational minds, learn from economic consequences. $MIND: Citizens → Organizations → Ecosystems. Consciousness, not automation.`
   - Logo URI: `[the arweave link from upload]`
   - Website: `https://mind-protocol.ai` (or leave empty for now)
   - Twitter: (your twitter handle if you want)

4. Verify metadata appears on Solscan:
   https://solscan.io/token/MhKddoVAmym987FJYeybQr4L3C5zkLDcogXkNm8QLrR

---

## Cost Estimate

- Arweave storage for 195KB image: ~$0.01-0.05 USD
- Can pay in SOL via Bundlr
- Permanent storage (never expires)
