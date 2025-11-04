# Vercel Auto-Deploy Setup

## Current Status

✅ **vercel.json configured** - Build command and framework set correctly
✅ **Git remote configured** - Connected to `git@github.com:mind-protocol/mindprotocol.git`
✅ **Build script ready** - `npm run build` works locally

## Why Auto-Deploy Might Not Be Working

Vercel auto-deploy requires the GitHub repository to be connected to your Vercel project. This is configured in the **Vercel Dashboard**, not in code.

## Steps to Enable Auto-Deploy

### 1. Connect GitHub Repository to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your Mind Protocol project
3. Go to **Settings** → **Git**
4. Under "Connected Git Repository":
   - If not connected: Click **Connect Git Repository**
   - Select **GitHub**
   - Authorize Vercel to access your GitHub account
   - Select repository: `mind-protocol/mindprotocol`
   - Choose branch: `main` (or your default branch)

### 2. Configure Production Branch

In **Settings** → **Git**:
- **Production Branch**: `main` (or your primary branch)
- Enable **Automatically deploy branches**

### 3. Configure Deploy Hooks (Optional)

If you want more control:
- Go to **Settings** → **Git** → **Deploy Hooks**
- Create a webhook URL
- Add this to your GitHub repository webhooks

### 4. Enable GitHub App Integration

Vercel needs the **Vercel GitHub App** installed:
1. Go to [GitHub Apps](https://github.com/settings/installations)
2. Find **Vercel**
3. Configure it to have access to `mind-protocol/mindprotocol`
4. Grant permissions for:
   - Read access to code
   - Write access to checks
   - Write access to deployments

## Verify Auto-Deploy is Working

### Test 1: Push a Commit
```bash
git commit --allow-empty -m "Test: Trigger Vercel deploy"
git push origin main
```

### Test 2: Check Vercel Dashboard
- Go to your project dashboard
- You should see a new deployment appear within ~10 seconds
- Status: Building → Ready

### Test 3: Check GitHub
- Go to your GitHub repository
- Check the **Environments** tab
- You should see deployments listed

## Current Configuration

**File: `vercel.json`**
```json
{
  "version": 2,
  "buildCommand": "npm run build",
  "framework": "nextjs"
}
```

**Build Command:** `npm run build`
**Framework:** Next.js 15.5.6
**TypeScript Checks:** Disabled (`ignoreBuildErrors: true`)
**ESLint Checks:** Disabled (`ignoreDuringBuilds: true`)

## Troubleshooting

### Issue: "Repository not found"
**Fix:** Make sure the Vercel GitHub App has access to your repository in GitHub settings.

### Issue: "Build fails but works locally"
**Fix:** Check environment variables in Vercel dashboard match your local `.env` file.

### Issue: "Deployments not triggered"
**Check:**
1. GitHub webhook is configured correctly
2. Vercel GitHub App has proper permissions
3. Branch name matches production branch setting
4. No ignored branches in Vercel settings

### Issue: "Build succeeds but site doesn't update"
**Fix:** Check if Vercel is deploying to the correct domain (production vs preview).

## Environment Variables

Make sure these are set in **Vercel Dashboard → Settings → Environment Variables**:

```
NEXT_PUBLIC_WS_URL=wss://your-backend.onrender.com/api/ws
```

(Or whatever value you need for your WebSocket backend)

## Commands

**Trigger manual deploy:**
```bash
vercel --prod
```

**Check deployment status:**
```bash
vercel ls
```

**Pull environment variables:**
```bash
vercel env pull
```

## Next Steps

1. ✅ Code configuration is ready
2. ⏳ Go to Vercel Dashboard and connect GitHub repository
3. ⏳ Test auto-deploy by pushing a commit
4. ✅ Builds will trigger automatically on every push

---

**Note:** If you don't have a Vercel account or project yet:
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Click "Add New Project"
4. Import `mind-protocol/mindprotocol` repository
5. Vercel will automatically detect Next.js and configure everything
