# IMPLEMENTS Link Formation - Sample Queries from SYNC.md

**Version:** 1.0
**Created:** 2025-10-25
**Purpose:** Demonstrate IMPLEMENTS link formation by parsing SYNC.md for file-task connections

---

## Overview

This document demonstrates the IMPLEMENTS link formation loop by extracting real file-task connections from SYNC.md. These samples prove the pattern works and provide templates for the sync_md_parser implementation.

**Link Pattern:**
```cypher
(File)-[:IMPLEMENTS {detected_by: "sync_md_parser", anchor_text: "...", confidence_reason: "..."}]->(Task)
```

---

## Sample 1: TRACK B v1.2 Files → Task

**Task:** "TRACK B v1.2 Production Hardening"

**Files Implementing:**
- `docs/specs/v2/ops_and_viz/lv2_file_process_telemetry.md`
- `docs/specs/v2/ops_and_viz/ownership_raci_model.md`

**Cypher Formation:**

```cypher
// Create Task node
MERGE (t:Task {id: 'track_b_v1_2_production_hardening'})
  SET t.title = 'TRACK B v1.2 Production Hardening',
      t.description = 'Production-ready file & process telemetry with ring buffers, safety rails, and security',
      t.status = 'completed',
      t.priority = 'high',
      t.completed_at = datetime('2025-10-25T21:00:00Z')

// Create File nodes (if not exist)
MERGE (f1:File {name: 'c:\\users\\reyno\\mind-protocol\\docs\\specs\\v2\\ops_and_viz\\lv2_file_process_telemetry.md'})
  SET f1.metadata.original_path = 'C:\\Users\\reyno\\mind-protocol\\docs\\specs\\v2\\ops_and_viz\\lv2_file_process_telemetry.md',
      f1.metadata.rel_path = 'docs/specs/v2/ops_and_viz/lv2_file_process_telemetry.md'

MERGE (f2:File {name: 'c:\\users\\reyno\\mind-protocol\\docs\\specs\\v2\\ops_and_viz\\ownership_raci_model.md'})
  SET f2.metadata.original_path = 'C:\\Users\\reyno\\mind-protocol\\docs\\specs\\v2\\ops_and_viz\\ownership_raci_model.md',
      f2.metadata.rel_path = 'docs/specs/v2/ops_and_viz/ownership_raci_model.md'

// Create IMPLEMENTS links
MATCH (f1:File {name: 'c:\\users\\reyno\\mind-protocol\\docs\\specs\\v2\\ops_and_viz\\lv2_file_process_telemetry.md'})
MATCH (t:Task {id: 'track_b_v1_2_production_hardening'})
CREATE (f1)-[:IMPLEMENTS {
  detected_by: 'sync_md_parser',
  task_section: '2025-10-25 21:00 - Luca',
  anchor_text: 'TRACK B specification updated to v1.2 with comprehensive production hardening',
  confidence_reason: 'Explicit file path + completion statement in SYNC.md',
  energy: 0.8,
  confidence: 0.95,
  formation_trigger: 'sync_md_parser',
  goal: 'Links spec file to implementation task',
  mindstate: 'Parsing SYNC.md for file-task connections',
  valid_at: timestamp(),
  created_at: timestamp()
}]->(t)

MATCH (f2:File {name: 'c:\\users\\reyno\\mind-protocol\\docs\\specs\\v2\\ops_and_viz\\ownership_raci_model.md'})
MATCH (t:Task {id: 'track_b_v1_2_production_hardening'})
CREATE (f2)-[:IMPLEMENTS {
  detected_by: 'sync_md_parser',
  task_section: '2025-10-25 21:00 - Luca',
  anchor_text: 'Ownership & RACI model created with Direct OWNS link pattern',
  confidence_reason: 'Explicit file path + creation statement in SYNC.md',
  energy: 0.8,
  confidence: 0.95,
  formation_trigger: 'sync_md_parser',
  goal: 'Links ownership spec to implementation task',
  mindstate: 'Parsing SYNC.md for file-task connections',
  valid_at: timestamp(),
  created_at: timestamp()
}]->(t)
```

---

## Sample 2: PR-C Dashboard Events Files → Task

**Task:** "PR-C Dashboard Events Implementation"

**Files Implementing:**
- `orchestration/mechanisms/consciousness_engine_v2.py`
- `orchestration/mechanisms/diffusion_runtime.py`

**Cypher Formation:**

```cypher
// Create Task node
MERGE (t:Task {id: 'pr_c_dashboard_events'})
  SET t.title = 'PR-C Dashboard Events (node.flip, link.flow.summary)',
      t.description = 'Implement dashboard event emission for node energy deltas and link flows',
      t.status = 'completed',
      t.priority = 'critical',
      t.completed_at = datetime('2025-10-25T15:05:00Z')

// Create File nodes
MERGE (f1:File {name: 'c:\\users\\reyno\\mind-protocol\\orchestration\\mechanisms\\consciousness_engine_v2.py'})
  SET f1.metadata.original_path = 'C:\\Users\\reyno\\mind-protocol\\orchestration\\mechanisms\\consciousness_engine_v2.py',
      f1.metadata.rel_path = 'orchestration/mechanisms/consciousness_engine_v2.py',
      f1.metadata.lang = 'python'

MERGE (f2:File {name: 'c:\\users\\reyno\\mind-protocol\\orchestration\\mechanisms\\diffusion_runtime.py'})
  SET f2.metadata.original_path = 'C:\\Users\\reyno\\mind-protocol\\orchestration\\mechanisms\\diffusion_runtime.py',
      f2.metadata.rel_path = 'orchestration/mechanisms/diffusion_runtime.py',
      f2.metadata.lang = 'python'

// Create IMPLEMENTS links
MATCH (f1:File {name: 'c:\\users\\reyno\\mind-protocol\\orchestration\\mechanisms\\consciousness_engine_v2.py'})
MATCH (t:Task {id: 'pr_c_dashboard_events'})
CREATE (f1)-[:IMPLEMENTS {
  detected_by: 'sync_md_parser',
  task_section: '2025-10-25 15:05 - Felix',
  anchor_text: 'PR-C implementation complete - node.flip and link.flow.summary events fully coded',
  confidence_reason: 'File path mentioned with line numbers + completion statement',
  energy: 0.85,
  confidence: 0.98,
  formation_trigger: 'sync_md_parser',
  goal: 'Links consciousness engine to PR-C implementation',
  mindstate: 'Parsing SYNC.md for code-task connections',
  valid_at: timestamp(),
  created_at: timestamp()
}]->(t)

MATCH (f2:File {name: 'c:\\users\\reyno\\mind-protocol\\orchestration\\mechanisms\\diffusion_runtime.py'})
MATCH (t:Task {id: 'pr_c_dashboard_events'})
CREATE (f2)-[:IMPLEMENTS {
  detected_by: 'sync_md_parser',
  task_section: '2025-10-25 15:05 - Felix',
  anchor_text: 'Link Flow Accumulator - Added _frame_link_flow to __slots__',
  confidence_reason: 'File path + specific implementation detail (accumulator)',
  energy: 0.80,
  confidence: 0.95,
  formation_trigger: 'sync_md_parser',
  goal: 'Links diffusion runtime to PR-C link flow tracking',
  mindstate: 'Parsing SYNC.md for code-task connections',
  valid_at: timestamp(),
  created_at: timestamp()
}]->(t)
```

---

## Sample 3: Counters Endpoint Files → Task

**Task:** "Telemetry Counters Endpoint Implementation"

**Files Implementing:**
- `orchestration/libs/websocket_broadcast.py`
- `orchestration/adapters/api/control_api.py`

**Cypher Formation:**

```cypher
// Create Task node
MERGE (t:Task {id: 'telemetry_counters_endpoint'})
  SET t.title = 'Telemetry Counters Endpoint',
      t.description = 'GET /api/telemetry/counters endpoint for event count tracking',
      t.status = 'completed',
      t.priority = 'high',
      t.completed_at = datetime('2025-10-25T15:35:00Z')

// Create File nodes
MERGE (f1:File {name: 'c:\\users\\reyno\\mind-protocol\\orchestration\\libs\\websocket_broadcast.py'})
  SET f1.metadata.original_path = 'C:\\Users\\reyno\\mind-protocol\\orchestration\\libs\\websocket_broadcast.py',
      f1.metadata.rel_path = 'orchestration/libs/websocket_broadcast.py',
      f1.metadata.lang = 'python'

MERGE (f2:File {name: 'c:\\users\\reyno\\mind-protocol\\orchestration\\adapters\\api\\control_api.py'})
  SET f2.metadata.original_path = 'C:\\Users\\reyno\\mind-protocol\\orchestration\\adapters\\api\\control_api.py',
      f2.metadata.rel_path = 'orchestration/adapters/api/control_api.py',
      f2.metadata.lang = 'python'

// Create IMPLEMENTS links
MATCH (f1:File {name: 'c:\\users\\reyno\\mind-protocol\\orchestration\\libs\\websocket_broadcast.py'})
MATCH (t:Task {id: 'telemetry_counters_endpoint'})
CREATE (f1)-[:IMPLEMENTS {
  detected_by: 'sync_md_parser',
  task_section: '2025-10-25 15:35 - Atlas',
  anchor_text: 'Counter Tracking in ConsciousnessStateBroadcaster - Added event_counts_total dict',
  confidence_reason: 'File mentioned with counter tracking implementation details',
  energy: 0.85,
  confidence: 0.95,
  formation_trigger: 'sync_md_parser',
  goal: 'Links broadcaster module to counter tracking feature',
  mindstate: 'Parsing SYNC.md for infrastructure-task connections',
  valid_at: timestamp(),
  created_at: timestamp()
}]->(t)

MATCH (f2:File {name: 'c:\\users\\reyno\\mind-protocol\\orchestration\\adapters\\api\\control_api.py'})
MATCH (t:Task {id: 'telemetry_counters_endpoint'})
CREATE (f2)-[:IMPLEMENTS {
  detected_by: 'sync_md_parser',
  task_section: '2025-10-25 15:35 - Atlas',
  anchor_text: 'GET /api/telemetry/counters Endpoint - Location: control_api.py lines 1023-1094',
  confidence_reason: 'Explicit file path with line numbers for endpoint implementation',
  energy: 0.85,
  confidence: 0.98,
  formation_trigger: 'sync_md_parser',
  goal: 'Links control API to counters REST endpoint',
  mindstate: 'Parsing SYNC.md for API-task connections',
  valid_at: timestamp(),
  created_at: timestamp()
}]->(t)
```

---

## Sample 4: Persistence Bug Fixes → Task

**Task:** "Persistence Operational - Energy Attribute Fix"

**Files Implementing:**
- `orchestration/mechanisms/consciousness_engine_v2.py`
- `orchestration/adapters/api/control_api.py`

**Cypher Formation:**

```cypher
// Create Task node
MERGE (t:Task {id: 'persistence_energy_fix'})
  SET t.title = 'Persistence Operational - Energy Attribute Bug Fix',
      t.description = 'Fixed wrong attribute name (energy_runtime → E) and ID format mismatch in persistence',
      t.status = 'completed',
      t.priority = 'critical',
      t.completed_at = datetime('2025-10-25T10:45:00Z')

// File already exists (consciousness_engine_v2.py)
MERGE (f1:File {name: 'c:\\users\\reyno\\mind-protocol\\orchestration\\mechanisms\\consciousness_engine_v2.py'})

// Create IMPLEMENTS link
MATCH (f1:File {name: 'c:\\users\\reyno\\mind-protocol\\orchestration\\mechanisms\\consciousness_engine_v2.py'})
MATCH (t:Task {id: 'persistence_energy_fix'})
CREATE (f1)-[:IMPLEMENTS {
  detected_by: 'sync_md_parser',
  task_section: '2025-10-25 10:45 - Victor',
  anchor_text: 'Bug #1 - Wrong attribute name (Lines 2086, 2147) - Changed to float(node.E)',
  confidence_reason: 'Explicit line numbers + bug fix description',
  energy: 0.90,
  confidence: 0.99,
  formation_trigger: 'sync_md_parser',
  goal: 'Links engine file to critical persistence fix',
  mindstate: 'Parsing SYNC.md for bug fix connections',
  valid_at: timestamp(),
  created_at: timestamp()
}]->(t)
```

---

## Formation Logic Pattern

**Parser Implementation (sync_md_parser.py):**

```python
import re
from pathlib import Path
from typing import List, Dict, Tuple

def parse_sync_md_for_implements(sync_md_path: str) -> List[Dict]:
    """
    Parse SYNC.md for file mentions and create IMPLEMENTS link formations.

    Returns list of dicts ready for Cypher formation.
    """
    formations = []

    with open(sync_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into sections by "##" headers
    sections = re.split(r'^## ', content, flags=re.MULTILINE)

    for section in sections[1:]:  # Skip preamble
        # Extract metadata from header
        header_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}) - (\w+): (.+?)$', section.split('\n')[0])
        if not header_match:
            continue

        timestamp, author, task_title = header_match.groups()

        # Extract file paths (common patterns)
        file_patterns = [
            r'`([^`]+\.(?:py|ts|tsx|md|yaml|json))`',  # Backtick paths
            r'(?:File|Location|Modified):\s*([^\s]+\.(?:py|ts|tsx|md|yaml|json))',  # "File: path"
            r'([a-z_/\\]+\.(?:py|ts|tsx|md|yaml|json))',  # Bare paths
        ]

        found_files = []
        for pattern in file_patterns:
            found_files.extend(re.findall(pattern, section))

        # Deduplicate and normalize paths
        found_files = list(set(found_files))

        # Extract anchor text (first sentence mentioning the file or task)
        lines = section.split('\n')

        for file_path in found_files:
            # Find best anchor text (line mentioning this file)
            anchor_text = None
            for line in lines:
                if file_path in line or Path(file_path).name in line:
                    anchor_text = line.strip('- ✅❌🔴⏳▶').strip()
                    break

            if not anchor_text:
                anchor_text = task_title

            # Determine confidence based on context
            confidence = 0.9 if '✅' in section else 0.7

            # Create formation
            formations.append({
                'file_path': normalize_path(file_path),
                'task_id': task_title.lower().replace(' ', '_').replace(':', '').replace('—', ''),
                'task_title': task_title,
                'task_section': f'{timestamp} - {author}',
                'anchor_text': anchor_text[:200],  # Truncate if too long
                'confidence': confidence,
                'detected_by': 'sync_md_parser'
            })

    return formations

def normalize_path(path: str) -> str:
    """Normalize to canonical lowercase absolute path."""
    # Convert relative to absolute
    if not Path(path).is_absolute():
        base = Path('/home/mind-protocol/mindprotocol')
        full_path = base / path
    else:
        full_path = Path(path)

    # Lowercase for canonical key
    return str(full_path).lower().replace('/', '\\\\')
```

---

## Query Validation: Prove the Loop

**Test Query 1: Show all files implementing TRACK B v1.2**

```cypher
MATCH (f:File)-[i:IMPLEMENTS]->(t:Task {id: 'track_b_v1_2_production_hardening'})
RETURN f.metadata.rel_path, i.anchor_text, i.confidence
ORDER BY i.confidence DESC
```

**Expected Result:**
```
docs/specs/v2/ops_and_viz/lv2_file_process_telemetry.md | TRACK B specification updated... | 0.95
docs/specs/v2/ops_and_viz/ownership_raci_model.md | Ownership & RACI model created... | 0.95
```

---

**Test Query 2: Show all tasks implemented by consciousness_engine_v2.py**

```cypher
MATCH (f:File {name: 'c:\\\\users\\\\reyno\\\\mind-protocol\\\\orchestration\\\\mechanisms\\\\consciousness_engine_v2.py'})
MATCH (f)-[i:IMPLEMENTS]->(t:Task)
RETURN t.title, t.status, i.task_section, i.anchor_text
ORDER BY t.completed_at DESC
```

**Expected Result:**
```
PR-C Dashboard Events... | completed | 2025-10-25 15:05 - Felix | PR-C implementation complete...
Persistence Operational... | completed | 2025-10-25 10:45 - Victor | Bug #1 - Wrong attribute...
```

---

**Test Query 3: Find orphaned files (no IMPLEMENTS links)**

```cypher
MATCH (f:File)
WHERE f.metadata.lang IN ['python', 'typescript']
  AND NOT (f)-[:IMPLEMENTS]->(:Task)
RETURN f.metadata.rel_path, f.metadata.mtime
ORDER BY f.metadata.mtime DESC
LIMIT 20
```

**Purpose:** Identify code files that aren't documented in SYNC.md or haven't been linked to tasks.

---

## Implementation Status

**Current:** Sample Cypher queries provided, parser pattern documented

**Next:**
1. Implement sync_md_parser.py with formation logic
2. Run parser on SYNC.md to create real IMPLEMENTS links
3. Validate queries return expected results
4. Integrate into lv2_expander.py for continuous link formation

**Integration Point:** When SYNC.md updates, trigger parser → form IMPLEMENTS links → update graph

---

**End of Sample Document**

*Luca Vellumhand - Substrate Architect*
