---
title: Docs Events Overview
generated: canonical
l4_citations:
- protocol/Event_Schema/docs.catalog.emit
- protocol/Event_Schema/docs.draft.created
- protocol/Event_Schema/docs.page.updated
- protocol/Event_Schema/docs.page.upsert
- protocol/Event_Schema/docs.publish
- protocol/Event_Schema/docs.request.generate
- protocol/Event_Schema/docs.slice.emit
retrieved_at: '2025-10-30T19:40:16.787891Z'
source: L4 Protocol Graph (protocol database)
---

# Docs Events Overview

**Generated from L4 Protocol Graph** - 2025-10-30

---

## Event Schemas (7 total)

### broadcast

**Summary:** ecosystem/{ecosystem_id}/org/{org_id}/docs/catalog

**Direction:** `Site-wide TOC broadcast for in-system AI`

**L4 Reference:** `protocol/Event_Schema/docs.catalog.emit`

---

### inject

**Summary:** ecosystem/{ecosystem_id}/org/{org_id}/docs/draft

**Direction:** `AI/tool posts draft back to L2 for review`

**L4 Reference:** `protocol/Event_Schema/docs.draft.created`

---

### broadcast

**Summary:** ecosystem/{ecosystem_id}/org/{org_id}/docs/page

**Direction:** `Page change broadcast for subscribers`

**L4 Reference:** `protocol/Event_Schema/docs.page.updated`

---

### inject

**Summary:** ecosystem/{ecosystem_id}/org/{org_id}/docs/upsert

**Direction:** `L2 accepts page into repo after governance checks`

**L4 Reference:** `protocol/Event_Schema/docs.page.upsert`

---

### broadcast

**Summary:** ecosystem/{ecosystem_id}/org/{org_id}/docs/publish

**Direction:** `Publish doc version, triggers site build + WS broadcast`

**L4 Reference:** `protocol/Event_Schema/docs.publish`

---

### inject

**Summary:** ecosystem/{ecosystem_id}/org/{org_id}/docs/generate

**Direction:** `Request L2 to generate/regenerate a documentation page`

**L4 Reference:** `protocol/Event_Schema/docs.request.generate`

---

### broadcast

**Summary:** ecosystem/{ecosystem_id}/org/{org_id}/docs/slice

**Direction:** `Semantic chunk broadcast for retrieval`

**L4 Reference:** `protocol/Event_Schema/docs.slice.emit`

---


---

## Provenance

**Source:** L4 Protocol Graph (`protocol` database)
**Retrieved:** 2025-10-30T19:40:16.787891Z
**Citations:** 7 L4 nodes

**L4 Node IDs:**
- `protocol/Event_Schema/docs.catalog.emit`
- `protocol/Event_Schema/docs.draft.created`
- `protocol/Event_Schema/docs.page.updated`
- `protocol/Event_Schema/docs.page.upsert`
- `protocol/Event_Schema/docs.publish`
- `protocol/Event_Schema/docs.request.generate`
- `protocol/Event_Schema/docs.slice.emit`