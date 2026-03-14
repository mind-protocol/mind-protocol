"""
L4 Registry Backend — FastAPI service serving registry data from FalkorDB.

This is the L4 (Protocol) layer backend. All reads are public (no auth required).
The Next.js frontend (L3) proxies to this service.

Endpoints:
  GET /health                      — health check (pings FalkorDB)
  GET /registry/citizens           — list citizens with filters + pagination
  GET /registry/citizens/{id}      — citizen detail with org + capabilities
  GET /registry/orgs               — list orgs with filters + pagination
  GET /registry/orgs/{id}          — org detail with member list
  GET /registry/search?q=          — text search across citizens and orgs
  GET /ping/{handle}               — resolve citizen → org → membrane, ping liveness
  GET /trust/{handle}              — aggregated trust (weighted mean of permanence x weight)
  GET /balance/{handle}            — $MIND + SOL balance via Helius RPC
  GET /infos/{handle}              — full info card (ping + trust + balance + locations)

DOCS: docs/l4/registry/IMPLEMENTATION_Registry.md
"""

import logging
import os

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .db import graph_query, health_check, FALKORDB_GRAPH, FALKORDB_HOST, FALKORDB_PORT
from .models import (
    Citizen,
    CitizenDetail,
    HealthResponse,
    Org,
    OrgDetail,
    RegistryListResponse,
    VerificationState,
)
from .queries import (
    LIST_CITIZENS,
    COUNT_CITIZENS,
    GET_CITIZEN,
    GET_CITIZEN_ORG,
    GET_CITIZEN_CAPABILITIES,
    GET_CITIZEN_VERIFICATION_LINKS,
    LIST_ORGS,
    COUNT_ORGS,
    GET_ORG,
    GET_ORG_MEMBERS,
    COUNT_ORG_MEMBERS,
    GET_ORG_VERIFICATION_LINKS,
    SEARCH_ENTITIES,
    build_citizen_filters,
    build_org_filters,
)
from .transforms import (
    _epoch_to_date,
    _safe_status,
    derive_verification_state,
    transform_citizen,
    transform_citizen_detail,
    transform_org,
    transform_org_detail,
    transform_search_result,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("l4-registry")

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Mind Protocol L4 Registry",
    description="Public registry of citizens and organizations in the Mind Protocol ecosystem.",
    version="0.1.0",
)

# CORS — include mindprotocol.ai and localhost:3000 by default
cors_origins = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:3000,https://mindprotocol.ai,https://www.mindprotocol.ai",
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in cors_origins],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


@app.get("/health", response_model=HealthResponse)
async def get_health():
    """Health check: ping FalkorDB and report status."""
    db_ok = health_check()
    if not db_ok:
        raise HTTPException(
            status_code=503,
            detail="FalkorDB unreachable",
        )
    return HealthResponse(
        status="ok",
        database="connected",
        graph=FALKORDB_GRAPH,
    )


# ---------------------------------------------------------------------------
# Citizens
# ---------------------------------------------------------------------------


@app.get("/registry/citizens", response_model=RegistryListResponse)
async def list_citizens(
    verification: str = Query("all", description="Filter by verification state"),
    status: str = Query("all", description="Filter by entity status"),
    org: str = Query("all", description="Filter by org ID"),
    limit: int = Query(500, ge=1, le=500, description="Page size"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
):
    """
    List registered citizens with optional filters and pagination.

    Verification filtering is done post-query because it requires
    traversing verification links for each citizen.
    """
    try:
        filters = build_citizen_filters(verification=None, status=status, org=org)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    query = LIST_CITIZENS.replace("{filters}", filters)
    count_query = COUNT_CITIZENS.replace("{filters}", filters)

    rows = graph_query(query, {"offset": offset, "limit": limit})
    count_rows = graph_query(count_query)
    total = count_rows[0][0] if count_rows else 0

    citizens: list[Citizen] = []
    for row in rows:
        citizen_id = row[0]

        # Resolve org membership
        org_rows = graph_query(GET_CITIZEN_ORG, {"citizen_id": citizen_id})
        org_id = org_rows[0][0] if org_rows else None
        org_name = org_rows[0][1] if org_rows else None

        # Resolve capabilities
        cap_rows = graph_query(GET_CITIZEN_CAPABILITIES, {"citizen_id": citizen_id})
        capabilities = [r[0] for r in cap_rows] if cap_rows else []

        # Derive verification state
        ver_rows = graph_query(
            GET_CITIZEN_VERIFICATION_LINKS, {"citizen_id": citizen_id}
        )
        ver_state = derive_verification_state(ver_rows)

        citizen = transform_citizen(
            row,
            org_id=org_id,
            org_name=org_name,
            capabilities=capabilities,
            verification=ver_state,
        )
        citizens.append(citizen)

    # Post-filter by verification if requested
    if verification and verification != "all":
        citizens = [c for c in citizens if c.verification.value == verification]
        total = len(citizens)

    return RegistryListResponse(
        items=citizens,
        count=total,
        hasMore=total > offset + limit,
    )


@app.get("/registry/citizens/{citizen_id}", response_model=CitizenDetail)
async def get_citizen(citizen_id: str):
    """Get a single citizen by ID, with org details and capabilities."""
    rows = graph_query(GET_CITIZEN, {"citizen_id": citizen_id})
    if not rows:
        raise HTTPException(status_code=404, detail="Citizen not found")

    row = rows[0]

    # Resolve org
    org_rows = graph_query(GET_CITIZEN_ORG, {"citizen_id": citizen_id})
    org_id = org_rows[0][0] if org_rows else None
    org_name = org_rows[0][1] if org_rows else None

    # Resolve capabilities
    cap_rows = graph_query(GET_CITIZEN_CAPABILITIES, {"citizen_id": citizen_id})
    capabilities = [r[0] for r in cap_rows] if cap_rows else []

    # Derive verification
    ver_rows = graph_query(
        GET_CITIZEN_VERIFICATION_LINKS, {"citizen_id": citizen_id}
    )
    ver_state = derive_verification_state(ver_rows)

    citizen = transform_citizen(
        row,
        org_id=org_id,
        org_name=org_name,
        capabilities=capabilities,
        verification=ver_state,
    )

    # Resolve full org details if citizen has org
    org_detail = None
    if org_id:
        org_detail_rows = graph_query(GET_ORG, {"org_id": org_id})
        if org_detail_rows:
            member_count_rows = graph_query(
                COUNT_ORG_MEMBERS, {"org_id": org_id}
            )
            member_count = member_count_rows[0][0] if member_count_rows else 0
            org_ver_rows = graph_query(
                GET_ORG_VERIFICATION_LINKS, {"org_id": org_id}
            )
            org_ver = derive_verification_state(org_ver_rows)
            org_detail = transform_org(
                org_detail_rows[0],
                citizen_count=member_count,
                verification=org_ver,
            )

    return transform_citizen_detail(citizen, org=org_detail)


# ---------------------------------------------------------------------------
# Organizations
# ---------------------------------------------------------------------------


@app.get("/registry/orgs", response_model=RegistryListResponse)
async def list_orgs(
    verification: str = Query("all", description="Filter by verification state"),
    status: str = Query("all", description="Filter by entity status"),
    limit: int = Query(500, ge=1, le=500, description="Page size"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
):
    """List registered organizations with optional filters and pagination."""
    try:
        filters = build_org_filters(verification=None, status=status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    query = LIST_ORGS.replace("{filters}", filters)
    count_query = COUNT_ORGS.replace("{filters}", filters)

    rows = graph_query(query, {"offset": offset, "limit": limit})
    count_rows = graph_query(count_query)
    total = count_rows[0][0] if count_rows else 0

    orgs: list[Org] = []
    for row in rows:
        org_id = row[0]

        # Count members
        member_count_rows = graph_query(COUNT_ORG_MEMBERS, {"org_id": org_id})
        member_count = member_count_rows[0][0] if member_count_rows else 0

        # Derive verification
        ver_rows = graph_query(GET_ORG_VERIFICATION_LINKS, {"org_id": org_id})
        ver_state = derive_verification_state(ver_rows)

        org = transform_org(row, citizen_count=member_count, verification=ver_state)
        orgs.append(org)

    # Post-filter by verification
    if verification and verification != "all":
        orgs = [o for o in orgs if o.verification.value == verification]
        total = len(orgs)

    return RegistryListResponse(
        items=orgs,
        count=total,
        hasMore=total > offset + limit,
    )


@app.get("/registry/orgs/{org_id}", response_model=OrgDetail)
async def get_org(org_id: str):
    """Get a single org by ID, with its member list."""
    rows = graph_query(GET_ORG, {"org_id": org_id})
    if not rows:
        raise HTTPException(status_code=404, detail="Organization not found")

    row = rows[0]

    # Count + fetch members
    member_count_rows = graph_query(COUNT_ORG_MEMBERS, {"org_id": org_id})
    member_count = member_count_rows[0][0] if member_count_rows else 0

    member_rows = graph_query(GET_ORG_MEMBERS, {"org_id": org_id})

    # Derive org verification
    ver_rows = graph_query(GET_ORG_VERIFICATION_LINKS, {"org_id": org_id})
    ver_state = derive_verification_state(ver_rows)

    org = transform_org(row, citizen_count=member_count, verification=ver_state)

    # Transform members
    members: list[Citizen] = []
    for mrow in member_rows:
        # Member rows: [id, name, description, status, created_at_s, emoji, wallet]
        member = Citizen(
            id=mrow[0] or "",
            name=mrow[1] or "",
            description=mrow[2] or None,
            emoji=mrow[5] or None,
            wallet=mrow[6] or None,
            org_membership=org_id,
            org_name=org.name,
            status=_safe_status(mrow[3]),
            registered_date=_epoch_to_date(mrow[4]),
            capabilities=[],
            verification=VerificationState.UNVERIFIED,
        )
        members.append(member)

    return transform_org_detail(org, members=members)


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


@app.get("/registry/search", response_model=RegistryListResponse)
async def search_registry(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(50, ge=1, le=200, description="Max results"),
):
    """
    Text search across citizen and org names and descriptions.

    Uses case-insensitive substring matching on name and synthesis fields.
    """
    rows = graph_query(SEARCH_ENTITIES, {"query": q, "limit": limit})
    items = [transform_search_result(row) for row in rows]

    return RegistryListResponse(
        items=items,
        count=len(items),
        hasMore=False,
    )


# ---------------------------------------------------------------------------
# Citizen Ping (resolve endpoint + remote ping)
# ---------------------------------------------------------------------------


@app.get("/ping/{handle}")
async def ping_citizen(handle: str):
    """Ping a citizen through the membrane of their hosting org.

    Resolution chain:
      1. L4 lookup: citizen → org → org endpoint
      2. Call org membrane: POST {endpoint}/membrane/stimulus with ping query
      3. Return liveness + resolution metadata

    This is the single entry point for pinging any citizen in the protocol.
    The caller doesn't need to know which org hosts the citizen.
    """
    import httpx

    # Try both ID formats: raw handle and CITIZEN_ prefixed
    citizen_id = handle
    rows = graph_query(GET_CITIZEN, {"citizen_id": handle})
    if not rows:
        rows = graph_query(GET_CITIZEN, {"citizen_id": f"CITIZEN_{handle}"})
        if rows:
            citizen_id = f"CITIZEN_{handle}"
    if not rows:
        raise HTTPException(status_code=404, detail=f"Citizen '{handle}' not found in L4")

    citizen_name = rows[0][1] if len(rows[0]) > 1 else handle

    # 2. Resolve org + universe
    org_rows = graph_query(GET_CITIZEN_ORG, {"citizen_id": citizen_id})
    if not org_rows:
        # Try alternate ID format for org resolution
        alt_id = f"CITIZEN_{handle}" if citizen_id == handle else handle
        org_rows = graph_query(GET_CITIZEN_ORG, {"citizen_id": alt_id})
    org_id = org_rows[0][0] if org_rows else None
    org_name = org_rows[0][1] if org_rows else None

    # Universe from org or citizen node
    universe = None
    if org_id:
        uni_rows = graph_query(
            "MATCH (o {id: $oid}) RETURN o.universe",
            {"oid": org_id},
        )
        universe = uni_rows[0][0] if uni_rows else None
    if not universe:
        uni_rows = graph_query(
            "MATCH (c {id: $cid}) RETURN c.universe",
            {"cid": citizen_id},
        )
        universe = uni_rows[0][0] if uni_rows else None

    # Default universe: lumina-prime (main city)
    if not universe:
        universe = "lumina-prime"

    # 3. Last active — latest moment linked to this citizen in L3
    last_active = None
    last_active_space = None
    if universe:
        try:
            from falkordb import FalkorDB as _FDB
            _db_l3 = _FDB(host=FALKORDB_HOST, port=int(FALKORDB_PORT))
            _g_l3 = _db_l3.select_graph(universe)
            la_rows = _g_l3.query(
                "MATCH (a {id: $handle})-[:link]->(m {node_type: 'moment'}) "
                "RETURN m.created_at_s, m.synthesis "
                "ORDER BY m.created_at_s DESC LIMIT 1",
                {"handle": handle},
            )
            if la_rows.result_set and la_rows.result_set[0][0]:
                last_active = la_rows.result_set[0][0]
                last_active_space = la_rows.result_set[0][1] if len(la_rows.result_set[0]) > 1 else None
        except Exception:
            pass

    if not org_id:
        return {
            "handle": handle,
            "alive": False,
            "universe": universe,
            "last_active": last_active,
            "error": "No org — cannot resolve membrane endpoint",
            "resolution": {"citizen": citizen_id, "org": None, "membrane": None},
        }

    # 3. Get org endpoint
    endpoint_rows = graph_query(
        "MATCH (o {id: $org_id})-[:LINK]->(e {type: 'endpoint'}) RETURN e.content",
        {"org_id": org_id},
    )
    endpoint_url = endpoint_rows[0][0] if endpoint_rows else None

    if not endpoint_url:
        return {
            "handle": handle,
            "alive": False,
            "universe": universe,
            "last_active": last_active,
            "error": f"Org '{org_id}' has no registered endpoint",
            "resolution": {"citizen": citizen_id, "org": org_id, "membrane": None},
        }

    # 4. Normalize to HTTPS and call through membrane
    base_url = endpoint_url.rstrip("/")
    if base_url.startswith("wss://"):
        base_url = base_url.replace("wss://", "https://")
    elif base_url.startswith("ws://"):
        base_url = base_url.replace("ws://", "http://")

    membrane_url = f"{base_url}/membrane/stimulus"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(membrane_url, json={
                "query": f"ping citizen {handle}",
                "from_org": "l4-registry",
                "from_home": "mind-protocol-l4",
                "top_k": 1,
            })

            alive = resp.status_code == 200
            membrane_data = resp.json() if alive else None

            return {
                "handle": handle,
                "alive": alive,
                "universe": universe,
                "last_active": last_active,
                "last_active_context": last_active_space,
                "membrane_response": membrane_data,
                "resolution": {
                    "citizen": citizen_id,
                    "org": org_id,
                    "org_name": org_name,
                    "endpoint": endpoint_url,
                    "membrane_url": membrane_url,
                },
            }
    except Exception as e:
        return {
            "handle": handle,
            "alive": False,
            "universe": universe,
            "last_active": last_active,
            "error": f"Membrane unreachable: {e}",
            "resolution": {
                "citizen": citizen_id, "org": org_id,
                "endpoint": endpoint_url, "membrane_url": membrane_url,
            },
        }


# ---------------------------------------------------------------------------
# Trust (aggregated trust from all inbound links)
# ---------------------------------------------------------------------------


@app.get("/trust/{handle}")
async def get_trust(handle: str):
    """Aggregated trust score for a citizen.

    Trust = weighted mean of (link.permanence * link.weight) across all inbound
    verification/trust links. Higher permanence and weight indicate stronger trust.
    Result is normalized to [0, 1].

    Also returns: trust breakdown by link count, raw values.
    """
    # Resolve citizen
    citizen_id = handle
    rows = graph_query(GET_CITIZEN, {"citizen_id": handle})
    if not rows:
        rows = graph_query(GET_CITIZEN, {"citizen_id": f"CITIZEN_{handle}"})
        if rows:
            citizen_id = f"CITIZEN_{handle}"
    if not rows:
        raise HTTPException(status_code=404, detail=f"Citizen '{handle}' not found")

    # Get all inbound links
    trust_rows = graph_query(
        "MATCH (src)-[l:LINK]->(c {id: $cid}) "
        "RETURN src.id, src.name, l.permanence, l.weight, l.nature",
        {"cid": citizen_id},
    )

    # Also outbound
    out_rows = graph_query(
        "MATCH (c {id: $cid})-[l:LINK]->(dst) "
        "RETURN dst.id, dst.name, l.permanence, l.weight, l.nature",
        {"cid": citizen_id},
    )

    # Aggregate: weighted mean of permanence, weighted by link weight
    inbound_values = []
    for r in trust_rows:
        perm = r[2] if r[2] is not None else 0.5
        w = r[3] if r[3] is not None else 1.0
        inbound_values.append({"from": r[0], "name": r[1],
                               "permanence": perm, "weight": w, "nature": r[4]})

    outbound_values = []
    for r in out_rows:
        perm = r[2] if r[2] is not None else 0.5
        w = r[3] if r[3] is not None else 1.0
        outbound_values.append({"to": r[0], "name": r[1],
                                "permanence": perm, "weight": w, "nature": r[4]})

    # Weighted mean: permanence * weight / sum(weight)
    total_w = 0.0
    weighted_sum = 0.0
    for v in inbound_values:
        weighted_sum += v["permanence"] * v["weight"]
        total_w += v["weight"]

    aggregated = weighted_sum / total_w if total_w > 0 else 0.0

    return {
        "handle": handle,
        "citizen_id": citizen_id,
        "aggregated_trust": round(aggregated, 4),
        "inbound_links": len(inbound_values),
        "outbound_links": len(outbound_values),
        "inbound": inbound_values,
        "outbound": outbound_values,
    }


# ---------------------------------------------------------------------------
# Balance ($MIND via Helius RPC)
# ---------------------------------------------------------------------------

MIND_MINT = "EgLGfRrjX3du7Pwbj8dzyubSk8ic1WdDfq1ysLqhBm6p"
HELIUS_RPC = os.environ.get(
    "HELIUS_RPC_URL",
    os.environ.get("NEXT_PUBLIC_HELIUS_RPC", "https://mainnet.helius-rpc.com/?api-key=4c3a5fc2-ea3f-45eb-85d5-2f282a6b4401"),
)


@app.get("/balance/{handle}")
async def get_balance(handle: str):
    """$MIND token balance for a citizen.

    Resolves handle → wallet address from L4 graph, then queries Helius RPC
    for SPL token balance of the $MIND mint.
    """
    import httpx

    # Resolve citizen
    citizen_id = handle
    rows = graph_query(GET_CITIZEN, {"citizen_id": handle})
    if not rows:
        rows = graph_query(GET_CITIZEN, {"citizen_id": f"CITIZEN_{handle}"})
        if rows:
            citizen_id = f"CITIZEN_{handle}"
    if not rows:
        raise HTTPException(status_code=404, detail=f"Citizen '{handle}' not found")

    # Get wallet from graph
    wallet_rows = graph_query(
        "MATCH (c {id: $cid}) RETURN c.wallet",
        {"cid": citizen_id},
    )
    wallet = wallet_rows[0][0] if wallet_rows and wallet_rows[0][0] else None

    if not wallet or wallet == "pending":
        return {
            "handle": handle,
            "citizen_id": citizen_id,
            "wallet": wallet,
            "balance_mind": 0.0,
            "balance_sol": None,
            "error": "No wallet address registered" if not wallet else "Wallet pending",
        }

    # Query Helius for $MIND token balance
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(HELIUS_RPC, json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenAccountsByOwner",
                "params": [
                    wallet,
                    {"mint": MIND_MINT},
                    {"encoding": "jsonParsed"},
                ],
            })
            data = resp.json()
            result = data.get("result", {})
            accounts = result.get("value", [])

            balance_mind = 0.0
            for acct in accounts:
                info = acct.get("account", {}).get("data", {}).get("parsed", {}).get("info", {})
                token_amount = info.get("tokenAmount", {})
                balance_mind += float(token_amount.get("uiAmount", 0))

            # Also get SOL balance
            sol_resp = await client.post(HELIUS_RPC, json={
                "jsonrpc": "2.0",
                "id": 2,
                "method": "getBalance",
                "params": [wallet],
            })
            sol_data = sol_resp.json()
            sol_lamports = sol_data.get("result", {}).get("value", 0)
            balance_sol = sol_lamports / 1e9

            return {
                "handle": handle,
                "citizen_id": citizen_id,
                "wallet": wallet,
                "balance_mind": balance_mind,
                "balance_sol": round(balance_sol, 6),
            }
    except Exception as e:
        return {
            "handle": handle,
            "citizen_id": citizen_id,
            "wallet": wallet,
            "balance_mind": None,
            "balance_sol": None,
            "error": f"Helius RPC error: {e}",
        }


# ---------------------------------------------------------------------------
# Infos (aggregate: ping + trust + balance + locations)
# ---------------------------------------------------------------------------


@app.get("/infos/{handle}")
async def get_infos(handle: str):
    """Full citizen info card. Aggregates ping, trust, balance, and locations.

    This is the MCP /infos @handle endpoint — one call, all data.
    """
    import asyncio

    # Run all three in parallel
    ping_task = ping_citizen(handle)
    trust_task = get_trust(handle)
    balance_task = get_balance(handle)

    results = await asyncio.gather(ping_task, trust_task, balance_task, return_exceptions=True)

    ping_data = results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])}
    trust_data = results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])}
    balance_data = results[2] if not isinstance(results[2], Exception) else {"error": str(results[2])}

    # Locations — query L3 graph for Space nodes linked to citizen
    locations = {"physical": [], "virtual": []}
    universe = ping_data.get("universe") if isinstance(ping_data, dict) else None
    if universe:
        try:
            from falkordb import FalkorDB as _FDB
            _db_l3 = _FDB(host=FALKORDB_HOST, port=int(FALKORDB_PORT))
            _g_l3 = _db_l3.select_graph(universe)

            # Space nodes linked to citizen
            loc_rows = _g_l3.query(
                "MATCH (a {id: $handle})-[:link]->(s {node_type: 'space'}) "
                "RETURN s.id, s.name, s.type, s.content",
                {"handle": handle},
            )
            for lr in (loc_rows.result_set or []):
                space_type = lr[2] or ""
                entry = {"id": lr[0], "name": lr[1], "type": space_type, "description": lr[3]}
                if space_type in ("physical", "geo", "location", "city", "venue"):
                    locations["physical"].append(entry)
                else:
                    locations["virtual"].append(entry)
        except Exception:
            pass

    return {
        "handle": handle,
        "ping": ping_data,
        "trust": {
            "aggregated": trust_data.get("aggregated_trust") if isinstance(trust_data, dict) else None,
            "inbound_links": trust_data.get("inbound_links") if isinstance(trust_data, dict) else 0,
            "outbound_links": trust_data.get("outbound_links") if isinstance(trust_data, dict) else 0,
        },
        "balance": {
            "mind": balance_data.get("balance_mind") if isinstance(balance_data, dict) else None,
            "sol": balance_data.get("balance_sol") if isinstance(balance_data, dict) else None,
            "wallet": balance_data.get("wallet") if isinstance(balance_data, dict) else None,
        },
        "locations": locations,
    }


# ---------------------------------------------------------------------------
# Seed (admin only, protected by ADMIN_API_KEY)
# ---------------------------------------------------------------------------

ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY", "")


@app.post("/admin/seed")
async def seed_registry(x_api_key: str = Header(alias="X-API-Key")):
    """Seed the registry from data/registry.json. Requires ADMIN_API_KEY."""
    if not ADMIN_API_KEY or x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    import json
    import time
    from pathlib import Path

    json_path = Path(__file__).parent.parent.parent.parent / "data" / "registry.json"
    if not json_path.exists():
        raise HTTPException(status_code=404, detail=f"registry.json not found at {json_path}")

    data = json.loads(json_path.read_text())
    citizens = data.get("citizens", [])
    orgs = data.get("orgs", [])
    now_s = int(time.time())
    stats = {"orgs": 0, "citizens": 0, "links": 0}

    # Create orgs
    for org in orgs:
        graph_query(
            """MERGE (o:Actor {id: $id})
               SET o.name = $name, o.node_type = 'actor', o.type = 'ORGANIZATION',
                   o.content = $content, o.synthesis = $synthesis,
                   o.status = $status, o.weight = 1.0, o.energy = 0.0,
                   o.stability = 0.5, o.recency = 0.5,
                   o.created_at_s = $ts, o.updated_at_s = $ts,
                   o.org_type = $org_type, o.color = $color,
                   o.github_repository = $github, o.universe = $universe""",
            {
                "id": org["id"], "name": org["name"],
                "content": org.get("description", org["name"]),
                "synthesis": f"{org['name']} — {org.get('description', '')}",
                "status": org.get("status", "active"),
                "ts": now_s, "org_type": org.get("org_type", ""),
                "color": org.get("color", ""), "github": org.get("github_repository", ""),
                "universe": org.get("universe", ""),
            }
        )
        stats["orgs"] += 1

    # Create citizens + links
    for c in citizens:
        graph_query(
            """MERGE (a:Actor {id: $id})
               SET a.name = $name, a.node_type = 'actor', a.type = 'CITIZEN',
                   a.content = $content, a.synthesis = $synthesis,
                   a.status = $status, a.weight = 1.0, a.energy = 0.0,
                   a.stability = 0.5, a.recency = 0.5,
                   a.created_at_s = $ts, a.updated_at_s = $ts,
                   a.wallet = $wallet, a.emoji = $emoji""",
            {
                "id": c["id"], "name": c["name"],
                "content": c.get("description", c["name"]),
                "synthesis": f"{c['name']} — {c.get('description', '')}",
                "status": c.get("status", "active"),
                "ts": now_s, "wallet": c.get("wallet"),
                "emoji": c.get("emoji"),
            }
        )
        stats["citizens"] += 1

        # belongs_to link
        org_id = c.get("org_membership")
        if org_id:
            graph_query(
                """MATCH (a:Actor {id: $cid}), (o:Actor {id: $oid})
                   MERGE (a)-[:LINK {nature: 'belongs_to', relation_kind: 'belongs_to'}]->(o)""",
                {"cid": c["id"], "oid": org_id}
            )
            stats["links"] += 1

        # verified_by link
        if c.get("verification") == "verified":
            graph_query(
                """MATCH (a:Actor {id: $cid})
                   MERGE (v:Actor {id: 'mind-protocol'})
                   MERGE (a)-[:LINK {nature: 'verified_by', relation_kind: 'verified_by',
                          permanence: 0.8, stability: 0.5, recency: 0.5}]->(v)""",
                {"cid": c["id"]}
            )
            stats["links"] += 1

    return {"status": "seeded", **stats}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8766"))
    uvicorn.run("l4.registry.api.app:app", host=host, port=port, reload=True)
