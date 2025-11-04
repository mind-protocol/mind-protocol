#!/usr/bin/env python3
"""
Replace hardcoded mind-protocol_* graph names with resolver calls

Replaces:
  "mind-protocol_felix" → graph_names.resolver.citizen("felix")
  "mind-protocol" → graph_names.resolver.org_base()
  "ecosystem" → graph_names.resolver.collective()  # or keep as-is
  "protocol" → graph_names.resolver.protocol()
"""

import re
from pathlib import Path

# Citizen names to replace
CITIZENS = ["ada", "atlas", "felix", "iris", "luca", "victor"]

# Files to update with their specific patterns
FILES_TO_UPDATE = {
    "tools/migrate_to_universal_types.py": {
        "import_add": "from orchestration.config.graph_names import resolver",
        "replacements": [
            (r'"mind-protocol_(ada|atlas|felix|iris|luca|victor)"', r'resolver.citizen("\1")'),
        ]
    },
    "tools/doc_ingestion/ask.py": {
        "import_add": "from orchestration.config.graph_names import resolver",
        "replacements": [
            (r"'mind-protocol'", "resolver.org_base()"),
        ]
    },
    "tools/doc_ingestion/graph.py": {
        "import_add": "from orchestration.config.graph_names import resolver",
        "replacements": [
            (r'"mind-protocol"', 'resolver.org_base()'),
        ]
    },
    "tools/doc_ingestion/config.py": {
        "import_add": "from orchestration.config.graph_names import resolver",
        "replacements": [
            (r'"mind-protocol"', 'resolver.org_base()'),
        ]
    },
    "tools/fix_naming_standardization.py": {
        "import_add": "from orchestration.config.graph_names import resolver",
        "replacements": [
            (r'"mind-protocol_(ada|atlas|felix|iris|luca|victor)"', r'resolver.citizen("\1")'),
        ]
    },
    "tools/mp_lint/cli.py": {
        "import_add": "from orchestration.config.graph_names import resolver",
        "replacements": [
            (r'"mind-protocol_(ada|atlas|felix|iris|luca|victor)"', r'resolver.citizen("\1")'),
        ]
    },
    "tools/check_l4_subsystems.py": {
        "import_add": "from orchestration.config.graph_names import resolver",
        "replacements": [
            (r'"mind-protocol_(ada|atlas|felix|iris|luca|victor)"', r'resolver.citizen("\1")'),
        ]
    },
}

def add_import(content, import_line):
    """Add import if not already present."""
    if import_line in content:
        return content, False

    # Find last import line
    lines = content.split('\n')
    last_import_idx = -1
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            last_import_idx = i

    if last_import_idx >= 0:
        lines.insert(last_import_idx + 1, import_line)
        return '\n'.join(lines), True
    else:
        # Add after shebang/docstring
        for i, line in enumerate(lines):
            if i > 5:  # Give up after a few lines
                break
            if not line.startswith('#') and not line.startswith('"""') and not line.startswith("'''"):
                lines.insert(i, import_line)
                return '\n'.join(lines), True
        return content, False

def update_file(filepath, config):
    """Update a file with graph name resolver calls."""
    full_path = Path(filepath)

    if not full_path.exists():
        print(f"⊘ Skip: {filepath} (not found)")
        return False

    try:
        with open(full_path, 'r') as f:
            content = f.read()

        original_content = content

        # Add import if needed
        if "import_add" in config:
            content, import_added = add_import(content, config["import_add"])

        # Apply replacements
        changes = 0
        for pattern, replacement in config["replacements"]:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                changes += 1
            content = new_content

        if content != original_content:
            with open(full_path, 'w') as f:
                f.write(content)
            print(f"✓ Updated: {filepath} ({changes} replacements)")
            return True
        else:
            print(f"⊘ No changes: {filepath}")
            return False

    except Exception as e:
        print(f"✗ Error: {filepath} → {e}")
        return False

def main():
    print("🔧 Replacing Hardcoded Graph Names with Resolver Calls")
    print("=" * 70)
    print()

    updated_count = 0

    for filepath, config in FILES_TO_UPDATE.items():
        if update_file(filepath, config):
            updated_count += 1

    print()
    print("=" * 70)
    print(f"✅ Updated {updated_count}/{len(FILES_TO_UPDATE)} files")
    print()
    print("Replacements:")
    print('  "mind-protocol_felix" → resolver.citizen("felix")')
    print('  "mind-protocol" → resolver.org_base()')
    print()
    print("Import added:")
    print('  from orchestration.config.graph_names import resolver')

if __name__ == "__main__":
    main()
