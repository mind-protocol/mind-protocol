# Mind Protocol Templates

Templates for `.mind/` configuration in client repos.

## Usage

Copy `templates/mind/` to `.mind/` in your repo:

```bash
cp -r templates/mind/ .mind/
```

Or use the mind CLI (when available):

```bash
mind init
```

## Contents

| File | Purpose |
|------|---------|
| `config.yaml` | Protocol version, schema source, L4 endpoints |
| `schema.yaml` | Graph schema v1.8.1 (node types, links, invariants) |

## Versioning

- `protocol.version` — Mind Protocol version (this repo)
- `protocol.schema_version` — Schema version (from `l4/schema/schema.yaml`)

Both should match between repos for compatibility.
