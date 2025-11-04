# Mind Protocol - Production Deployment Guide

**Last Updated:** 2025-11-04
**Status:** ⚠️ DEPLOYMENT READY WITH KNOWN ISSUES (see below) 

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Production Architecture                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Frontend (Vercel)                                           │
│  ├─ Next.js 15 Dashboard                                     │
│  ├─ React 18 Components                                      │
│  ├─ D3.js Graph Visualization                                │
│  └─ WebSocket Client                                         │
│                                                               │
│  Backend (Render)                                            │
│  ├─ WebSocket API Server (FastAPI + Uvicorn)                │
│  ├─ Consciousness Engines (Python)                           │
│  ├─ MPSv3 Supervisor (Service Orchestration)                │
│  └─ Services: conversation_watcher, signals_collector, etc.  │
│                                                               │
│  Database (Render Redis)                                     │
│  └─ FalkorDB (Redis module for graph storage)               │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚨 KNOWN ISSUES (Must Fix Before Production)

**Critical blockers identified during infrastructure testing (2025-11-04):**

### 1. WebSocket Server Crash on Startup
- **Symptom:** Server starts, loads graphs, crashes within 2 seconds
- **Root Cause:** SafeMode tripwire kills server due to observability/telemetry emission failures
- **Location:** `orchestration/services/health/safe_mode.py`
- **Impact:** API endpoints timeout, no real-time data to dashboard
- **Status:** ❌ BLOCKING - Backend non-functional

### 2. SubEntity Loading Failure
- **Symptom:** Engines log "graph.subentities is EMPTY!" despite 2,168 SubEntity nodes in DB
- **Root Cause:** Label case mismatch in query (`SubEntity` vs `Subentity`)
- **Location:** `orchestration/libs/utils/falkordb_adapter.py`
- **Impact:** Consciousness layer runs with empty state, no data to visualize
- **Status:** ❌ BLOCKING - Core functionality broken

### 3. WebSocket Connection Bug
- **Symptom:** "WebSocket is not connected. Need to call 'accept' first" (~5M errors/5sec)
- **Root Cause:** Connection handling flow error
- **Location:** `orchestration/adapters/api/control_api.py:2808`
- **Impact:** HTTP API timeouts, dashboard can't connect
- **Status:** ⚠️ KNOWN ISSUE - Liveness checks disabled as workaround

**Recommendation:** Fix these issues before deploying to production. See `consciousness/citizens/SYNC.md` for detailed diagnostics.

---

## Prerequisites

- **Render Account:** https://render.com (free tier available)
- **Vercel Account:** https://vercel.com (free tier available)
- **GitHub Repository:** Code pushed to GitHub
- **Domain (Optional):** Custom domain for production

---

## Step 1: Deploy Backend to Render

### 1.1 Create Render Account & Connect GitHub

1. Sign up at https://render.com
2. Connect your GitHub account
3. Grant Render access to your Mind Protocol repository

### 1.2 Deploy FalkorDB (Redis Service)

1. From Render Dashboard, click **"New +"** → **"Redis"**
2. Configure:
   - **Name:** `mind-protocol-falkordb`
   - **Plan:** Starter (upgrade to Standard for production - 1GB RAM minimum)
   - **Region:** Choose closest to your users
   - **Max Memory Policy:** `noeviction` (REQUIRED for graph persistence)
3. Click **"Create Redis"**
4. Wait for deployment (1-2 minutes)
5. **Save the Internal Redis URL** (format: `redis://user:pass@host:port`)

### 1.3 Deploy Backend Web Service

1. From Render Dashboard, click **"New +"** → **"Blueprint"**
2. Select your Mind Protocol repository
3. Render will auto-detect `render.yaml` and show services:
   - `mind-protocol-falkordb` (Redis)
   - `mind-protocol-backend` (Web Service)
4. Click **"Apply"** to deploy both services
5. **Configure Environment Variables** (in Render Dashboard):
   - Most are auto-set from `render.yaml`
   - **Required:** `ECONOMY_REDIS_URL` (should auto-populate from Redis service)
   - **Optional:** Set Solana/Helius keys if using token economy features

### 1.4 Verify Backend Deployment

```bash
# Check health endpoint (replace with your Render URL)
curl https://mind-protocol-backend.onrender.com/healthz

# Expected: {"status": "ok", ...}
```

**Note:** First deployment takes 5-10 minutes (installing dependencies + downloading models)

---

## Step 2: Deploy Frontend to Vercel

### 2.1 Create Vercel Account & Import Project

1. Sign up at https://vercel.com
2. Click **"Add New..."** → **"Project"**
3. Import your Mind Protocol repository from GitHub
4. Vercel auto-detects Next.js configuration

### 2.2 Configure Environment Variables

In Vercel project settings → **"Environment Variables"**:

**Required:**
- **Variable:** `NEXT_PUBLIC_WS_URL`
- **Value:** `https://mind-protocol-backend.onrender.com` (your Render backend URL)
- **Environments:** Production, Preview, Development

### 2.3 Deploy

1. Click **"Deploy"**
2. Wait 2-3 minutes for build
3. Vercel provides deployment URL: `https://your-app.vercel.app`

### 2.4 Verify Frontend Deployment

1. Visit `https://your-app.vercel.app`
2. Navigate to `/consciousness` page
3. Check browser console for WebSocket connection

**Expected:** Dashboard loads, attempts WebSocket connection to backend

---

## Step 3: Configure CORS (Backend)

Backend needs to allow requests from Vercel frontend.

### 3.1 Add CORS Environment Variable to Render

In Render Dashboard → Backend Service → Environment:

- **Variable:** `ALLOWED_ORIGINS`
- **Value:** `https://your-app.vercel.app,https://your-custom-domain.com`

### 3.2 Update Backend Code (if needed)

Check `orchestration/adapters/ws/websocket_server.py` for CORS configuration:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Step 4: Custom Domain (Optional)

### 4.1 Add Domain to Vercel

1. Vercel Dashboard → Project → Settings → Domains
2. Add your custom domain
3. Configure DNS records as instructed by Vercel

### 4.2 Add Domain to Render (if using API subdomain)

1. Render Dashboard → Backend Service → Settings → Custom Domain
2. Add `api.your-domain.com`
3. Configure DNS CNAME record
4. Update Vercel's `NEXT_PUBLIC_WS_URL` to `https://api.your-domain.com`

---

## Step 5: Post-Deployment Verification

### 5.1 Backend Health Check

```bash
# Health endpoint
curl https://your-backend.onrender.com/healthz

# Consciousness status (if working)
curl https://your-backend.onrender.com/api/consciousness/status
```

### 5.2 Frontend Functionality

1. Visit dashboard: `https://your-app.vercel.app/consciousness`
2. Check browser DevTools → Console for errors
3. Verify WebSocket connection established
4. Confirm graph visualization loads

### 5.3 Database Verification

```bash
# SSH into Render backend (if available) or use Redis CLI
redis-cli -h <your-redis-host> -p 6379 -a <password>

# Check graph existence
GRAPH.LIST

# Query node count for a citizen
GRAPH.QUERY "mind-protocol_victor" "MATCH (n) RETURN count(n)"
```

---

## Monitoring & Maintenance

### Render Monitoring

- **Logs:** Render Dashboard → Service → Logs (real-time)
- **Metrics:** CPU, Memory, Network usage in dashboard
- **Alerts:** Configure in Settings → Notifications

### Vercel Monitoring

- **Deployment Logs:** Vercel Dashboard → Deployments → [Latest] → Logs
- **Analytics:** Vercel Dashboard → Analytics (on Pro plan)
- **Function Logs:** Vercel Dashboard → Functions

### Health Checks

Set up external monitoring (e.g., UptimeRobot, Pingdom):
- Monitor: `https://your-backend.onrender.com/healthz`
- Frequency: Every 5 minutes
- Alert on: HTTP 500, timeout > 10s

---

## Scaling Considerations

### Backend (Render)

**Starter Plan Limits:**
- 512 MB RAM
- 0.5 CPU
- Good for: Development, low traffic

**Standard Plan Recommended:**
- 1 GB RAM minimum (for sentence-transformers embeddings)
- 1 CPU
- Good for: Production, moderate traffic

**Upgrade Path:**
1. Render Dashboard → Backend Service → Settings
2. Change Instance Type to "Standard"
3. Redeploy

### Frontend (Vercel)

**Free Tier:**
- 100 GB bandwidth/month
- Unlimited deployments
- Good for: Most use cases

**Pro Plan ($20/month):**
- 1 TB bandwidth
- Advanced analytics
- Required for: High traffic, team collaboration

### Database (FalkorDB/Redis)

**Starter Plan:**
- 256 MB RAM
- Good for: Development, testing

**Standard Plan Recommended:**
- 1 GB RAM minimum
- Automatic backups
- Good for: Production (thousands of nodes)

---

## Troubleshooting

### Backend Won't Start

**Check Render Logs:**
```
Render Dashboard → Backend Service → Logs
```

**Common Issues:**
- Missing environment variable (check `ECONOMY_REDIS_URL`)
- Redis connection failed (verify FalkorDB running)
- Port already in use (Render manages this automatically)
- Dependency installation failed (check requirements.txt)

### Frontend Can't Connect to Backend

**Check Browser Console:**
```
DevTools → Console → Look for WebSocket errors
```

**Common Issues:**
- CORS blocked (add Vercel domain to `ALLOWED_ORIGINS`)
- Wrong `NEXT_PUBLIC_WS_URL` (verify Render backend URL)
- Backend down (check Render service status)
- Firewall blocking WebSocket (test with curl)

### Database Connection Issues

**Verify Redis URL:**
```bash
# Test connection
redis-cli -u $ECONOMY_REDIS_URL ping
# Expected: PONG
```

**Common Issues:**
- Wrong credentials in `ECONOMY_REDIS_URL`
- Redis service not running (check Render dashboard)
- Network timeout (check Render region/latency)

### Known Issue: WebSocket Crashes

**Symptom:** Backend logs show SafeMode tripwire killing server

**Workaround (Temporary):**
1. Disable SafeMode in `orchestration/services/health/safe_mode.py`
2. Or increase tripwire threshold
3. Monitor logs for root cause

**Proper Fix:** See SYNC.md for detailed diagnostics (code fix required)

---

## Rollback Procedure

### Frontend (Vercel)

1. Vercel Dashboard → Deployments
2. Find last working deployment
3. Click **"..."** → **"Promote to Production"**

### Backend (Render)

1. Render Dashboard → Backend Service → Deploys
2. Find last working deploy
3. Click **"Redeploy"**

### Database (Redis)

**If data corrupted:**
1. Render Dashboard → FalkorDB Redis → Backups
2. Select restore point
3. Click **"Restore"**

**Note:** Only available on Standard plan or higher

---

## Security Checklist

- [ ] All environment variables set (no defaults in production)
- [ ] `MP_HOT_RELOAD=0` in production
- [ ] CORS configured (not using wildcard `*`)
- [ ] Redis password set (auto-generated by Render)
- [ ] No API keys committed to git
- [ ] HTTPS enforced (automatic on Render/Vercel)
- [ ] Rate limiting configured (if high traffic expected)
- [ ] Monitoring alerts set up

---

## Cost Estimate

**Free Tier (Development):**
- Render: Free (512 MB web service + 256 MB Redis)
- Vercel: Free (100 GB bandwidth)
- **Total:** $0/month

**Production (Recommended):**
- Render Backend: $7/month (Standard 1GB)
- Render FalkorDB: $7/month (Standard 1GB Redis)
- Vercel: Free or $20/month (Pro)
- **Total:** $14-34/month

**High Traffic (Scale):**
- Render Backend: $25/month (Pro 2GB)
- Render FalkorDB: $15/month (Pro 2GB Redis)
- Vercel Pro: $20/month
- **Total:** $60/month

---

## Support & Documentation

**Render Docs:** https://render.com/docs
**Vercel Docs:** https://vercel.com/docs
**FalkorDB Docs:** https://docs.falkordb.com
**Mind Protocol Issues:** See `consciousness/citizens/SYNC.md`

---

## Deployment Checklist

**Before Deploying:**
- [ ] Fix critical bugs (WebSocket crash, SubEntity loading)
- [ ] Test locally with production config
- [ ] Review `SYNC.md` for known issues
- [ ] Backup current database (if migrating)

**During Deployment:**
- [ ] Push code to GitHub
- [ ] Deploy Render backend via Blueprint
- [ ] Deploy Vercel frontend
- [ ] Configure environment variables
- [ ] Set up CORS

**After Deployment:**
- [ ] Verify health endpoints
- [ ] Test WebSocket connection
- [ ] Check graph visualization
- [ ] Set up monitoring
- [ ] Configure alerts

**⚠️ REMINDER:** Current system has blocking bugs. Fix before production deployment.

---

**Deployment Prepared By:** Victor "The Resurrector"
**Date:** 2025-11-04
**Status:** Ready for deployment AFTER critical bug fixes
