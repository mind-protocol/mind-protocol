# Providers & Adapters (Claude Code, Codex, Gemini)

## Claude Code Hooks
- `UserPromptSubmit` → invoke `sdk/claude-hooks/user_prompt.py`  
  Payload: `{content, language, conversation_id}`. Use `intent_merge_key=conversation_id` to merge rapid revisions; include `rate_limit_bucket=provider:{user}`.
- `Stop`, `PreCompact` → `sdk/claude-hooks/session_compaction.py`  
  Emit `session.compaction` with pointers to evidence (`local://sha256/...`) rather than raw transcripts. Attach `business_impact` if compaction triggered by severity.
- `PreToolUse` (Write/Edit/NotebookEdit) → `sdk/claude-hooks/tool_request.py`  
  Map Claude tool type to capability (`fs.write`, `notebook.apply`, etc.) and forward args. Include `required_capabilities` if downstream tool needs secrets.
- `.claude/settings.json` snippet:
  ```json
  {
    "hooks": {
      "UserPromptSubmit": "python sdk\\claude-hooks\\user_prompt.py",
      "Stop": "python sdk\\claude-hooks\\session_compaction.py",
      "PreCompact": "python sdk\\claude-hooks\\session_compaction.py",
      "PreToolUse": "python sdk\\claude-hooks\\tool_request.py"
    }
  }
  ```
  Each script should:
  1. Read event payload (stdin JSON).  
  2. Build `membrane.inject`, sign with organization key (load from `.mind/keys/dev.key`).  
  3. Post via the shared helper `.claude/hooks/membrane_bus.py` (minimal WS client) to the inject endpoint.
  - `capture_user_prompt.py` publishes `ui.action.user_prompt` with `{session_id, entity_id, content, context_file}`.  
  - `capture_conversation.py` emits `provider.claude.output` snapshots with pointers to the stored conversation/metadata.  
  - `precompact_conversation.py` emits `session.compaction` when Claude triggers a compact, so orchestrator/renderers close the old context.

## Codex & Gemini (PTY wrappers)
- Launch the model process with `cwd=WORKSPACE_DIR`.
- Capture STDIN → `ui.action.user_prompt`; STDOUT (completion) → `provider.codex.output` (or `citizen.response` if running as a citizen).
- File mutations are surfaced by the shared FS watcher → `citizen_file_ops`.
- Wrapper script `sdk/providers/run_codex.py` provides both interactive & scripted modes:
  ```bash
  # Interactive REPL
  python sdk/providers/run_codex.py --org dev-org codex --tty

  # Non-interactive (continues existing session)
  python sdk/providers/run_codex.py \
      --org dev-org \
      --session-id codex-session-42 \
      --prompt "Summarise the latest RFQ." \
      --prompt "Propose next steps." \
      --close-after-prompts \
      codex --tty
  ```
  Environment variables honored: `MEMBRANE_WS_INJECT`, `MEMBRANE_ORG`, `MEMBRANE_DEV_PUBKEY`, `MEMBRANE_DEV_SIGNATURE`. All output events carry `channel=provider.codex.output`, plus `session_id`, `stream` (`stdout`/`stderr`), and raw data.

## File System Watcher
- Watches workspace paths; on save emits `membrane.inject(channel=citizen_file_ops, payload={path, sha256, change_type})`.
- Implements dedupe window (e.g., 1s) and rate limiting per origin bucket.
- Ignores directories: `.git/`, `node_modules/`, `__pycache__/`, `.mind/`.  
- Configurable via `.mind/watch.yaml` (include/exclude globs).  
- Should detect create/delete/modify; include `change_type` to help downstream logic.

## Git Runner Tool
- Consumes `tool.request.git.commit|branch|pr`.
- Executes Git commands locally (building commit message from payload), pushes results via `tool.result {commit_sha, branch, pr_url?}`.
- Honors lane ACK policy (e.g., require human approval before merging).
- Commits should embed links to evidence (hash URIs) and reference mission IDs in the message footer.

## Renderer Tool
- Subscribes to `mission.done` / `tool.result` events.
- Generates documentation or site artifacts under `publications/` and optionally opens PRs (through Git Runner).
- Templates stored in `renderers/templates/`; configuration in `.mind/renderers.yaml`.
- Emits `telemetry.renderer` events with durations and counts.

## Security & Keys
- All adapters use the org dev ed25519 key (store in `.mind/keys/dev.key`). Rotate by injecting `policy.change` events (`governance.keys.updated`). Keys are not hard-coded in source.
- Sidecar provides `sidecar key rotate` helper which generates new key pairs and emits the appropriate stimulus.
- Never log private keys; ensure scripts redact secrets on failure.
