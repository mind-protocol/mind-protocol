# IMPLEMENTATION: Membrane System

```
STATUS: V1 SPEC
PURPOSE: Code architecture for structured graph dialogues
```

---

## Code Structure

```
tools/mcp/
└── membrane_server.py          # MCP server exposing membrane tools

mind/connectome/
├── __init__.py                 # Exports ConnectomeRunner (membrane)
├── runner.py                   # ConnectomeRunner - protocol execution
├── session.py                  # Session state management + call stack
├── loader.py                   # YAML protocol loading
├── steps.py                    # Step execution (ask, query, branch, call_protocol, create)
├── validation.py               # Answer validation
└── templates.py                # Interpolation and templating

skills/                         # Skill markdown files (domain knowledge)
├── health_coverage.md
├── module_design.md
├── feature_implementation.md
├── escalation_handling.md
├── decision_capture.md
└── progress_tracking.md

protocols/                      # Protocol YAML files (procedures)
├── explore_space.yaml
├── add_objectives.yaml
├── add_invariant.yaml
├── add_health_coverage.yaml
├── add_implementation.yaml
├── record_work.yaml
├── investigate.yaml
└── resolve_blocker.yaml

tests/connectome_v0/
├── connectomes/                # Test protocol definitions
│   ├── create_validation.yaml
│   ├── document_progress.yaml
│   └── explore_escalation.yaml
└── test_*.py                   # 30 passing tests
```

---

## Key Components

### MCP Server (`tools/mcp/membrane_server.py`)

| Class | Purpose | Dock |
|-------|---------|------|
| `MembraneServer` | JSON-RPC handler for MCP protocol | Line 51 |
| `_handle_call_tool` | Routes tool calls to implementations | Line 173 |
| `_format_response` | Formats runner response for MCP | Line 234 |

**Tools exposed:**
- `membrane_start` → `runner.start(protocol_name)`
- `membrane_continue` → `runner.continue_session()`
- `membrane_abort` → `runner.abort()`
- `membrane_list` → lists protocol YAML files

### Skill Loading (Doctor responsibility)

Skills are markdown files loaded into agent context before protocol execution:

```python
def load_skill(domain: str) -> str:
    """Load skill markdown for domain knowledge."""
    path = skills_dir / f"{domain}.md"
    return path.read_text()

# Doctor loads skill, provides to agent
skill_content = load_skill("health_coverage")
# Agent has skill knowledge when answering protocol questions
```

### Runner (`mind/connectome/runner.py`)

| Class | Purpose | Dock |
|-------|---------|------|
| `ConnectomeRunner` | Protocol executor (the membrane) | Class definition |
| `start()` | Creates session, loads protocol, returns first step | Method |
| `continue_session()` | Validates answer, advances step, handles branching | Method |
| `abort()` | Cleans up session | Method |

### Session (`mind/connectome/session.py`)

| Field | Type | Purpose |
|-------|------|---------|
| `session_id` | str | Unique identifier |
| `protocol_name` | str | Which protocol is running |
| `current_step` | str | Current step ID |
| `answers` | Dict | Step ID → answer mapping |
| `context` | Dict | Interpolation context |
| `call_stack` | List | Stack for sub-protocol calls |
| `created_nodes` | List | Nodes to commit |
| `created_links` | List | Links to commit |

### Steps (`mind/connectome/steps.py`)

| Step Type | Handler | Output |
|-----------|---------|--------|
| `ask` | Returns question + expects to agent | `{status: 'active', step: {...}}` |
| `query` | Executes graph query, stores result | Advances to next step |
| `branch` | Evaluates condition, routes to then/else/cases | Advances to selected step |
| `call_protocol` | Pushes stack, starts sub-protocol | Executes sub-protocol |
| `create` | Instantiates nodes/links from spec | `{status: 'complete', created: {...}}` |
| `update` | Modifies existing node | Advances to next step |

### Validation (`mind/connectome/validation.py`)

| Validator | Checks |
|-----------|--------|
| `validate_string` | min_length, pattern |
| `validate_id` | node exists, type matches |
| `validate_id_list` | each ID valid, min/max count |
| `validate_string_list` | list format, min/max count |
| `validate_enum` | value in options |

### Templates (`mind/connectome/templates.py`)

| Function | Purpose |
|----------|---------|
| `interpolate()` | `{variable}` → value from context |
| `slugify()` | text → url-safe-slug |
| `truncate()` | text → max N chars |
| `timestamp()` | → current ISO timestamp |

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        MCP CLIENT                                │
│  (Claude Code, agent)                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ JSON-RPC over stdio
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     membrane_server.py                           │
│  MembraneServer.handle_request() → routes to tool handlers      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ runner.start() / runner.continue_session()
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        runner.py                                 │
│  ConnectomeRunner manages session lifecycle                      │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────────────┐
│      session.py          │     │           loader.py              │
│  Session state           │     │  Load YAML → membrane dict       │
└─────────────────────────┘     └─────────────────────────────────┘
                              │
                              │ execute step
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         steps.py                                 │
│  ask → return question                                          │
│  query → call graph, store result                               │
│  create → instantiate nodes/links                               │
│  update → modify existing node                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────────────┐
│    validation.py         │     │         templates.py             │
│  Validate answer format  │     │  Interpolate {vars} in specs    │
└─────────────────────────┘     └─────────────────────────────────┘
                              │
                              │ graph operations
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     mind/physics/graph.py                      │
│  GraphOps.create_node(), create_link()                          │
│  GraphQueries.find(), related_to()                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Configuration

### MCP Server Config (`.mcp.json`)

```json
{
  "mcpServers": {
    "membrane": {
      "command": "python3",
      "args": ["tools/mcp/membrane_server.py"],
      "cwd": "/path/to/mind"
    }
  }
}
```

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `MIND_FALKORDB_HOST` | Graph database host | localhost |
| `MIND_FALKORDB_PORT` | Graph database port | 6379 |

---

## Membrane YAML Location

Membrane definitions live in:
```
tests/connectome_v0/connectomes/
├── create_validation.yaml
├── document_progress.yaml
└── explore_escalation.yaml
```

**Future:** Move to `mind/connectome/membranes/` or `config/membranes/`

---

## Protocol YAML (Not Yet Implemented)

Protocols will live alongside membranes:
```
mind/connectome/protocols/
├── module_design.yaml
├── health_coverage.yaml
├── feature_implementation.yaml
├── escalation_handling.yaml
├── decision_capture.yaml
└── progress_tracking.yaml
```

Doctor will load and execute protocols, calling membranes as specified.

---

## Extension Points

| Extension | Where | How |
|-----------|-------|-----|
| Add new membrane | `tests/connectome_v0/connectomes/` | Create YAML file |
| Add new step type | `mind/connectome/steps.py` | Add handler function |
| Add new validator | `mind/connectome/validation.py` | Add validation function |
| Add new template filter | `mind/connectome/templates.py` | Add filter function |
| Add graph operations | `mind/physics/graph.py` | Add to GraphOps/GraphQueries |

---

## Tests

```bash
# Run all connectome tests
pytest tests/connectome_v0/ -v

# Current status: 30 passing
```

| Test File | Coverage |
|-----------|----------|
| `test_loader.py` | YAML loading, schema validation |
| `test_session.py` | Session lifecycle |
| `test_validation.py` | All answer types |
| `test_steps.py` | Step execution |
| `test_runner.py` | End-to-end flows |

---

## CHAIN

- **Prev:** VALIDATION_Membrane_System.md
- **Next:** SYNC_Membrane_System.md
- **Patterns:** PATTERNS_Membrane_System.md
- **Algorithm:** ALGORITHM_Membrane_System.md
