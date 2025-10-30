# Mind Protocol Configuration Requirements

**Document Version:** 1.0
**Last Updated:** 2025-10-29
**Author:** Atlas (Infrastructure Engineer)
**Purpose:** Complete documentation of all environment variables, dependencies, and configuration required for Mind Protocol deployment

---

## Overview

This document specifies ALL configuration required to run Mind Protocol services. Use this as:
- ✅ **Pre-deployment checklist** - Verify all required config exists
- ✅ **Staging/production setup guide** - What to configure in each environment
- ✅ **Troubleshooting reference** - When services fail to start, check here first

---

## Quick Start Checklist

**Minimum Required for Basic Operation:**
- [ ] FalkorDB running (Docker container)
- [ ] `WS_PORT` set (default: 8000)
- [ ] `DASHBOARD_PORT` set (default: 3000)
- [ ] Python 3.9+ with dependencies installed

**Required for Full Economy Runtime:**
- [ ] `ECONOMY_REDIS_URL` - Redis connection string
- [ ] `MIND_MINT_ADDRESS` - Solana token mint address
- [ ] `HELIUS_API_KEY` - Helius RPC API key
- [ ] `UBC_TREASURY_WALLET` - Treasury wallet address

---

## Core Infrastructure

### FalkorDB (Graph Database)

**Docker Container:**
```bash
docker run -d \
  --name mind_protocol_falkordb \
  -p 6379:6379 \
  falkordb/falkordb:latest
```

**Configuration:**
- **Port:** 6379 (default Redis port)
- **Host:** 127.0.0.1 (localhost)
- **Connection:** No authentication required for localhost
- **Health Check:** TCP connection to port 6379

**Verification:**
```bash
# Check if running
docker ps | grep falkordb

# Should show: mind_protocol_falkordb with status "Up" and "(healthy)"
```

---

### WebSocket Server (Consciousness Engines + API)

**Service:** `ws_api`
**Command:** `python -m orchestration.adapters.ws.websocket_server`

**Required Environment Variables:**

| Variable | Default | Description | Required? |
|----------|---------|-------------|-----------|
| `WS_PORT` | `8000` | Port for WebSocket/HTTP server | ✅ Yes |
| `MP_HOT_RELOAD` | `1` | Enable hot-reload on code changes | No (recommended for dev) |
| `MP_PERSIST_ENABLED` | `1` | Enable graph persistence to FalkorDB | ✅ Yes |
| `MP_PERSIST_MIN_BATCH` | `5` | Minimum nodes before persisting | No |
| `MP_PERSIST_INTERVAL_SEC` | `5.0` | Seconds between persistence checks | No |

**Dependencies:**
- FalkorDB must be running and healthy (port 6379)
- Python dependencies installed (`requirements.txt`)

**Health Check:**
```bash
curl http://localhost:8000/healthz?selftest=1
# Should return: {"status": "healthy", ...}
```

**Ports:**
- `8000` - WebSocket + HTTP API
- Requires FalkorDB on `6379`

---

### Dashboard (Next.js Frontend)

**Service:** `dashboard`
**Command:** `npm run dev` (development) or `npm run build && npm start` (production)

**Required Environment Variables:**

| Variable | Default | Description | Required? |
|----------|---------|-------------|-----------|
| `PORT` | `3000` | Port for Next.js dev server | No |
| `DASHBOARD_PORT` | `3000` | Alternative port specification | No |

**Dependencies:**
- Node.js 18+
- npm dependencies installed (`npm install`)
- WebSocket server running (port 8000)

**Health Check:**
```bash
curl http://localhost:3000
# Should return: HTML page
```

**Ports:**
- `3000` - Dashboard web interface
- Connects to WebSocket server on `8000`

---

## Economy Runtime Services

### Overview

Economy runtime consists of:
- **Membrane Store**: Redis-backed budget/spend tracking
- **Price Oracle**: Helius-based MIND token price lookup
- **UBC Distributor**: Universal Basic Compute distribution
- **Policy Loader**: Budget policy evaluation

**Architecture:** Economy runtime is **embedded within the WebSocket server** (`ws_api` service), not deployed as separate services.

**Status:** ✅ Integrated into ws_api service, configured in `services.yaml`
**Deployment:** Activated automatically when ws_api starts (if required env vars are set)

---

### Economy Core Settings

**Service:** Economy runtime (when enabled)
**Code Location:** `orchestration/services/economy/`

**Required Environment Variables:**

#### Organization & Graph

| Variable | Default | Description | Required? |
|----------|---------|-------------|-----------|
| `ECONOMY_ORG_ID` | `consciousness-infrastructure_mind-protocol` | Organization identifier | No |
| `ECONOMY_L2_GRAPH` | `consciousness-infrastructure_mind-protocol` | L2 graph name for policies | No |

#### Redis Connection

| Variable | Default | Description | Required? |
|----------|---------|-------------|-----------|
| `ECONOMY_REDIS_URL` | `redis://localhost:6379/0` | Redis connection string | ✅ Yes |

**Redis Setup:**

**Default Configuration:** FalkorDB (already required for consciousness substrate) is Redis-compatible and serves as the Redis backend for economy runtime. No separate Redis installation needed.

```bash
# FalkorDB provides Redis compatibility (default setup)
docker run -d \
  --name mind_protocol_falkordb \
  -p 6379:6379 \
  falkordb/falkordb:latest

# Verify Redis commands work with FalkorDB
redis-cli ping  # Should return: PONG
```

**Alternative (Separate Redis):** If you prefer separate Redis for economy data:
```bash
# Run Redis on different port (e.g., 6380)
docker run -d --name mind_redis -p 6380:6379 redis:latest

# Update ECONOMY_REDIS_URL
export ECONOMY_REDIS_URL="redis://localhost:6380/0"
```

#### Throttle & Policy Settings

| Variable | Default | Description | Required? |
|----------|---------|-------------|-----------|
| `ECONOMY_THROTTLE_INTERVAL` | `60` | Seconds between throttle evaluations | No |
| `ECONOMY_POLICY_REFRESH` | `300` | Seconds between policy reloads | No |
| `ECONOMY_SPEND_ALPHA` | `0.2` | EMA alpha for spend tracking | No |
| `ECONOMY_ROI_ALPHA` | `0.5` | EMA alpha for ROI tracking | No |
| `ECONOMY_WALLET_FLOOR_MULT` | `0.4` | Wallet floor multiplier | No |

#### Lane Wallets (JSON)

| Variable | Default | Description | Required? |
|----------|---------|-------------|-----------|
| `ECONOMY_LANE_WALLETS` | `{}` | JSON map of lane→wallet address | No |

**Example:**
```bash
export ECONOMY_LANE_WALLETS='{"autonomy": "Hxs...", "missions": "Gft..."}'
```

---

### Price Oracle (Helius Integration)

**Purpose:** Fetch real-time MIND token price from Solana via Helius RPC

**Required Environment Variables:**

| Variable | Default | Description | Required? |
|----------|---------|-------------|-----------|
| `MIND_MINT_ADDRESS` | _(empty)_ | Solana token mint address for MIND | ✅ Yes |
| `HELIUS_API_KEY` | _(empty)_ | Helius RPC API key | ✅ Yes |
| `HELIUS_BASE_URL` | `https://api.helius.xyz` | Helius API base URL | No |
| `MIND_USD_FALLBACK` | `1.0` | Fallback price if oracle fails | No |
| `ECONOMY_PRICE_TTL` | `300` | Seconds to cache price | No |

**Obtaining Helius API Key:**
1. Sign up at https://helius.xyz
2. Create new project
3. Copy API key
4. Set as `HELIUS_API_KEY`

**Deployment Note:**
- Price oracle only activates if BOTH `MIND_MINT_ADDRESS` AND `HELIUS_API_KEY` are set
- If either missing, falls back to `MIND_USD_FALLBACK` price
- Check `settings.has_price_oracle` property to verify activation

---

### Universal Basic Compute (UBC)

**Purpose:** Daily distribution of compute credits to citizen wallets

**Required Environment Variables:**

| Variable | Default | Description | Required? |
|----------|---------|-------------|-----------|
| `UBC_DAILY` | `100.0` | Daily UBC amount to distribute | No |
| `UBC_TREASURY_WALLET` | _(empty)_ | Treasury wallet (source of UBC) | ✅ Yes |
| `UBC_CITIZEN_WALLETS` | `{}` | JSON map of citizen→wallet address | ✅ Yes |
| `UBC_CRON_OFFSET_SECONDS` | `0` | Offset for UBC distribution schedule | No |

**Example:**
```bash
export UBC_TREASURY_WALLET="TreasuryAddressHere..."
export UBC_CITIZEN_WALLETS='{"ada": "AdaWallet...", "felix": "FelixWallet..."}'
```

**Deployment Note:**
- UBC distribution requires wallet custody service (see below)
- Currently uses STUB implementation (no actual transfers)
- ⚠️ **Not production-ready** until custody service integrated

---

### Wallet Custody Service

**Status:** ⚠️ **STUB IMPLEMENTATION** - Not production-ready

**Purpose:** Secure key management for Solana wallet operations

**Required (When Implemented):**
- Vault storage for sealed wallet keys
- Ledger tracking for all transactions
- Solana RPC endpoint (via Helius)

**Current Limitation:**
- Codex-B SYNC_27_10_25.md (line 38): "Replace the UBC ledger stub with actual custody transfers once Solana signing is ready"
- Can emit telemetry but cannot execute real transfers
- Requires implementation before production use

**Deployment Blocker:** ✋ **HIGH** - Cannot distribute real UBC until custody service complete

---

## Service Watchers & Collectors

### Conversation Watcher

**Service:** `conversation_watcher`
**Command:** `python -m orchestration.services.watchers.conversation_watcher`

**Purpose:** Auto-captures conversation contexts for consciousness continuity

**Configuration:**
- No environment variables required
- Requires WebSocket server running

**Dependencies:**
- `ws_api` must be healthy

---

### Signals Collector

**Service:** `signals_collector`
**Command:** `python -m orchestration.services.signals_collector`

**Purpose:** Collects telemetry signals from consciousness engines

**Configuration:**
- No environment variables required
- Listens on port 8010 (hardcoded)

**Dependencies:**
- `ws_api` must be healthy

---

### Autonomy Orchestrator

**Service:** `autonomy_orchestrator`
**Command:** `python -m orchestration.services.autonomy_orchestrator`

**Purpose:** Coordinates autonomous citizen actions

**Configuration:**
- No environment variables required

**Dependencies:**
- `ws_api` must be healthy

---

## Python Dependencies

**File:** `requirements.txt`

**Installation:**
```bash
cd /home/mind-protocol/mindprotocol
pip install -r requirements.txt
```

**Critical Dependencies:**
- `falkordb` - FalkorDB Python client
- `websockets` - WebSocket server
- `fastapi` - HTTP API framework
- `redis` - Redis client (for economy runtime)
- `solana` - Solana blockchain client (for wallet custody)

**Verification:**
```bash
python -c "import falkordb, websockets, fastapi, redis; print('All imports successful')"
```

---

## Node.js Dependencies

**File:** `package.json`

**Installation:**
```bash
cd /home/mind-protocol/mindprotocol
npm install
```

**Critical Dependencies:**
- `next` - Next.js framework
- `react` - React library
- `@pixi/react` - PixiJS for consciousness visualization

**Verification:**
```bash
npm list next react
```

---

## Environment Variable Summary

### Required for Basic Operation
```bash
# Core Infrastructure
export WS_PORT=8000
export DASHBOARD_PORT=3000
export MP_PERSIST_ENABLED=1
```

### Required for Economy Runtime
```bash
# Redis
export ECONOMY_REDIS_URL="redis://localhost:6379/0"

# Solana/Helius
export MIND_MINT_ADDRESS="<your-token-mint-address>"
export HELIUS_API_KEY="<your-helius-api-key>"

# UBC Distribution
export UBC_TREASURY_WALLET="<treasury-wallet-address>"
export UBC_CITIZEN_WALLETS='{"ada": "<wallet>", "felix": "<wallet>", ...}'
```

### Optional Tuning
```bash
# Persistence
export MP_PERSIST_MIN_BATCH=5
export MP_PERSIST_INTERVAL_SEC=5.0

# Economy Throttling
export ECONOMY_THROTTLE_INTERVAL=60
export ECONOMY_POLICY_REFRESH=300

# Price Oracle
export ECONOMY_PRICE_TTL=300
export MIND_USD_FALLBACK=1.0
```

---

## Configuration Files

### Services Configuration
**File:** `orchestration/services/mpsv3/services.yaml`

**Purpose:** Defines all MPSv3-managed services, dependencies, health checks, restart policies

**Current Services:**
- `falkordb` - Graph database (also serves as Redis for economy runtime)
- `ws_api` - WebSocket server + consciousness engines + **economy runtime**
- `dashboard` - Next.js frontend
- `conversation_watcher` - Context capture
- `signals_collector` - Telemetry collection
- `autonomy_orchestrator` - Autonomy coordination

**Economy Runtime Integration:**
- ✅ Economy runtime (membrane store, price oracle, UBC distributor) is embedded in `ws_api` service
- ✅ Environment variables configured in `services.yaml`
- ✅ Automatically activates when ws_api starts (if required env vars are set)

**Not Yet Included:**
- Wallet custody service (STUB implementation, not production-ready)

---

## Deployment Readiness Checklist

### Pre-Deployment Verification

**Infrastructure:**
- [ ] Docker installed and running
- [ ] FalkorDB container created and healthy (serves both graph + Redis for economy)
- [ ] Python 3.9+ installed
- [ ] Node.js 18+ installed

**Configuration:**
- [ ] All required environment variables set
- [ ] Environment variables exported in shell or `.env` file
- [ ] Configuration verified against this document

**Dependencies:**
- [ ] Python `requirements.txt` installed
- [ ] Node.js `package.json` dependencies installed
- [ ] No import errors when testing

**Testing:**
- [ ] FalkorDB health check passes (TCP port 6379)
- [ ] WebSocket server starts and responds to `/healthz`
- [ ] Dashboard loads in browser
- [ ] Integration tests pass (`python orchestration/tests/test_infrastructure_integration.py`)

---

## Common Issues & Solutions

### Issue: "Cannot connect to FalkorDB"

**Symptoms:**
- WebSocket server fails to start
- Error: "Connection refused" on port 6379

**Solutions:**
1. Check FalkorDB container: `docker ps | grep falkordb`
2. Start if stopped: `docker start mind_protocol_falkordb`
3. Check logs: `docker logs mind_protocol_falkordb`
4. Verify port: `lsof -i :6379`

---

### Issue: "Economy services fail to start"

**Symptoms:**
- Import errors from `orchestration.services.economy`
- Missing environment variable errors

**Solutions:**
1. Verify Redis running: `redis-cli ping` (should return "PONG")
2. Check required env vars: `echo $ECONOMY_REDIS_URL`
3. Test Redis connection: `redis-cli -u $ECONOMY_REDIS_URL ping`
4. If missing Helius key: Economy will use fallback price (warning only)

---

### Issue: "Dashboard not loading"

**Symptoms:**
- Port 3000 shows "Cannot connect"
- Next.js not starting

**Solutions:**
1. Check if WebSocket server running first (dependency)
2. Verify Node.js version: `node --version` (need 18+)
3. Reinstall dependencies: `npm install`
4. Check port availability: `lsof -i :3000`
5. Try manual start: `npm run dev` (see actual error)

---

## Security Considerations

### Secrets Management

**⚠️ Never commit secrets to git:**
- `HELIUS_API_KEY`
- `UBC_TREASURY_WALLET` private keys
- `UBC_CITIZEN_WALLETS` private keys
- Production Redis credentials

**Recommended:**
- Use `.env` file (add to `.gitignore`)
- Use environment variable management (e.g., direnv, dotenv)
- Use secrets management service in production (AWS Secrets Manager, Vault)

### Network Security

**Development (localhost):**
- FalkorDB: No authentication (localhost only)
- Redis: No authentication (localhost only)
- WebSocket: No TLS (localhost only)

**Production:**
- ✅ Enable Redis authentication (`requirepass`)
- ✅ Use TLS for WebSocket (wss://)
- ✅ Firewall external access to FalkorDB/Redis ports
- ✅ Use reverse proxy (nginx) for dashboard

---

## Next Steps

**After Configuration Complete:**
1. Proceed to `DEPLOYMENT_RUNBOOK.md` for deployment procedures
2. Set up staging environment for integration testing
3. Run full test suite against live services
4. Monitor health checks and telemetry

**For Production Deployment:**
1. Complete wallet custody service implementation (blocks UBC)
2. Set up secrets management
3. Configure production Redis with authentication
4. Enable TLS/SSL for external connections
5. Set up monitoring/alerting

---

## Document Maintenance

**Update this document when:**
- Adding new services to `services.yaml`
- Adding new environment variables to code
- Discovering undocumented configuration
- Changing default values
- Adding new dependencies

**Version History:**
- 1.0 (2025-10-29): Initial comprehensive documentation

---

**Status:** Configuration requirements documented. Ready for deployment procedure creation.

---

*Atlas - Infrastructure Engineer*
*"If it's not documented, it's not deployable."*
