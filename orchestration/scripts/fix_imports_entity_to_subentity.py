#!/usr/bin/env python3
"""
Auto-fix imports after entity→subentity file renames
Run after file renames complete
"""
import os
import re
from pathlib import Path

RENAMES = {
    "entity_bootstrap": "subentity_bootstrap",
    "entity_post_bootstrap": "subentity_post_bootstrap", 
    "entity_creation": "subentity_creation",
    "entity_persistence": "subentity_persistence"
}

def fix_imports_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Fix: from mechanisms.subentity_bootstrap import ...
    for old, new in RENAMES.items():
        content = re.sub(
            rf'from\s+mechanisms\.{old}\s+import',
            f'from mechanisms.{new} import',
            content
        )
        content = re.sub(
            rf'from\s+orchestration\.mechanisms\.{old}\s+import',
            f'from orchestration.mechanisms.{new} import',
            content
        )
        content = re.sub(
            rf'import\s+mechanisms\.{old}',
            f'import mechanisms.{new}',
            content
        )
        content = re.sub(
            rf'import\s+orchestration\.mechanisms\.{old}',
            f'import orchestration.mechanisms.{new}',
            content
        )
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    orchestration = Path(__file__).parent.parent
    fixed_count = 0
    files_checked = 0
    
    print("="*70)
    print("FIXING IMPORTS: entity_* → subentity_*")
    print("="*70)
    print()
    
    for pyfile in orchestration.rglob("*.py"):
        files_checked += 1
        if fix_imports_in_file(pyfile):
            print(f"Fixed: {pyfile.relative_to(orchestration)}")
            fixed_count += 1
    
    print()
    print(f"Total files checked: {files_checked}")
    print(f"Total files fixed: {fixed_count}")
    print("="*70)

if __name__ == "__main__":
    main()
