# Event Contracts (v1.1)

## Write Path (fan-in): `membrane.inject`
- **Required fields**  
  `v`, `id`, `ts`, `type=membrane.inject`, `org`, `scope`, `channel`, `origin`, `ttl_frames`, `payload`, `sig`.  
  - `scope ∈ {personal, organizational, infrastructure}`  
  - `channel` must follow `^[a-z0-9._:-]+$` (namespace.style)  
  - `sig` holds `{algo: "ed25519", pubkey, signature}` (hex/base64 allowed; SDKs handle encoding)
- **Recommended hardening fields**  
  `dedupe_key`, `intent_merge_key`, `rate_limit_bucket`, `business_impact`, `source_trust_estimate`, `ack_policy`, `required_capabilities`, `features_raw` (numeric hints for novelty/urgency/uncertainty/etc.).  
  These fields allow integrator & orchestrator physics to respond without bespoke logic.
- **TTL semantics** – `ttl_frames` is expressed in engine frames (not ms). Engines drop expired stimuli and broadcast `inject.rejected {reason:"ttl_expired"}` for transparency.
- **Signature process** – Sidecar signs the canonical JSON serialization (sorted keys, UTF-8). Keys are rotated via `governance.keys.updated`.

### Representative Examples
```jsonc
// UI prompt submission
{
  "type":"membrane.inject","org":"dev-org","scope":"organizational",
  "channel":"ui.action.user_prompt","origin":"ui","ttl_frames":600,
  "payload":{"content":"summarise the term sheet","conversation_id":"tab-42"},
  "intent_merge_key":"tab-42","dedupe_key":"sha256:…","sig":{…}
}
```
```jsonc
// File save watcher event
{
  "type":"membrane.inject","org":"dev-org","scope":"organizational",
  "channel":"citizen_file_ops","origin":"sidecar","ttl_frames":300,
  "payload":{"path":"app/pricing/model.ts","sha256":"…","change":"modified"},
  "features_raw":{"novelty":0.35,"urgency":0.1}
}
```
```jsonc
// Tool request (Git commit)
{
  "type":"membrane.inject","org":"dev-org","channel":"tool.request",
  "origin":"orchestrator","payload":{
    "request_id":"git-commit-1730",
    "capability":"git.commit",
    "args":{"paths":["app/pricing/model.ts"],"message":"fix pricing drift"}
  },
  "ack_policy":"tool_required","ttl_frames":900,"sig":{…}
}
```

## Read Path (fan-out)
- **Attention & Perception**: `wm.emit`, `percept.frame`, optional `percept.seed` for new observers.
- **Structure**: `graph.delta.node.upsert/delete`, `graph.delta.link.upsert/delete`.
- **Membrane**: `membrane.transfer.up`, `membrane.transfer.down`, `membrane.export.rejected`, `membrane.permeability.updated`.
- **Work orchestration**: `intent.created`, `intent.escalated`, `mission.assigned`, `mission.progress`, `mission.done`.
- **Tool mesh**: `tool.offer`, `tool.requested`, `tool.result`.
- **Operations & economics**: `telemetry.integrator`, `telemetry.qos`, `economy.spend`, `economy.ubc.distributed`, `hierarchy.snapshot`, `policy.applied` / `policy.rejected`.
- **Governance**: `governance.keys.updated`, `policy.change` echoes (for audit trail).

### Broadcast payload snippets
```jsonc
// Working memory pulse
{ "type":"wm.emit","ts":"2025-10-27T12:05:11Z","entities":["E.builder","E.trader","E.guardian"] }
```
```jsonc
// Percept frame
{
  "type":"percept.frame","entity_id":"E.builder","ts":"…",
  "affect":{"valence":0.22,"arousal":0.71},
  "goal_match":0.64,"novelty":0.38,"uncertainty":0.31,"peripheral_pressure":0.42,
  "anchors_top":["N.mem_brain","N.ws_mux"],"anchors_peripheral":["N.pareto"],"commentary":"RFQ surge"
}
```
```jsonc
// Tool result (Git commit)
{
  "type":"tool.result","request_id":"git-commit-1730","ts":"…",
  "ok":true,
  "artifact":{"type":"git_commit","sha":"abc123","branch":"auto/fix-pricing"},
  "telemetry":{"duration_ms":830}
}
```

## Schema registry (v3) alignment
- Canonical JSON-Schema definitions live in **FalkorDB `schema_registry`**. Use `tools/generate_complete_type_reference.py` to export the latest inventory (Parts 1–4) and merge changes instead of editing ad hoc copies.  
- Layer-4 protocol types are ingested via `python tools/schema_registry/add_protocol_l4.py --host localhost --port 6379` (idempotent, regenerates node/link field definitions).  
- Query helper (Cypher):
  ```cypher
  MATCH (s:schema_registry {version: 3}) RETURN s.name, s.defn;
  ```
- When adding payloads or fields, update the registry first, regenerate the reference, then link the regenerated markdown into citizen prompts.

### Ecosystem layer type inventory (schema_registry v3)
_These types extend the existing Part 3/4 inventories; ensure they are recorded in the registry before use._

### L3 node definitions (v3)

| Node Type | Description | Key Fields (in addition to universal attributes) |
|-----------|-------------|--------------------------------------------------|
| `Ecosystem` | Domain container (e.g. “trading commodities”) | `slug` (string), `domain` (string), `version` (string) |
| `Org_Profile` | L3 view of an organization | `org_id` (string), `jurisdiction` (string), `tags` (string[]) |
| `Public_Presence` | Published capability/canal listing | `channels` (enum[]), `capabilities` (string[]), `visibility` (enum public/partners/private), `attestations` (node ids) |
| `Capability_Descriptor` | Capability descriptor (refers to L4 schema) | `name` (string), `schema_ref` (string), `cost_hint` (string) |
| `RFQ` | Structured request for quote | `commodity` (string), `qty` (object `{value, unit}`), `incoterm` (string), `delivery_window` (object `{from,to}`), `counterparty_pref` (string[]) |
| `Quote` | Response to `RFQ` | `price` (float), `currency` (string), `valid_until` (datetime), `terms` (string) |
| `Deal` | Business deal | `deal_type` (enum trade/partnership/service), `state` (enum Proposed/Negotiating/Agreed/Settled/Cancelled), `instrument` (enum TermSheet/Confirmation), `qty` (float), `price` (float), `incoterm` (string) |
| `Agreement` | Signed agreement | `agreement_type` (enum MSA/NDA/SLA/Confirmation), `effective_at` (datetime), `expires_at` (datetime) |
| `Instrument` | Contract template | `instrument_type` (enum TermSheet/Confirmation/etc.), `template_uri` (string), `version` (string) |
| `Info_Asset` | Shareable information artefact | `title` (string), `access` (enum public/bilateral/paid), `pointer` (CID/URI), `tags` (string[]) |
| `Info_Offer` | Offer to share an info asset | `price_model` (enum free/one_off/subscription), `terms` (string) |
| `Info_Request` | Request for information | `topic` (string), `deadline` (datetime), `constraints` (string) |
| `Market` | Market segment | `name` (string), `region` (string), `product_class` (string) |
| `Market_Signal` | Market signal (exists already) | `asset` (string), `signal_type` (enum price/volume/sentiment), `timestamp` (datetime), `value` (float) |
| `Counterparty` | External party profile | `company_type` (enum startup/enterprise/dao/protocol), `status` (enum active/inactive/etc.), `website` (string) |
| `Contact_Channel` | Contact method | `channel_type` (enum email/api/portal), `address` (string) |
| `Attestation` | Cryptographic or signed attestation | `sig` (string), `issuer` (string), `purpose` (string) |
| `Reputation_Assessment` | Reputation assessment (existing) | `assessment_type` (enum credibility/expertise/trustworthiness), `score` (0..1), `subject` (node id) |
| `Policy_Lane` | Lane definition | `lane_id` (string), `capacity` (int), `ack_policy` (enum none/human_required/tool_required) |
| `Citizen_Template` | Citizen bootstrap template | `image` (string), `default_subscribe` (string[]), `default_publish` (string[]), `limits` (object `{cpu, mem}`) |
| `Tool_Template` | Tool bootstrap template | `capabilities` (string[]), `runner_image` (string), `resources` (object `{cpu, mem}`) |
| `Renderer_Template` | Renderer bootstrap template | `triggers` (string[]), `output` (enum git:publications/site:static), `branch_prefix` (string) |

### L3 link definitions (v3)

| Link Type | From → To | Description | Type-specific fields |
|-----------|-----------|-------------|----------------------|
| `PUBLISHES` | Org_Profile → Public_Presence | Org publishes its public presence | `audience` (enum public/partners) |
| `LISTS_CAPABILITY` | Public_Presence → Capability_Descriptor | Presence lists capability | none |
| `HAS_CHANNEL` | Public_Presence → Contact_Channel | Presence exposes a channel | `priority` (enum primary/secondary) |
| `CONFORMS_TO` | Capability_Descriptor/Tool_Template/Citizen_Template → Schema/Capability | (References L4 definitions) | `schema_version` (string) |
| `OFFERS` | Org_Profile → Info_Offer / Info_Asset | Org offers asset | `access_level` (enum) |
| `SEEKS` | Org_Profile → Info_Request | Org seeks an info request | none |
| `SHARES_WITH` | Info_Asset → Org_Profile | Asset shared with org | `access_level` (enum) |
| `RESTRICTED_BY` | Info_Asset/Info_Offer → Policy_Lane/Agreement | Access controlled by policy/agreement | `restriction_type` (enum lane/agreement) |
| `PROPOSES` | Org_Profile → Deal / RFQ | Org proposes deal/RFQ | none |
| `QUOTES_FOR` | Org_Profile → Quote | Org issues quote | none |
| `RESPONDS_TO` | Quote → RFQ | Quote responds to RFQ | `response_time_ms` (float) |
| `NEGOTIATES` | Org_Profile ↔ Deal | Negotiation relationship | `role` (enum buyer/seller) |
| `USES_INSTRUMENT` | Deal → Instrument | Deal uses template | `version` (string) |
| `SETTLED_BY` | Deal → Agreement | Deal settled by agreement | `settlement_date` (datetime) |
| `REFERENCES_MARKET` | RFQ/Deal/Quote → Market | References relevant market | none |
| `EVIDENCED_BY` | Deal/Quote/Agreement/Info_Asset → Attestation | Evidence pointer | `evidence_type` (enum doc/hash) |
| `ENDORSES` | Org_Profile → Org_Profile/Capability_Descriptor | Org endorses another org/capability | `endorsement_type` (enum reputation/capability) |
| `TRUSTS` | Org_Profile → Reputation_Assessment | Org trusts assessment | `context` (string) |
| `ACTIVATES` | Ecosystem → Citizen_Template/Tool_Template/Renderer_Template | Ecosystem activates template | `activation_id` (string) |
| `DEPLOYS` | Ecosystem → Org_Profile | Ecosystem deploys org | `deployment_id` (string) |
| `ROUTES_VIA` | Policy_Lane → Capability_Descriptor | Lane routes requests to capability | `priority` (int) |

> **Merge guidance**: if the registry already contains earlier revisions, diff v3 fields against the current entries and update attributes (e.g., required fields, enums) instead of creating duplicates. Regenerate the Complete Type Reference after every registry change.

### Ingestion helper
- Run `python tools/schema_registry/add_ecosystem_v3.py --host localhost --port 6379` to upsert these schemas into `schema_registry`.  
- Afterwards regenerate the reference:  
  `python tools/generate_complete_type_reference.py > docs/COMPLETE_TYPE_REFERENCE.md`  
- Commit the updated reference so citizens / adapters ingest the latest schema definitions.

All consumers subscribe via the broadcast namespace; no component should issue pull requests or rely on REST snapshots.
