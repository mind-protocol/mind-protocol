# Twitter/X Bridge — Sync: Current State

```
LAST_UPDATED: 2026-03-17
UPDATED_BY: @mentor
STATUS: CANONICAL
```

---

## MATURITY

**What's canonical (v1):**
- Mention polling via GET /2/users/:id/mentions with since_id pagination
- L3 Moment creation through graph_enricher.on_message()
- Orchestrator routing with citizen mention detection
- JSONL logging and since_id file persistence
- Exponential backoff on errors (capped at 300s, max 20 consecutive)
- Graceful degradation when env vars are missing
- home_server.py integration (ENABLE_TWITTER flag, start/stop lifecycle)

**What's still being designed:**
- Nothing — implementation is complete, awaiting production deployment

**What's proposed (v2+):**
- Webhook mode (Account Activity API) to replace polling if scale demands it
- DM reading if X API tier is upgraded
- Media attachment processing (images/videos in mentions)

---

## CURRENT STATE

The Twitter bridge is fully implemented at `mind-mcp/runtime/bridges/twitter_bridge.py`. It follows the same architectural pattern as the Telegram bridge: background daemon thread, polling loop, graph_enricher pipeline, orchestrator enqueue.

`home_server.py` has been updated to start/stop the bridge (lines 210-217, 243-247), gated by `ENABLE_TWITTER=true` (default). The bridge checks for `X_BEARER_TOKEN` and `X_BOT_USER_ID` at startup and logs a warning if either is absent, without crashing.

The bridge has NOT been tested on production yet because the required environment variables are not set in the production environment.

---

## IN PROGRESS

### Production deployment

- **Started:** 2026-03-17
- **By:** @mentor
- **Status:** blocked — env vars not set in prod
- **Context:** The code is merged and home_server.py will attempt to start the bridge on next deploy. Without env vars, it will gracefully skip. Need to add X_BEARER_TOKEN and X_BOT_USER_ID to the production environment to activate.

---

## RECENT CHANGES

### 2026-03-17: Twitter bridge implemented

- **What:** Created `runtime/bridges/twitter_bridge.py` with full mention polling, L3 enrichment, and orchestrator routing. Updated `home_server.py` to start/stop the bridge.
- **Why:** X/Twitter was the only platform with write-only access. Discord and Telegram had full bidirectional bridges. This closes the gap so X interactions produce L3 Moments and build trust through L5 co-activation like every other platform.
- **Files:** `runtime/bridges/twitter_bridge.py` (new), `home_server.py` (modified)
- **Insights:** The graph_enricher interface (`on_message()`) made this straightforward — the bridge is purely a translator from X API response format to the universal pipeline. Most of the work was handling X API v2 quirks (author expansion, rate limit headers, since_id vs offset pagination).

---

## KNOWN ISSUES

No known issues. The implementation has not been tested against the live X API yet, so issues may surface during production testing.

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** VIEW_Deploy / VIEW_Debug

**Where I stopped:** Implementation complete. Blocked on production env var configuration.

**What you need to understand:**
The bridge is enabled by default but safe — it checks for credentials before starting. The moment someone adds `X_BEARER_TOKEN` and `X_BOT_USER_ID` to the production environment, it will start polling on next server restart. No code changes needed.

**Watch out for:**
- X free tier rate limits: 10k reads/month. If poll interval is too aggressive, you will hit 429s. Default 300s (5 min) is safe.
- `since_id` file: on first run, no since_id exists, so the first poll fetches the most recent mentions (up to 100). After that, pagination kicks in.
- The bridge imports `graph_enricher` via `sys.path.insert` (not a package import) because `scripts/` is not a proper Python package. This works but is fragile.

**Open questions I had:**
- Should the bridge also track quote tweets (retweets with comment) that mention the bot? Currently only direct mentions are polled.

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Twitter bridge is implemented and integrated into home_server.py. It polls for mentions, creates L3 Moments, routes to orchestrator, and builds trust — identical pipeline to Telegram. Not yet live because production env vars are not set.

**Decisions made:**
- 5-minute poll interval default (conservative for free tier)
- Bridge enabled by default (`ENABLE_TWITTER=true`) but fails safe without credentials
- Citizen routing via @handle matching against `citizens/` directory

**Needs your input:**
- Add `X_BEARER_TOKEN` and `X_BOT_USER_ID` to the production environment
- Decide if `X_POLL_INTERVAL` should be tuned (default 300s)

---

## TODO

### Doc/Impl Drift

No drift — docs written from current implementation.

### Immediate

- [ ] Add `X_BEARER_TOKEN` to production environment
- [ ] Add `X_BOT_USER_ID` to production environment
- [ ] Set `X_POLL_INTERVAL` if default 300s is not desired
- [ ] Deploy and verify bridge starts (check logs for "X/Twitter bridge started")
- [ ] Test live polling — send a mention to the bot account on X
- [ ] Verify L3 Moments appear in the graph after mention processing

### Later

- [ ] Monitor rate limit usage over first week of production
- IDEA: Quote tweet tracking (retweets with comment mentioning the bot)
- IDEA: Webhook mode (Account Activity API) for lower latency if polling proves insufficient

---

## POINTERS

| What | Where |
|------|-------|
| Bridge implementation | `mind-mcp/runtime/bridges/twitter_bridge.py` |
| Telegram bridge (architectural ancestor) | `mind-mcp/runtime/bridges/telegram_bridge.py` |
| Graph enricher pipeline | `mind-mcp/scripts/graph_enricher.py` |
| Orchestrator message queue | `mind-mcp/runtime/orchestrator/message_queue.py` |
| Outbound send handler | `mind-mcp/runtime/bridges/send_handler.py` |
| Home server integration | `mind-mcp/home_server.py` (lines 210-217, 243-247) |
| Mention log | `shrine/state/twitter_mentions.jsonl` |
| Pagination state | `shrine/state/twitter_since_id.txt` |
| PATTERNS doc | `mind-protocol/docs/bridges/PATTERNS_Twitter_Bridge.md` |
