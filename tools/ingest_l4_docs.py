#!/usr/bin/env python3
"""
L4 Documentation Ingestion Script

Ingests L4 law documents as U4_Knowledge_Object nodes with:
- Rich metadata (status, version, hash, owner)
- Implementation status tracking
- DOCUMENTS relationships to L4_Governance_Policy nodes
- IMPLEMENTS relationships from code artifacts
"""

import os
import re
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

# Try to import frontmatter, graceful fallback
try:
    import frontmatter
    HAS_FRONTMATTER = True
except ImportError:
    HAS_FRONTMATTER = False
    print("Warning: python-frontmatter not installed. Install with: pip install python-frontmatter")

from falkordb import FalkorDB

# Connect to FalkorDB
db = FalkorDB(host='localhost', port=6379)
graph = db.select_graph('protocol')  # L4 lives in protocol graph

L4_DOCS_DIR = Path(__file__).parent.parent / "docs" / "L4-law"


def compute_hash(file_path: Path) -> str:
    """Compute SHA-256 hash of file content"""
    return hashlib.sha256(file_path.read_bytes()).hexdigest()


def parse_markdown_doc(file_path: Path) -> Dict:
    """Parse markdown document with frontmatter and extract metadata"""

    content = file_path.read_text(encoding='utf-8')

    # Try to parse frontmatter (YAML between --- delimiters)
    metadata = {}
    body = content

    if HAS_FRONTMATTER:
        try:
            post = frontmatter.loads(content)
            metadata = dict(post.metadata)
            body = post.content
        except:
            pass  # No frontmatter or parse error, use defaults

    # Extract title (first # heading or filename)
    title_match = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
    else:
        title = file_path.stem.replace('_', ' ').replace('-', ' ').title()

    # Extract description (first paragraph after title)
    desc_match = re.search(r'^#\s+.+?\n\n(.+?)(?:\n\n|\n#)', body, re.MULTILINE | re.DOTALL)
    description = desc_match.group(1).strip()[:500] if desc_match else ""

    # Determine document type from filename/content
    filename_lower = file_path.name.lower()
    if filename_lower.startswith('law-'):
        ko_type = 'policy'
    elif 'spec' in filename_lower or 'specification' in filename_lower:
        ko_type = 'spec'
    elif 'schema' in filename_lower:
        ko_type = 'reference'
    elif 'guide' in filename_lower:
        ko_type = 'guide'
    else:
        ko_type = 'reference'

    # Extract version (from filename like LAW-002 or v1.0)
    version_match = re.search(r'v?(\d+\.\d+)', file_path.stem)
    if version_match:
        version = version_match.group(1)
    else:
        # Extract LAW-NNN number as version
        law_match = re.search(r'LAW-(\d+)', file_path.stem)
        version = law_match.group(1) if law_match else '1.0'

    # Determine status from content
    status = 'active'
    if 'DRAFT' in body[:500].upper() or metadata.get('status') == 'draft':
        status = 'draft'
    elif 'DEPRECATED' in body[:500].upper() or metadata.get('status') == 'deprecated':
        status = 'deprecated'

    # Extract author/owner
    author_match = re.search(r'\*\*Author[s]?:\*\*\s*(.+?)(?:\n|\*\*)', body)
    owner = author_match.group(1).strip() if author_match else metadata.get('author', 'Mind Protocol')

    return {
        'name': title,
        'description': description,
        'ko_type': ko_type,
        'version': version,
        'status': status,
        'owner': owner,
        'file_path': str(file_path.relative_to(file_path.parent.parent.parent)),
        'hash': compute_hash(file_path),
        'uri': f"l4://law/{file_path.stem}",
        'metadata': metadata,
        'body': body
    }


def determine_implementation_status(doc_data: Dict, body: str) -> Tuple[str, List[str], str]:
    """
    Determine implementation status by searching for code references

    Returns: (status, implementing_files, notes)
    """

    # Look for implementation references in document
    impl_patterns = [
        r'(?:implemented|implements|implementation)\s+(?:in|by|at)\s+`([^`]+)`',
        r'`([^`]+\.(?:py|ts|js|sql))`',
        r'\[([^\]]+\.(?:py|ts|js|sql))\]',
    ]

    implementing_files = []
    for pattern in impl_patterns:
        matches = re.findall(pattern, body, re.IGNORECASE)
        implementing_files.extend(matches)

    # Remove duplicates
    implementing_files = list(set(implementing_files))

    # Check if files actually exist
    existing_files = []
    for file_ref in implementing_files:
        # Try to find file in codebase
        potential_paths = [
            Path(file_ref),
            Path('orchestration') / file_ref,
            Path('services') / file_ref,
            Path('app') / file_ref,
        ]

        for p in potential_paths:
            if p.exists():
                existing_files.append(str(p))
                break

    # Determine status
    if len(existing_files) > 0:
        status = 'implemented'
        notes = f"Implemented in {len(existing_files)} file(s)"
    elif len(implementing_files) > 0:
        status = 'partially_implemented'
        notes = f"References {len(implementing_files)} files (not all verified)"
    elif 'DRAFT' in body[:500].upper():
        status = 'not_implemented'
        notes = "Draft specification - not yet implemented"
    else:
        status = 'unknown'
        notes = "Implementation status unclear"

    return status, existing_files, notes


def create_knowledge_object_node(doc_data: Dict, impl_status: str, impl_notes: str) -> str:
    """Create U4_Knowledge_Object node in FalkorDB"""

    now = datetime.now(timezone.utc).isoformat()

    # Generate unique ko_id
    ko_id = f"l4_law_{doc_data['file_path'].replace('/', '_').replace('.md', '')}"

    cypher = """
    MERGE (ko:U4_Knowledge_Object {ko_id: $ko_id})
    SET ko.name = $name,
        ko.description = $description,
        ko.detailed_description = $detailed_description,
        ko.type_name = 'U4_Knowledge_Object',
        ko.ko_type = $ko_type,
        ko.level = 'L4',
        ko.scope_ref = 'protocol',
        ko.uri = $uri,
        ko.hash = $hash,
        ko.owner = $owner,
        ko.status = $status,
        ko.version = $version,
        ko.file_path = $file_path,
        ko.implementation_status = $impl_status,
        ko.implementation_notes = $impl_notes,
        ko.created_at = $now,
        ko.updated_at = $now,
        ko.valid_from = $now,
        ko.valid_to = NULL,
        ko.visibility = 'public',
        ko.policy_ref = 'l4://law/governance',
        ko.proof_uri = 'l4://proofs/schema_registry',
        ko.commitments = [],
        ko.created_by = 'l4_docs_ingestion_script',
        ko.substrate = 'organizational'
    RETURN ko.ko_id
    """

    params = {
        'ko_id': ko_id,
        'name': doc_data['name'],
        'description': doc_data['description'][:500],
        'detailed_description': doc_data['description'],
        'ko_type': doc_data['ko_type'],
        'uri': doc_data['uri'],
        'hash': doc_data['hash'],
        'owner': doc_data['owner'],
        'status': doc_data['status'],
        'version': doc_data['version'],
        'file_path': doc_data['file_path'],
        'impl_status': impl_status,
        'impl_notes': impl_notes,
        'now': now
    }

    result = graph.query(cypher, params)
    print(f"  ✅ Created node: {ko_id}")

    return ko_id


def create_documents_relationships(ko_id: str, doc_data: Dict):
    """Create DOCUMENTS relationships to L4 policy/schema nodes"""

    # Determine what this document DOCUMENTS
    file_stem = Path(doc_data['file_path']).stem.lower()

    relationships = []

    # LAW documents → L4_Governance_Policy
    if file_stem.startswith('law-'):
        law_num_match = re.search(r'law-(\d+)', file_stem)
        if law_num_match:
            law_num = law_num_match.group(1)
            policy_id = f"LAW-{law_num}"
            relationships.append(('L4_Governance_Policy', policy_id))

    # Schema docs → Schema nodes
    if 'schema' in file_stem:
        if 'registry' in file_stem:
            relationships.append(('U4_Subentity', 'schema_registry'))
        if 'extensions' in file_stem:
            relationships.append(('L4_Schema_Bundle', 'privacy_extensions'))

    # Subsystem docs → U4_Subentity
    if 'subsystem' in file_stem:
        relationships.append(('U4_Subentity', 'l4_subsystems'))

    # Create relationships
    now = datetime.now(timezone.utc).isoformat()

    for target_type, target_id in relationships:
        cypher = f"""
        MATCH (ko:U4_Knowledge_Object {{ko_id: $ko_id}})
        MATCH (target:{target_type})
        WHERE target.name = $target_id
           OR target.policy_id = $target_id
           OR target.ko_id = $target_id
        MERGE (ko)-[r:U4_DOCUMENTS]->(target)
        SET r.doc_role = $doc_role,
            r.confidence = 1.0,
            r.energy = 0.8,
            r.forming_mindstate = 'documentation',
            r.goal = 'document_specification',
            r.created_at = $now,
            r.updated_at = $now,
            r.valid_from = $now,
            r.valid_to = NULL,
            r.visibility = 'public',
            r.commitments = [],
            r.created_by = 'l4_docs_ingestion_script',
            r.substrate = 'organizational'
        RETURN count(r)
        """

        params = {
            'ko_id': ko_id,
            'target_id': target_id,
            'doc_role': doc_data['ko_type'],
            'now': now
        }

        try:
            result = graph.query(cypher, params)
            if result.result_set and result.result_set[0][0] > 0:
                print(f"    → DOCUMENTS: {target_type}.{target_id}")
        except Exception as e:
            print(f"    ⚠ Could not create DOCUMENTS → {target_type}.{target_id}: {e}")


def create_implements_relationships(ko_id: str, implementing_files: List[str]):
    """Create IMPLEMENTS relationships from code artifacts to this doc"""

    if not implementing_files:
        return

    now = datetime.now(timezone.utc).isoformat()

    for file_path in implementing_files:
        cypher = """
        MATCH (ko:U4_Knowledge_Object {ko_id: $ko_id})
        MATCH (code:U4_Code_Artifact)
        WHERE code.path = $file_path OR code.path ENDS WITH $file_path
        MERGE (code)-[r:U4_IMPLEMENTS]->(ko)
        SET r.confidence = 0.9,
            r.energy = 0.7,
            r.forming_mindstate = 'implementation',
            r.goal = 'implement_specification',
            r.evidence_rules_passed = [],
            r.last_lint_ts = $now,
            r.created_at = $now,
            r.updated_at = $now,
            r.valid_from = $now,
            r.valid_to = NULL,
            r.visibility = 'public',
            r.commitments = [],
            r.created_by = 'l4_docs_ingestion_script',
            r.substrate = 'organizational'
        RETURN count(r)
        """

        params = {
            'ko_id': ko_id,
            'file_path': file_path,
            'now': now
        }

        try:
            result = graph.query(cypher, params)
            if result.result_set and result.result_set[0][0] > 0:
                print(f"    ← IMPLEMENTS: {file_path}")
        except Exception as e:
            print(f"    ⚠ Could not create IMPLEMENTS from {file_path}: {e}")


def ingest_l4_documentation():
    """Main ingestion function"""

    print("=" * 80)
    print("L4 Documentation Ingestion")
    print("=" * 80)
    print(f"\nScanning: {L4_DOCS_DIR}\n")

    # Find all markdown files
    md_files = sorted(L4_DOCS_DIR.glob("*.md"))

    if not md_files:
        print("❌ No markdown files found in", L4_DOCS_DIR)
        return

    print(f"Found {len(md_files)} L4 documents to ingest\n")

    stats = {
        'total': len(md_files),
        'ingested': 0,
        'implemented': 0,
        'partial': 0,
        'not_implemented': 0,
        'errors': 0
    }

    for md_file in md_files:
        try:
            print(f"\n📄 {md_file.name}")
            print("-" * 80)

            # Parse document
            doc_data = parse_markdown_doc(md_file)
            print(f"  Type: {doc_data['ko_type']}")
            print(f"  Status: {doc_data['status']}")
            print(f"  Version: {doc_data['version']}")
            print(f"  Owner: {doc_data['owner']}")

            # Determine implementation status
            impl_status, impl_files, impl_notes = determine_implementation_status(
                doc_data, doc_data['body']
            )
            print(f"  Implementation: {impl_status}")
            print(f"  Notes: {impl_notes}")

            # Track stats
            if impl_status == 'implemented':
                stats['implemented'] += 1
            elif impl_status == 'partially_implemented':
                stats['partial'] += 1
            else:
                stats['not_implemented'] += 1

            # Create node
            ko_id = create_knowledge_object_node(doc_data, impl_status, impl_notes)

            # Create relationships
            create_documents_relationships(ko_id, doc_data)
            create_implements_relationships(ko_id, impl_files)

            stats['ingested'] += 1

        except Exception as e:
            print(f"  ❌ Error: {e}")
            stats['errors'] += 1
            import traceback
            traceback.print_exc()

    # Print summary
    print("\n" + "=" * 80)
    print("INGESTION SUMMARY")
    print("=" * 80)
    print(f"Total documents: {stats['total']}")
    print(f"Successfully ingested: {stats['ingested']}")
    print(f"Errors: {stats['errors']}")
    print(f"\nImplementation Status:")
    print(f"  ✅ Implemented: {stats['implemented']}")
    print(f"  🟡 Partial: {stats['partial']}")
    print(f"  ⭕ Not implemented: {stats['not_implemented']}")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    ingest_l4_documentation()
