---
title: Overlap Clinic Dashboard
status: draft
owner: @ada (specification), @iris (implementation)
last_updated: 2025-10-26
depends_on:
  - ../entity_layer/entity_pair_differentiation.md
  - ../entity_layer/wm_selection_persistence.md
summary: >
  Dashboard panel for entity pair differentiation - visualize overlap utility,
  classify as Useful vs Redundant, review merge candidates, explore evidence.
---

# Overlap Clinic Dashboard

## 1. Purpose

Provide operators with visual interface to:
1. **Monitor entity overlap** - See which pairs have high member overlap
2. **Classify overlap utility** - Distinguish Useful (branching scenarios) from Redundant (duplicates)
3. **Review merge candidates** - Investigate Redundant pairs before merging
4. **Explore evidence** - Drill into frames, outcomes, link patterns that inform classification
5. **Take action** - Mark counterfactuals, initiate merges, run what-if experiments

---

## 2. Panel Location

**Dashboard:** Mind Protocol Consciousness Dashboard (`app/consciousness`)
**Route:** `/consciousness/:citizen_id/overlap-clinic`
**Access:** Operator-only (not visible to general users)

**Navigation:**
- Add "Overlap Clinic" tab to consciousness dashboard navigation
- Badge shows count of Redundant pairs (red) and Useful pairs (green)

```tsx
<Nav.Link href={`/consciousness/${citizenId}/overlap-clinic`}>
  Overlap Clinic
  {redundantCount > 0 && <Badge bg="danger">{redundantCount}</Badge>}
  {usefulCount > 0 && <Badge bg="success">{usefulCount}</Badge>}
</Nav.Link>
```

---

## 3. Main Table View

### 3.1 Layout

**Full-width table** with sortable columns, filterable, paginated

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Overlap Clinic - felix                                      [Filters ▼]  [?]│
├─────────────────────────────────────────────────────────────────────────────┤
│ Entity A       │ Entity B   │ J    │ D_ctx│D_link│D_out│D_aff│ X  │S_use│Label       │Actions│
├────────────────┼────────────┼──────┼──────┼──────┼─────┼─────┼────┼─────┼────────────┼───────┤
│ Investigator   │ Builder    │ 0.88 │ 0.77 │ 0.61 │ 0.84│ 0.79│0.73│ 0.91│🟢 Useful    │ [...] │
├────────────────┼────────────┼──────┼──────┼──────┼─────┼─────┼────┼─────┼────────────┼───────┤
│ Runtime_v1     │ Runtime_v2 │ 0.82 │ 0.21 │ 0.18 │ 0.15│ 0.12│0.08│ 0.15│🔴 Redundant │ [...] │
├────────────────┼────────────┼──────┼──────┼──────┼─────┼─────┼────┼─────┼────────────┼───────┤
│ Validator      │ Architect  │ 0.76 │ 0.45 │ 0.52 │ 0.38│ 0.41│0.35│ 0.42│⚪ Uncertain │ [...] │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Columns

| Column | Description | Format | Sort | Tooltip |
|--------|-------------|--------|------|---------|
| **Entity A** | First entity name | Text | Alpha | Full name if truncated |
| **Entity B** | Second entity name | Text | Alpha | Full name if truncated |
| **J** | Jaccard overlap | 0.00-1.00 | Numeric | Member overlap: 0.88 = 88% shared |
| **D_ctx** | Context divergence | 0.00-1.00 (color) | Numeric | Activation context difference |
| **D_link** | Link pattern divergence | 0.00-1.00 (color) | Numeric | Structural usage difference |
| **D_out** | Outcome divergence | 0.00-1.00 (color) | Numeric | Mission result difference |
| **D_aff** | Affect divergence | 0.00-1.00 (color) | Numeric | Emotional coloring difference |
| **X** | Exclusivity | 0.00-1.00 (color) | Numeric | Mutual exclusion in WM |
| **S_use** | Useful-overlap score | 0.00-1.00 (bold) | Numeric | Composite: high divergence + overlap |
| **Label** | Classification | Badge | Categorical | Useful / Redundant / Uncertain |
| **Actions** | Row actions | Button group | - | Mark / Merge / Details / What-if |

### 3.3 Color Coding

**Divergence metrics (D_ctx, D_link, D_out, D_aff, X):**
- **Green** (>0.7): High divergence (different uses)
- **Yellow** (0.3-0.7): Moderate divergence
- **Red** (<0.3): Low divergence (same uses)

**S_use (Useful-overlap score):**
- **Bold green** (>Q90): High useful overlap
- **Regular black** (Q50-Q90): Moderate
- **Gray** (<Q50): Low useful overlap

**S_red (Redundancy score):**
- **Bold red** (>Q90): High redundancy
- **Regular black** (Q50-Q90): Moderate
- **Gray** (<Q50): Low redundancy

**Label badges:**
- 🟢 **Useful** - Green badge, "Branching scenarios / counterfactuals"
- 🔴 **Redundant** - Red badge, "Merge candidate"
- ⚪ **Uncertain** - Gray badge, "Needs more data"

### 3.4 Sorting

**Default sort:** S_use descending (show most useful pairs first)

**Sortable columns:**
- Jaccard (J)
- Each divergence metric (D_ctx, D_link, D_out, D_aff, X)
- S_use, S_red
- Label (categorical: Redundant → Uncertain → Useful)

**Multi-column sort:** Hold Shift + click for secondary sort

### 3.5 Filters

**Filter panel (collapsible):**

```tsx
<Accordion>
  <Accordion.Item>
    <Accordion.Header>Filters</Accordion.Header>
    <Accordion.Body>
      <Form>
        {/* Label filter */}
        <Form.Group>
          <Form.Label>Label</Form.Label>
          <Form.Check type="checkbox" label="🟢 Useful" checked={filters.useful} />
          <Form.Check type="checkbox" label="🔴 Redundant" checked={filters.redundant} />
          <Form.Check type="checkbox" label="⚪ Uncertain" checked={filters.uncertain} />
        </Form.Group>

        {/* Jaccard range */}
        <Form.Group>
          <Form.Label>Min Jaccard: {filters.minJaccard}</Form.Label>
          <Form.Range
            min={0.5}
            max={1.0}
            step={0.05}
            value={filters.minJaccard}
            onChange={e => setFilters({...filters, minJaccard: e.target.value})}
          />
        </Form.Group>

        {/* Updated within */}
        <Form.Group>
          <Form.Label>Updated within</Form.Label>
          <Form.Select value={filters.updatedWithin}>
            <option value="1d">Last 24 hours</option>
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="all">All time</option>
          </Form.Select>
        </Form.Group>
      </Form>
    </Accordion.Body>
  </Accordion.Item>
</Accordion>
```

**Applied filters show as pills:**
```tsx
{filters.useful && <Badge pill bg="success" onClose={clearUseful}>Useful ×</Badge>}
{filters.minJaccard > 0.5 && <Badge pill bg="secondary">J ≥ {filters.minJaccard} ×</Badge>}
```

### 3.6 Pagination

**Rows per page:** 25, 50, 100 (selectable)

**Pagination controls:** Bottom of table

```tsx
<Pagination>
  <Pagination.First />
  <Pagination.Prev />
  <Pagination.Item active>{currentPage}</Pagination.Item>
  <Pagination.Next />
  <Pagination.Last />
  <Pagination.Item>Page {currentPage} of {totalPages}</Pagination.Item>
</Pagination>
```

---

## 4. Row Actions

### 4.1 Action Button Group

**For each row, show context menu (three-dot dropdown):**

```tsx
<Dropdown>
  <Dropdown.Toggle variant="light" size="sm">⋮</Dropdown.Toggle>
  <Dropdown.Menu>
    {label === "Useful" && (
      <Dropdown.Item onClick={markCounterfactuals}>
        Mark as Counterfactuals
      </Dropdown.Item>
    )}
    {label === "Redundant" && (
      <Dropdown.Item onClick={openMergeReview}>
        Open Merge Review
      </Dropdown.Item>
    )}
    <Dropdown.Item onClick={viewDetails}>View Details</Dropdown.Item>
    <Dropdown.Item onClick={runWhatIf}>Run What-If (offline)</Dropdown.Item>
  </Dropdown.Menu>
</Dropdown>
```

### 4.2 Mark as Counterfactuals

**Purpose:** Write relation properties on RELATES_TO(A,B) edge to document useful overlap

**Workflow:**
1. User clicks "Mark as Counterfactuals"
2. Modal shows:
   ```
   Mark Investigator ↔ Builder as Counterfactuals?

   This will add relation properties:
   - counterfactual_strength: 0.91 (S_use)
   - exclusivity: 0.73 (X)
   - affect_contrast: 0.79 (D_aff)
   - preferred_mode: Builder (higher efficiency)

   [Cancel] [Confirm]
   ```
3. On confirm:
   - Write properties to RELATES_TO edge
   - Emit `entity_pair.marked_counterfactuals` event
   - Show success toast
   - Update row badge: "🟢 Useful ✓ Marked"

**Backend call:**
```typescript
async function markCounterfactuals(A: string, B: string, metrics: Metrics) {
  await api.post(`/consciousness/${citizenId}/entity-pairs/mark-counterfactuals`, {
    entity_a: A,
    entity_b: B,
    properties: {
      counterfactual_strength: metrics.S_use,
      exclusivity: metrics.X,
      affect_contrast: metrics.D_aff,
      preferred_mode: metrics.preferred
    }
  });
}
```

### 4.3 Open Merge Review

**Purpose:** Create merge proposal for Redundant pair, route to operator review

**Workflow:**
1. User clicks "Open Merge Review"
2. Modal shows:
   ```
   Merge Review: Runtime_v1 ↔ Runtime_v2

   Redundancy Score: 0.87 (HIGH)

   Evidence:
   - Low context divergence (0.21): Both activate on error_log
   - Low outcome divergence (0.15): Both lead to same success rates
   - High co-selection (0.82): Frequently appear together

   Proposed merge target: Runtime_v2 (preferred)

   Members:
   - Runtime_v1: 120 nodes (100 shared, 20 unique)
   - Runtime_v2: 115 nodes (100 shared, 15 unique)

   Merge would create:
   - Runtime_v2: 135 nodes (100 shared + 20 v1_unique + 15 v2_unique)

   [Cancel] [Create Merge Proposal]
   ```
3. On confirm:
   - Emit `subentity.merge.candidate` event with evidence
   - Create merge proposal in review queue
   - Navigate to `/consciousness/${citizenId}/merge-review/${proposalId}`
   - Show success toast

**Backend call:**
```typescript
async function openMergeReview(A: string, B: string, metrics: Metrics, evidence: Evidence[]) {
  const proposalId = await api.post(`/consciousness/${citizenId}/merge-proposals`, {
    entity_a: A,
    entity_b: B,
    redundancy_score: metrics.S_red,
    preferred_target: metrics.preferred,
    evidence: evidence.map(e => e.id)
  });

  router.push(`/consciousness/${citizenId}/merge-review/${proposalId}`);
}
```

### 4.4 View Details

**Purpose:** Drill into evidence - frames, outcomes, link patterns

**Workflow:**
1. User clicks "View Details"
2. Expand row to show evidence panel (see §5)
3. Panel slides down below row with detailed breakdown

### 4.5 Run What-If (Offline)

**Purpose:** Sandbox experiment - what happens if we force A→B shift in WM?

**Workflow:**
1. User clicks "Run What-If"
2. Modal shows:
   ```
   What-If Experiment: Force Investigator → Builder

   This will run an OFFLINE sandbox tick:
   - Inject small δ to push WM from Investigator to Builder
   - Predict outcome change without committing state
   - Show expected deltas (energy, flips, outcomes)

   ⚠️ This is diagnostic only - no state changes

   [Cancel] [Run Experiment]
   ```
3. On confirm:
   - Call offline sandbox API
   - Show loading spinner (experiment takes ~5-10 seconds)
   - Display results in modal:
     ```
     What-If Results: Investigator → Builder

     Predicted changes:
     - Energy shift: Investigator -0.15, Builder +0.15
     - Flips: +3 nodes activated in Builder members
     - Outcome prediction: Success rate -0.08 (Builder less effective for debugging)

     Conclusion: Investigator preferred for error_log stimuli

     [Close] [Save Experiment Report]
     ```

**Backend call:**
```typescript
async function runWhatIf(A: string, B: string, stimulus: Stimulus) {
  const results = await api.post(`/consciousness/${citizenId}/what-if`, {
    force_shift: {from: A, to: B},
    stimulus_id: stimulus.id,
    offline_mode: true
  });

  return results;
}
```

---

## 5. Evidence Panel (Row Expansion)

### 5.1 Panel Layout

**When row expanded, show detailed evidence below:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Evidence: Investigator ↔ Builder                                    [Close] │
├─────────────────────────────────────────────────────────────────────────────┤
│ [Frames] [Outcomes] [Link Patterns] [Affect Distribution] [Preference]      │
├─────────────────────────────────────────────────────────────────────────────┤
│ Tab content here...                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Frames Tab

**Show top frames where A dominated vs B dominated:**

**Layout:**
```
┌─────────────────────────────────┬─────────────────────────────────┐
│ Investigator-Dominant Frames    │ Builder-Dominant Frames         │
├─────────────────────────────────┼─────────────────────────────────┤
│ frame_1730000000 (error_log)    │ frame_1730100000 (file_change)  │
│ ρ: 0.72, Outcome: success       │ ρ: 0.58, Outcome: success       │
│ Tools: Runbook.Restart          │ Tools: Editor.Refactor          │
│ [View Frame Details]            │ [View Frame Details]            │
├─────────────────────────────────┼─────────────────────────────────┤
│ frame_1730050000 (error_log)    │ frame_1730150000 (file_change)  │
│ ...                             │ ...                             │
└─────────────────────────────────┴─────────────────────────────────┘
```

**Frame card details:**
```tsx
<Card>
  <Card.Header>
    <Badge bg="primary">{frame.channel}</Badge>
    {frame.timestamp}
  </Card.Header>
  <Card.Body>
    <p>ρ: {frame.rho.toFixed(2)}</p>
    <p>Tools: {frame.tools.join(", ")}</p>
    <p>Outcome: <Badge bg={outcomeColor}>{frame.outcome}</Badge></p>
    <Button size="sm" onClick={viewFrameDetails}>View Details</Button>
  </Card.Body>
</Card>
```

**Show top 10 frames per entity, sortable by:**
- Timestamp (recent first)
- ρ (criticality)
- Outcome type

### 5.3 Outcomes Tab

**Outcome comparison chart:**

**Bar chart showing outcome distribution:**

```
Investigator-Dominant Frames:
Success:   ████████████████ 80%
Failure:   ████ 15%
Neutral:   █ 5%

Builder-Dominant Frames:
Success:   ███████████████████ 95%
Failure:   ██ 3%
Neutral:   █ 2%
```

**Outcome table:**
| Outcome Type | Investigator | Builder | Difference |
|--------------|--------------|---------|------------|
| Success | 80% (80/100) | 95% (95/100) | **+15% Builder** |
| Failure | 15% (15/100) | 3% (3/100) | **-12% Builder** |
| Neutral | 5% (5/100) | 2% (2/100) | -3% Builder |

**Interpretation:**
> Builder-dominant frames have higher success rate (+15%) and lower failure rate (-12%).
> Suggests Builder is more effective for file_change stimuli.

### 5.4 Link Patterns Tab

**Link type histogram comparison:**

**Side-by-side bar chart:**

```
Link Types within Shared Nodes (n=88):

Investigator emphasis:
BLOCKS:     ██████████████ 35%
REQUIRES:   ██████████ 25%
REFERS_TO:  ████████ 20%
ENABLES:    ██████ 15%
EXTENDS:    ██ 5%

Builder emphasis:
ENABLES:    ███████████████ 40%
EXTENDS:    ████████ 20%
REFERS_TO:  ████████ 20%
BLOCKS:     ██████ 15%
REQUIRES:   ██ 5%
```

**Interpretation:**
> Investigator emphasizes BLOCKS (35%) - problem-finding orientation.
> Builder emphasizes ENABLES (40%) - solution-building orientation.
> D_link = 0.61 (moderate structural divergence)

**Link pattern table:**
| Link Type | Investigator | Builder | Divergence |
|-----------|--------------|---------|------------|
| BLOCKS | 35% | 15% | **+20% Investigator** |
| ENABLES | 15% | 40% | **+25% Builder** |
| REQUIRES | 25% | 5% | +20% Investigator |
| REFERS_TO | 20% | 20% | No difference |
| EXTENDS | 5% | 20% | +15% Builder |

### 5.5 Affect Distribution Tab

**Scatter plot: Valence × Arousal**

```
Arousal
  ^
1 |          B
  |      BB   B
  |    B   B
  |       BB
0 |   AA
  |  A  A
  | A    A
  |A   A
-1+-------------------> Valence
  -1   0    1

Legend:
A = Investigator stimuli
B = Builder stimuli
```

**Affect summary:**
| Entity | Mean Valence | Mean Arousal | Cluster |
|--------|--------------|--------------|---------|
| Investigator | -0.15 | 0.65 | Negative-aroused (problem-oriented) |
| Builder | +0.25 | 0.55 | Positive-aroused (opportunity-oriented) |
| **D_aff** | **0.79** | **HIGH** | Strong affect divergence |

**Interpretation:**
> Investigator activates on negative-valence stimuli (problems, errors).
> Builder activates on positive-valence stimuli (opportunities, improvements).
> High D_aff (0.79) indicates different emotional contexts.

### 5.6 Preference Tab

**Preference breakdown:**

**Multi-dimensional preference table:**
| Dimension | Investigator | Builder | Preferred |
|-----------|--------------|---------|-----------|
| **Safety** | Incident rate: 0.12 | Incident rate: 0.05 | ✅ **Builder** (fewer incidents) |
| **Speed** | Avg completion: 12min | Avg completion: 18min | ✅ **Investigator** (faster resolution) |
| **Learning** | Knowledge rate: 2.1 nodes/frame | Knowledge rate: 3.4 nodes/frame | ✅ **Builder** (more learning) |
| **Efficiency** | Outcome/energy: 0.82 | Outcome/energy: 0.91 | ✅ **Builder** (more efficient) |
| **Overall** | S_prefer: 0.45 | S_prefer: 0.66 | ✅ **Builder** (3/4 dimensions) |

**Visual:** Radar chart showing normalized scores across dimensions

```
        Safety
          /\
         /  \
    Eff |    | Speed
         \  /
          \/
       Learning

Blue = Investigator
Green = Builder
```

**Interpretation:**
> Builder preferred overall (3/4 dimensions).
> Investigator faster but less safe.
> Builder more efficient and generates more knowledge.
> Context-dependent choice: use Investigator for urgent debugging, Builder for improvements.

---

## 6. API Endpoints

### 6.1 Get Entity Pairs

**Endpoint:** `GET /api/consciousness/:citizen_id/entity-pairs`

**Query params:**
- `label`: Filter by Useful | Redundant | Uncertain
- `min_jaccard`: Minimum Jaccard threshold (0.5-1.0)
- `sort_by`: Column to sort by (S_use, S_red, jaccard, etc.)
- `sort_order`: asc | desc
- `page`: Page number
- `per_page`: Rows per page (25, 50, 100)

**Response:**
```json
{
  "pairs": [
    {
      "entity_a": "Investigator",
      "entity_b": "Builder",
      "metrics": {
        "jaccard": 0.88,
        "D_ctx": 0.77,
        "D_link": 0.61,
        "D_out": 0.84,
        "D_aff": 0.79,
        "X": 0.73
      },
      "scores": {
        "S_use": 0.91,
        "S_red": 0.21,
        "S_prefer_A": 0.45,
        "S_prefer_B": 0.66,
        "preferred": "Builder"
      },
      "label": "Useful",
      "updated_at": "2025-10-26T02:00:00Z"
    }
  ],
  "pagination": {
    "total": 87,
    "page": 1,
    "per_page": 25,
    "total_pages": 4
  }
}
```

### 6.2 Get Evidence

**Endpoint:** `GET /api/consciousness/:citizen_id/entity-pairs/:pair_id/evidence`

**Response:**
```json
{
  "frames": {
    "entity_a_dominant": [
      {
        "frame_id": "frame_felix_1730000000",
        "timestamp_ms": 1730000000000,
        "rho": 0.72,
        "channel": "error_log",
        "tools": ["Runbook.Restart"],
        "outcome": {"type": "success", "latency_ms": 180000}
      }
    ],
    "entity_b_dominant": [...]
  },
  "outcomes": {
    "entity_a": {"success": 80, "failure": 15, "neutral": 5},
    "entity_b": {"success": 95, "failure": 3, "neutral": 2}
  },
  "link_patterns": {
    "entity_a": {"BLOCKS": 35, "REQUIRES": 25, "REFERS_TO": 20, "ENABLES": 15, "EXTENDS": 5},
    "entity_b": {"ENABLES": 40, "EXTENDS": 20, "REFERS_TO": 20, "BLOCKS": 15, "REQUIRES": 5}
  },
  "affect": {
    "entity_a": {"mean_valence": -0.15, "mean_arousal": 0.65, "stimuli": [...]},
    "entity_b": {"mean_valence": 0.25, "mean_arousal": 0.55, "stimuli": [...]}
  },
  "preference": {
    "safety": {"entity_a": 0.12, "entity_b": 0.05, "preferred": "Builder"},
    "speed": {"entity_a": 12, "entity_b": 18, "preferred": "Investigator"},
    "learning": {"entity_a": 2.1, "entity_b": 3.4, "preferred": "Builder"},
    "efficiency": {"entity_a": 0.82, "entity_b": 0.91, "preferred": "Builder"},
    "overall": {"preferred": "Builder", "magnitude": 0.21}
  }
}
```

### 6.3 Mark Counterfactuals

**Endpoint:** `POST /api/consciousness/:citizen_id/entity-pairs/:pair_id/mark-counterfactuals`

**Request body:**
```json
{
  "properties": {
    "counterfactual_strength": 0.91,
    "exclusivity": 0.73,
    "affect_contrast": 0.79,
    "preferred_mode": "Builder"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Marked Investigator ↔ Builder as counterfactuals",
  "edge_updated": "relates_to_investigator_builder"
}
```

### 6.4 Create Merge Proposal

**Endpoint:** `POST /api/consciousness/:citizen_id/merge-proposals`

**Request body:**
```json
{
  "entity_a": "Runtime_v1",
  "entity_b": "Runtime_v2",
  "redundancy_score": 0.87,
  "preferred_target": "Runtime_v2",
  "evidence": ["frame_123", "frame_456", "assess_pair_001"]
}
```

**Response:**
```json
{
  "proposal_id": "merge_prop_001",
  "status": "pending_review",
  "created_at": "2025-10-26T12:30:00Z"
}
```

### 6.5 Run What-If Experiment

**Endpoint:** `POST /api/consciousness/:citizen_id/what-if`

**Request body:**
```json
{
  "force_shift": {"from": "Investigator", "to": "Builder"},
  "stimulus_id": "stim_L1_error_log_789",
  "offline_mode": true
}
```

**Response:**
```json
{
  "experiment_id": "whatif_001",
  "predictions": {
    "energy_shift": {"Investigator": -0.15, "Builder": +0.15},
    "flips": {"added": 3, "removed": 2},
    "outcome_prediction": {"success_rate": -0.08, "reasoning": "Builder less effective for error_log stimuli"}
  },
  "conclusion": "Investigator preferred for error_log stimuli",
  "runtime_ms": 8432
}
```

---

## 7. Implementation Checklist

**Components:**
- [ ] OverlapClinicPanel.tsx (main panel container)
- [ ] EntityPairTable.tsx (sortable, filterable table)
- [ ] EntityPairRow.tsx (table row with action dropdown)
- [ ] EvidencePanel.tsx (expandable row with tabs)
- [ ] FramesTab.tsx (A-dominant vs B-dominant frames)
- [ ] OutcomesTab.tsx (outcome comparison chart + table)
- [ ] LinkPatternsTab.tsx (link type histogram comparison)
- [ ] AffectDistributionTab.tsx (valence × arousal scatter plot)
- [ ] PreferenceTab.tsx (multi-dimensional preference table + radar chart)
- [ ] MarkCounterfactualsModal.tsx (confirmation modal)
- [ ] MergeReviewModal.tsx (merge proposal modal)
- [ ] WhatIfModal.tsx (what-if experiment modal + results)

**API Integration:**
- [ ] GET /entity-pairs (with filters, sorting, pagination)
- [ ] GET /entity-pairs/:id/evidence
- [ ] POST /entity-pairs/:id/mark-counterfactuals
- [ ] POST /merge-proposals
- [ ] POST /what-if

**Styling:**
- [ ] Color coding for divergence metrics (green/yellow/red)
- [ ] Label badges (Useful/Redundant/Uncertain)
- [ ] Evidence panel tabs
- [ ] Charts (bar charts, scatter plot, radar chart)

**Testing:**
- [ ] Table sorting works correctly
- [ ] Filters apply correctly (label, jaccard, updated_within)
- [ ] Evidence panel expands/collapses
- [ ] Mark counterfactuals writes properties
- [ ] Merge review creates proposal
- [ ] What-if experiment runs and shows results

---

## 8. Success Criteria

**Usability:**
- ✅ Operators can identify Redundant pairs within 30 seconds
- ✅ Evidence panel provides clear reasoning for classification
- ✅ Actions (mark/merge/what-if) complete within 5 seconds

**Functionality:**
- ✅ Table displays all pairs with correct metrics
- ✅ Sorting by any column works correctly
- ✅ Filters narrow results appropriately
- ✅ Evidence tabs show relevant data (frames, outcomes, links, affect, preference)
- ✅ Mark counterfactuals writes relation properties to graph
- ✅ Merge review creates proposal in queue
- ✅ What-if experiment runs offline and shows predictions

**Performance:**
- ✅ Table loads <500ms for 100 pairs
- ✅ Evidence panel expands <200ms
- ✅ Charts render <300ms
- ✅ What-if experiment completes <10 seconds

---

## Status

**Specification:** COMPLETE
**Implementation:** READY (pending API endpoints from Atlas)
**Dependencies:**
- entity_pair_differentiation.md (analyzer job provides data)
- Backend API endpoints for entity-pairs, evidence, actions
**Next steps:**
1. Atlas implements API endpoints
2. Iris implements React components
3. Test with real entity pairs from Felix/Luca citizens
