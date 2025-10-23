"""
Adapters package for Mind Protocol orchestration layer.

Adapters handle I/O boundaries:
- storage: FalkorDB operations (retrieval, insertion, extraction)
- search: Embedding and semantic search
- ws: WebSocket event emission
- api: REST API endpoints

All adapters are stateless and can be imported by services.

Author: Ada (Architect)
Created: 2025-10-22
"""
