"""
Corpus Processing Orchestrator

Main orchestrator for documentation ingestion pipeline. Coordinates all components:
- Manifest reading and state tracking (ingest_docs.py)
- Markdown chunking (md_chunker.py)
- Semantic processing (map_and_link.py - Felix's intelligence layer)
- Graph writing (graph.py)
- Structural linting (lint_graph.py)

Supports checkpoint/resume for fault-tolerant processing.

Author: Atlas (Infrastructure Engineer)
Date: 2025-10-29
Spec: docs/SPEC DOC INPUT.md
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add project root to Python path for orchestration imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.logger import setup_logger, log_section, log_table, log_progress, Colors
from config import get_config, DocIngestionConfig
from graph import GraphWrapper
from md_chunker import MarkdownChunker
from ingest_docs import IngestionStateManager, ProcessingStatus
from lint_graph import GraphLinter

logger = setup_logger(__name__)

# Felix's semantic intelligence layer
try:
    from map_and_link import process_chunks
    MAP_AND_LINK_AVAILABLE = True
except ImportError as e:
    MAP_AND_LINK_AVAILABLE = False
    logger.warning(f"map_and_link.py import failed: {e}")


class CorpusProcessor:
    """
    Main orchestrator for corpus processing.

    Coordinates all pipeline components with checkpoint/resume support.
    """

    def __init__(self, config: DocIngestionConfig):
        """
        Initialize processor.

        Args:
            config: Configuration object
        """
        self.config = config
        self.state_manager = IngestionStateManager(config.processing.state_db_path)
        self.graph = GraphWrapper(
            graph_name=config.falkordb.graph_name,
            host=config.falkordb.host,
            port=config.falkordb.port
        )
        self.chunker = MarkdownChunker(
            target_tokens=config.chunk.target_tokens,
            max_tokens=config.chunk.max_tokens
        )

        # Statistics
        self.stats = {
            'files_processed': 0,
            'files_failed': 0,
            'total_chunks': 0,
            'total_nodes': 0,
            'total_links': 0,
            'total_qa_tasks': 0
        }

    def _log_event(self, event_type: str, payload: Dict[str, Any]):
        """Emit JSONL event log."""
        log_line = {
            "type": event_type,
            **payload,
            "timestamp": datetime.utcnow().isoformat()
        }
        print(f"@@ {json.dumps(log_line)}", flush=True)

    def _deduplicate_nodes(self, file_path: str) -> int:
        """
        Find and merge duplicate nodes from a file using semantic similarity.

        Args:
            file_path: Source file path to check for duplicates

        Returns:
            Number of duplicate pairs found and linked
        """
        from embedding_service import EmbeddingService

        try:
            embedding_service = EmbeddingService(config=self.config)

            # Query all nodes from this file
            query = """
            MATCH (n)
            WHERE n.source_file = $source_file
            RETURN
                n.id AS id,
                labels(n) AS labels,
                n.name AS name,
                n.description AS description
            ORDER BY labels(n)[0], n.id
            """

            result = self.graph.graph.query(query, {'source_file': file_path})

            nodes_by_type = {}
            for record in result.result_set:
                node_id = record[0]
                labels = record[1]
                name = record[2]
                description = record[3]

                node_type = labels[0] if labels else None
                if not node_type:
                    continue

                if node_type not in nodes_by_type:
                    nodes_by_type[node_type] = []

                nodes_by_type[node_type].append({
                    'id': node_id,
                    'name': name,
                    'description': description,
                    'text_for_embedding': f"{name}. {description}"
                })

            # Find duplicates within each type
            duplicate_pairs = []
            similarity_threshold = 0.85

            for node_type, nodes in nodes_by_type.items():
                if len(nodes) < 2:
                    continue  # No duplicates possible with < 2 nodes

                # Compute embeddings for all nodes of this type
                for node in nodes:
                    node['embedding'] = embedding_service.embed(node['text_for_embedding'])

                # Compare all pairs
                for i in range(len(nodes)):
                    for j in range(i + 1, len(nodes)):
                        node_a = nodes[i]
                        node_b = nodes[j]

                        # Compute cosine similarity
                        import numpy as np
                        embedding_a = np.array(node_a['embedding'])
                        embedding_b = np.array(node_b['embedding'])

                        similarity = np.dot(embedding_a, embedding_b) / (
                            np.linalg.norm(embedding_a) * np.linalg.norm(embedding_b)
                        )

                        if similarity >= similarity_threshold:
                            duplicate_pairs.append({
                                'node_a_id': node_a['id'],
                                'node_b_id': node_b['id'],
                                'node_type': node_type,
                                'similarity': float(similarity),
                                'node_a_name': node_a['name'],
                                'node_b_name': node_b['name']
                            })

            # Create SAME_AS edges for duplicate pairs
            for pair in duplicate_pairs:
                # Create bidirectional SAME_AS edge
                edge_result = self.graph.ensure_edge(
                    edge_type='SAME_AS',
                    source_id=pair['node_a_id'],
                    target_id=pair['node_b_id'],
                    meta={
                        'similarity': pair['similarity'],
                        'detected_by': 'deduplication_pass',
                        'detection_method': 'semantic_similarity',
                        'threshold': similarity_threshold
                    },
                    confidence=pair['similarity'],
                    status='CONFIRMED'
                )

                if edge_result['confirmed']:
                    self._log_event("duplicate_nodes_linked", {
                        "node_a_id": pair['node_a_id'],
                        "node_b_id": pair['node_b_id'],
                        "node_type": pair['node_type'],
                        "similarity": pair['similarity'],
                        "file": file_path
                    })

                    print(f"  ⚠️  Duplicate detected: {pair['node_a_name']} ≈ {pair['node_b_name']}", flush=True)
                    print(f"      Similarity: {pair['similarity']:.3f}, Type: {pair['node_type']}", flush=True)

            return len(duplicate_pairs)

        except Exception as e:
            print(f"⚠️  Deduplication failed: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return 0

    def _run_qa_check(self, recent_files: list) -> Dict[str, Any]:
        """
        Run QA checks on recently processed files.

        Args:
            recent_files: List of file paths to check

        Returns:
            QA results with quality scores and issues found
        """
        print(f"\n{'='*60}")
        print(f"🔍 RUNNING QA CHECK ON {len(recent_files)} RECENT FILES")
        print(f"{'='*60}\n")

        qa_results = {
            'files_checked': len(recent_files),
            'total_nodes': 0,
            'total_edges': 0,
            'incomplete_nodes_rejected': 0,
            'duplicates_found': 0,
            'low_confidence_edges': 0,
            'orphaned_nodes': 0,
            'issues': [],
            'quality_score': 0.0
        }

        for file_path in recent_files:
            # Query nodes from this file
            query_nodes = """
            MATCH (n)
            WHERE n.source_file = $source_file
            RETURN count(n) AS node_count
            """
            result = self.graph.graph.query(query_nodes, {'source_file': file_path})
            node_count = result.result_set[0][0] if result.result_set else 0
            qa_results['total_nodes'] += node_count

            # Query edges from this file (source or target from this file)
            query_edges = """
            MATCH (source)-[r]->(target)
            WHERE source.source_file = $source_file OR target.source_file = $source_file
            RETURN count(r) AS edge_count, avg(r.confidence) AS avg_confidence
            """
            result = self.graph.graph.query(query_edges, {'source_file': file_path})
            if result.result_set:
                edge_count = result.result_set[0][0]
                avg_confidence = result.result_set[0][1]
                qa_results['total_edges'] += edge_count

                # Check for low confidence edges
                if avg_confidence and avg_confidence < 0.7:
                    qa_results['low_confidence_edges'] += 1
                    qa_results['issues'].append({
                        'file': file_path,
                        'type': 'low_confidence',
                        'severity': 'warning',
                        'message': f'Average edge confidence: {avg_confidence:.2f} (below 0.7 threshold)'
                    })

            # Check for duplicates (SAME_AS edges)
            query_duplicates = """
            MATCH (a)-[r:SAME_AS]->(b)
            WHERE a.source_file = $source_file
            RETURN count(r) AS duplicate_count
            """
            result = self.graph.graph.query(query_duplicates, {'source_file': file_path})
            duplicate_count = result.result_set[0][0] if result.result_set else 0
            qa_results['duplicates_found'] += duplicate_count

            # Check for orphaned nodes (nodes with no edges)
            query_orphans = """
            MATCH (n)
            WHERE n.source_file = $source_file
            AND NOT (n)-[]-()
            RETURN count(n) AS orphan_count
            """
            result = self.graph.graph.query(query_orphans, {'source_file': file_path})
            orphan_count = result.result_set[0][0] if result.result_set else 0
            qa_results['orphaned_nodes'] += orphan_count

            if orphan_count > 0:
                qa_results['issues'].append({
                    'file': file_path,
                    'type': 'orphaned_nodes',
                    'severity': 'warning',
                    'message': f'{orphan_count} nodes have no edges (isolated)'
                })

        # Calculate quality score (0-100)
        score = 100.0

        # Penalize for issues
        if qa_results['duplicates_found'] > 0:
            score -= min(10, qa_results['duplicates_found'] * 2)  # -2 per duplicate, max -10

        if qa_results['low_confidence_edges'] > 0:
            score -= min(15, qa_results['low_confidence_edges'] * 5)  # -5 per low conf file, max -15

        if qa_results['orphaned_nodes'] > 0:
            orphan_ratio = qa_results['orphaned_nodes'] / max(1, qa_results['total_nodes'])
            score -= min(20, orphan_ratio * 50)  # Up to -20 based on orphan ratio

        qa_results['quality_score'] = max(0, score)

        # Print QA summary
        print(f"QA RESULTS:")
        print(f"  Total nodes: {qa_results['total_nodes']}")
        print(f"  Total edges: {qa_results['total_edges']}")
        print(f"  Duplicates found: {qa_results['duplicates_found']}")
        print(f"  Orphaned nodes: {qa_results['orphaned_nodes']}")
        print(f"  Quality score: {qa_results['quality_score']:.1f}/100")

        if qa_results['issues']:
            print(f"\n  Issues found ({len(qa_results['issues'])}):")
            for issue in qa_results['issues']:
                severity_icon = '⚠️' if issue['severity'] == 'warning' else '❌'
                print(f"    {severity_icon} [{issue['type']}] {issue['message']}")
        else:
            print(f"  ✅ No issues found")

        print(f"\n{'='*60}\n")

        # Log QA event
        self._log_event("qa_check_complete", qa_results)

        return qa_results

    def sync_manifest(self, manifest_path: str) -> Dict[str, int]:
        """
        Sync manifest with database state.

        Args:
            manifest_path: Path to manifest.json

        Returns:
            Sync statistics
        """
        self._log_event("manifest_sync_start", {"manifest": manifest_path})

        stats = self.state_manager.sync_manifest(manifest_path)

        self._log_event("manifest_sync_complete", stats)
        return stats

    def process_file(self, file_path: str) -> bool:
        """
        Process a single file through the pipeline.

        Args:
            file_path: Path to markdown file

        Returns:
            True if successful, False if failed
        """
        self._log_event("file_processing_start", {"file": file_path})

        try:
            # Mark as processing
            self.state_manager.mark_processing(file_path)

            # Resolve file path relative to project root
            resolved_path = Path(file_path)
            if not resolved_path.is_absolute():
                resolved_path = PROJECT_ROOT / resolved_path

            # Read file content
            with open(str(resolved_path), 'r', encoding='utf-8') as f:
                content = f.read()

            # Chunk file
            self._log_event("chunking_start", {"file": file_path})
            chunks = self.chunker.chunk_file(content)
            chunk_stats = self.chunker.chunk_stats(chunks)

            self._log_event("chunking_complete", {
                "file": file_path,
                "chunk_count": len(chunks),
                "avg_tokens": chunk_stats['avg_tokens']
            })

            # Process chunks via Felix's map_and_link
            if not MAP_AND_LINK_AVAILABLE:
                raise RuntimeError("map_and_link.py not available")

            self._log_event("semantic_processing_start", {
                "file": file_path,
                "chunk_count": len(chunks)
            })

            # Prepare inputs for map_and_link
            # Generate chunk IDs from file path + index
            filename = resolved_path.name
            # Get file modification time
            last_updated = datetime.fromtimestamp(os.path.getmtime(str(resolved_path))).isoformat()

            inputs = {
                "chunks": [
                    {
                        "chunk_id": f"{filename}_{c.chunk_index}",
                        "text": c.content,
                        "index": c.chunk_index,
                        "token_count": c.token_count,
                        "document_path": file_path,
                        "last_updated": last_updated
                    }
                    for c in chunks
                ],
                "graph": self.graph,
                "seed_ids": []  # Could extract seed IDs from file metadata
            }

            # Prepare config thresholds
            thresholds = {
                "MIN_CONF_PROPOSE_LINK": self.config.confidence.propose_link,
                "MIN_CONF_AUTOCONFIRM": self.config.confidence.autoconfirm,
                "MIN_CONF_CREATE_TASK": self.config.confidence.create_task
            }

            # Call Felix's semantic processing
            result = process_chunks(inputs, thresholds)

            self._log_event("semantic_processing_complete", {
                "file": file_path,
                "theme": result.get('theme'),
                "node_count": len(result.get('node_proposals', [])),
                "link_count": len(result.get('edges', [])),
                "task_count": len(result.get('tasks', []))
            })

            # Write node proposals to graph
            node_count = 0
            for idx, node_proposal in enumerate(result.get('node_proposals', [])):
                # node_proposals come back hydrated with {id, type, props} from map_and_link
                node_id = node_proposal.get('id')
                node_type = node_proposal.get('type')
                properties = node_proposal.get('props', {})

                # VALIDATION: Reject incomplete nodes (name=None or description=None)
                node_name = properties.get('name')
                node_desc = properties.get('description')

                if not node_name or not node_desc:
                    self._log_event("node_proposal_rejected_incomplete", {
                        "node_id": node_id,
                        "node_type": node_type,
                        "reason": f"missing {'name' if not node_name else 'description'}",
                        "file": file_path
                    })
                    print(f"\n⚠️  Rejected incomplete node: {node_id}", flush=True)
                    print(f"    Type: {node_type}, Name: {node_name}, Description: {node_desc}", flush=True)
                    print(f"    Reason: Nodes must have both name and description\n", flush=True)
                    continue  # Skip this incomplete node

                # VALIDATION: Reject nodes with None/invalid type
                if not node_type or node_type == 'None':
                    self._log_event("node_proposal_rejected_invalid_type", {
                        "node_id": node_id,
                        "node_type": node_type,
                        "name": node_name,
                        "reason": "invalid or None type",
                        "file": file_path
                    })
                    print(f"\n⚠️  Rejected node with invalid type: {node_id}", flush=True)
                    print(f"    Type: {node_type}, Name: {node_name}", flush=True)
                    print(f"    Reason: Node type cannot be None or invalid\n", flush=True)
                    continue  # Skip this invalid node

                # Add source_file to properties
                properties['source_file'] = file_path

                node_result = self.graph.ensure_node(
                    node_type=node_type,
                    node_id=node_id,
                    properties=properties
                )

                if node_result['confirmed']:
                    node_count += 1
                    self._log_event("node_created", {
                        "node_id": node_id,
                        "node_type": node_type,
                        "file": file_path
                    })
                else:
                    self._log_event("node_creation_failed", {
                        "node_id": node_id,
                        "error": node_result.get('error'),
                        "file": file_path
                    })

            # Write edges to graph
            link_count = 0
            for edge in result.get('edges', []):
                edge_result = self.graph.ensure_edge(
                    edge_type=edge['type'],
                    source_id=edge['source'],
                    target_id=edge['target'],
                    meta=edge.get('meta', {}),
                    confidence=edge.get('confidence', 1.0),
                    status=edge.get('status', 'CONFIRMED')
                )

                if edge_result['confirmed']:
                    link_count += 1
                    self._log_event("edge_created", {
                        "edge_type": edge['type'],
                        "source": edge['source'],
                        "target": edge['target'],
                        "confidence": edge.get('confidence'),
                        "file": file_path
                    })
                else:
                    error_msg = edge_result.get('error', '')
                    self._log_event("edge_creation_failed", {
                        "edge_type": edge['type'],
                        "source": edge['source'],
                        "target": edge['target'],
                        "error": error_msg,
                        "file": file_path
                    })

                    # Auto-Resolve Missing Endpoint (ARM)
                    if "does not exist" in error_msg:
                        missing_id = None
                        other_id = None

                        if "Source node" in error_msg:
                            missing_id = edge['source']
                            other_id = edge['target']
                        elif "Target node" in error_msg:
                            missing_id = edge['target']
                            other_id = edge['source']

                        if missing_id:
                            try:
                                from arm import auto_resolve_missing_endpoint

                                arm_result = auto_resolve_missing_endpoint(
                                    graph=self.graph,
                                    missing_id=missing_id,
                                    other_id=other_id,
                                    edge_type=edge['type'],
                                    embedding_service=None  # Will create its own
                                )

                                # Log ARM candidates
                                print(f"\n⚠️  Missing node: {missing_id}", flush=True)
                                print(f"    Edge: {edge['source']} →[{edge['type']}]→ {edge['target']}", flush=True)
                                print(f"    ARM found {len(arm_result['candidates'])} candidates:", flush=True)
                                for i, cand in enumerate(arm_result['candidates'][:3], 1):
                                    print(f"      {i}. {cand['id']} (score={cand['score_combined']:.3f})", flush=True)

                                # Create QA task with ARM candidates
                                self.state_manager.create_qa_task(
                                    file_path=file_path,
                                    task_type='arm_resolve_missing_node',
                                    description=f"ARM: Missing node '{missing_id}' - {len(arm_result['candidates'])} candidates found"
                                )

                                self._log_event("arm_candidates_found", {
                                    "missing_id": missing_id,
                                    "edge_type": edge['type'],
                                    "candidates_count": len(arm_result['candidates']),
                                    "top_candidate": arm_result['candidates'][0]['id'] if arm_result['candidates'] else None,
                                    "file": file_path
                                })

                            except Exception as arm_error:
                                print(f"⚠️  ARM failed for {missing_id}: {arm_error}", flush=True)

            # Update completed edges (edges that got metadata completions in later chunks)
            completed_edges = result.get('completed_edges', [])
            if completed_edges:
                print(f"Updating {len(completed_edges)} edges with completed metadata...", flush=True)
                for edge in completed_edges:
                    edge_result = self.graph.ensure_edge(
                        edge_type=edge['type'],
                        source_id=edge.get('source', edge.get('source_id')),
                        target_id=edge.get('target', edge.get('target_id')),
                        meta=edge.get('meta', {}),
                        confidence=edge.get('confidence', 1.0),
                        status=edge.get('status', 'CONFIRMED')
                    )

                    if edge_result['confirmed']:
                        self._log_event("edge_metadata_completed", {
                            "edge_type": edge['type'],
                            "source": edge.get('source', edge.get('source_id')),
                            "target": edge.get('target', edge.get('target_id')),
                            "file": file_path
                        })

            # Deduplication pass: Find and merge duplicate nodes from this file
            print(f"Running deduplication pass for {file_path}...", flush=True)
            dedup_count = self._deduplicate_nodes(file_path)
            if dedup_count > 0:
                print(f"✓ Deduplicated {dedup_count} duplicate node pairs", flush=True)

            # Create QA tasks
            qa_task_count = 0
            for task in result.get('tasks', []):
                self.state_manager.create_qa_task(
                    file_path=file_path,
                    task_type=task.get('type', 'manual_review'),
                    description=task.get('description', '')
                )
                qa_task_count += 1

                self._log_event("qa_task_created", {
                    "task_type": task.get('type'),
                    "description": task.get('description'),
                    "file": file_path
                })

            # Mark as completed
            self.state_manager.mark_completed(
                file_path=file_path,
                chunk_count=len(chunks),
                node_count=node_count,
                link_count=link_count
            )

            # Update statistics
            self.stats['files_processed'] += 1
            self.stats['total_chunks'] += len(chunks)
            self.stats['total_nodes'] += node_count
            self.stats['total_links'] += link_count
            self.stats['total_qa_tasks'] += qa_task_count

            self._log_event("file_processing_complete", {
                "file": file_path,
                "chunks": len(chunks),
                "nodes": node_count,
                "links": link_count,
                "qa_tasks": qa_task_count
            })

            return True

        except Exception as e:
            # Mark as failed
            import traceback
            error_msg = f"{type(e).__name__}: {str(e)}"
            traceback_str = traceback.format_exc()
            print(f"FULL TRACEBACK:\n{traceback_str}", flush=True)

            self.state_manager.mark_failed(file_path, error_msg)

            self.stats['files_failed'] += 1

            self._log_event("file_processing_failed", {
                "file": file_path,
                "error": error_msg
            })

            return False

    def process_corpus(
        self,
        manifest_path: str,
        max_files: Optional[int] = None,
        resume: bool = True
    ) -> Dict[str, Any]:
        """
        Process entire corpus from manifest.

        Args:
            manifest_path: Path to manifest.json
            max_files: Maximum files to process (None for all)
            resume: Resume from last checkpoint

        Returns:
            Processing statistics
        """
        self._log_event("corpus_processing_start", {
            "manifest": manifest_path,
            "max_files": max_files,
            "resume": resume
        })

        # Sync manifest
        sync_stats = self.sync_manifest(manifest_path)

        # Reset any stuck 'processing' files if resuming
        if resume:
            reset_count = self.state_manager.reset_processing_files()
            if reset_count > 0:
                self._log_event("recovery", {"reset_files": reset_count})

        # Get pending files
        pending_files = self.state_manager.get_pending_files(limit=max_files)

        self._log_event("processing_queue", {
            "pending_count": len(pending_files),
            "max_files": max_files
        })

        if not pending_files:
            self._log_event("corpus_processing_complete", {
                "message": "No pending files to process"
            })
            return self.stats

        # Process files with checkpointing and QA checks
        checkpoint_interval = self.config.processing.checkpoint_interval
        qa_interval = self.config.processing.qa_check_interval
        recent_files_for_qa = []

        for idx, file_record in enumerate(pending_files):
            # Process file
            success = self.process_file(file_record.file_path)

            # Track recent files for QA
            if success:
                recent_files_for_qa.append(file_record.file_path)

            # Run QA check every N files
            if (idx + 1) % qa_interval == 0 and recent_files_for_qa:
                qa_results = self._run_qa_check(recent_files_for_qa)

                # Alert if quality is poor
                if qa_results['quality_score'] < 60:
                    print(f"\n⚠️  WARNING: Quality score below 60 ({qa_results['quality_score']:.1f}/100)")
                    print(f"   Consider reviewing extraction parameters or LLM prompts\n")

                # Clear recent files list
                recent_files_for_qa = []

            # Checkpoint every N files
            if (idx + 1) % checkpoint_interval == 0:
                self._log_event("checkpoint", {
                    "processed": idx + 1,
                    "total": len(pending_files),
                    "stats": self.stats
                })

        # Run final QA check if there are remaining files
        if recent_files_for_qa:
            print(f"\n📊 Running final QA check on remaining {len(recent_files_for_qa)} files...")
            qa_results = self._run_qa_check(recent_files_for_qa)

        # Final statistics
        final_stats = self.state_manager.get_processing_stats()

        self._log_event("corpus_processing_complete", {
            "manifest": manifest_path,
            **final_stats,
            **self.stats
        })

        return {**final_stats, **self.stats}

    def run_linter(self) -> Dict[str, Any]:
        """
        Run structural linter on graph.

        Returns:
            Lint results
        """
        self._log_event("lint_start", {"graph": self.config.falkordb.graph_name})

        linter = GraphLinter(
            self.graph,
            config={
                'enable_c1_check': self.config.lint.enable_c1_check,
                'enable_c2_check': self.config.lint.enable_c2_check,
                'enable_c3_check': self.config.lint.enable_c3_check,
                'enable_c4_check': self.config.lint.enable_c4_check,
                'enable_c5_check': self.config.lint.enable_c5_check,
                'enable_c6_check': self.config.lint.enable_c6_check,
                'enable_c7_check': self.config.lint.enable_c7_check,
            }
        )

        violations = linter.run_all_checks()

        result = {
            'total_violations': len(violations),
            'errors': sum(1 for v in violations if v.severity.value == 'ERROR'),
            'warnings': sum(1 for v in violations if v.severity.value == 'WARNING')
        }

        self._log_event("lint_complete", result)

        return {
            'violations': violations,
            **result
        }


def main():
    """CLI entrypoint."""
    import argparse

    # Setup logging to file AND console
    log_file = Path(__file__).parent / 'corpus_processing.log'

    class TeeOutput:
        """Write to both file and original stream."""
        def __init__(self, file_path, original_stream):
            self.file = open(file_path, 'a')  # Append mode
            self.original = original_stream

        def write(self, data):
            self.original.write(data)
            self.file.write(data)
            self.file.flush()

        def flush(self):
            self.original.flush()
            self.file.flush()

    # Redirect stdout and stderr to log file + console
    sys.stdout = TeeOutput(log_file, sys.stdout)
    sys.stderr = TeeOutput(log_file, sys.stderr)

    # Log session start
    log_section(logger, f"📚 Doc Ingestion Pipeline - Session Started {datetime.now().strftime('%H:%M:%S')}")
    logger.info(f"Log file: {Colors.DIM}{log_file}{Colors.RESET}")

    parser = argparse.ArgumentParser(description='Process documentation corpus')
    parser.add_argument('manifest', help='Path to manifest.json')
    parser.add_argument('--max-files', type=int, help='Maximum files to process')
    parser.add_argument('--no-resume', action='store_true', help='Do not resume from checkpoint')
    parser.add_argument('--lint', action='store_true', help='Run linter after processing')

    args = parser.parse_args()

    # Load config
    config = get_config()

    # Override manifest path
    config.processing.manifest_path = args.manifest

    # Validate config
    errors = config.validate()
    if errors:
        logger.error("Configuration errors:")
        for error in errors:
            logger.error(f"  - {error}")
        sys.exit(1)

    # Initialize processor
    processor = CorpusProcessor(config)

    # Process corpus
    stats = processor.process_corpus(
        manifest_path=args.manifest,
        max_files=args.max_files,
        resume=not args.no_resume
    )

    # Run linter if requested
    if args.lint:
        lint_results = processor.run_linter()
        log_section(logger, "🔍 Structural Validation Results")
        log_table(logger,
            ["Metric", "Count"],
            [
                ["Total violations", lint_results['total_violations']],
                ["Errors", lint_results['errors']],
                ["Warnings", lint_results['warnings']]
            ]
        )

    # Print final stats
    log_section(logger, "✅ Processing Complete")
    log_table(logger,
        ["Metric", "Count"],
        [
            ["Files processed", f"{Colors.BRIGHT_GREEN}{stats.get('files_processed', 0)}{Colors.RESET}"],
            ["Files failed", f"{Colors.BRIGHT_RED}{stats.get('files_failed', 0)}{Colors.RESET}" if stats.get('files_failed', 0) > 0 else "0"],
            ["Total chunks", stats.get('total_chunks', 0)],
            ["Total nodes", stats.get('total_nodes', 0)],
            ["Total links", stats.get('total_links', 0)],
            ["QA tasks", stats.get('total_qa_tasks', 0)]
        ]
    )

    # Exit code: 0 if no failures, 1 if failures
    sys.exit(1 if stats.get('files_failed', 0) > 0 else 0)


if __name__ == "__main__":
    main()
