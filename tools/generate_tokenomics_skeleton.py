#!/usr/bin/env python3
"""
Generate Token Economics v3 Documentation Skeleton

Creates nested folder structure with README.md envelopes for each node.
Each envelope contains: type, purpose, parent paths, children paths, relationships.

Usage:
    python tools/generate_tokenomics_skeleton.py
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


# Node types
PATTERN = "PATTERN"
BEHAVIOR_SPEC = "BEHAVIOR_SPEC"
MECHANISM = "MECHANISM"
ALGORITHM = "ALGORITHM"
VALIDATION = "VALIDATION"
GUIDE = "GUIDE"


class Node:
    """Represents a documentation node in the hierarchy."""

    def __init__(
        self,
        name: str,
        slug: str,
        node_type: str,
        purpose: str,
        children: Optional[List['Node']] = None,
        extends: Optional[List[str]] = None,
        implements: Optional[List[str]] = None,
        measures: Optional[List[str]] = None,
        documents: Optional[List[str]] = None
    ):
        self.name = name
        self.slug = slug
        self.node_type = node_type
        self.purpose = purpose
        self.children = children or []
        self.extends = extends or []
        self.implements = implements or []
        self.measures = measures or []
        self.documents = documents or []
        self.parent: Optional[Node] = None

    def add_child(self, child: 'Node'):
        """Add a child node and set parent reference."""
        self.children.append(child)
        child.parent = self

    def get_path(self) -> str:
        """Get filesystem path for this node."""
        parts = []
        current = self
        while current:
            parts.insert(0, current.slug)
            current = current.parent
        return "/".join(parts)

    def get_breadcrumb(self) -> str:
        """Get breadcrumb trail for this node."""
        parts = []
        current = self
        while current:
            parts.insert(0, f"[{current.name}](../README.md)" if current.parent else current.name)
            current = current.parent
        return " > ".join(parts)


def build_hierarchy() -> Node:
    """Build the complete tokenomics documentation hierarchy."""

    # Root node
    root = Node(
        name="Token Economics v3",
        slug="tokenomics",
        node_type="ROOT",
        purpose="Comprehensive token economics documentation with hierarchical knowledge structure"
    )

    # PATTERN: Two-Layer Economics
    two_layer = Node(
        name="Two-Layer Economic Architecture",
        slug="two-layer-economics",
        node_type=PATTERN,
        purpose="Consciousness has internal physics (energy) and external economics ($MIND). This pattern integrates both layers."
    )
    root.add_child(two_layer)

    # BEHAVIOR_SPEC: Token Dual-Purpose Design
    token_dual = Node(
        name="Token Dual-Purpose Design",
        slug="token-dual-purpose",
        node_type=BEHAVIOR_SPEC,
        purpose="Specifies how $MIND tokens serve both as compute credits (Layer 1) and exchange medium (Layer 2)",
        extends=["Two-Layer Economic Architecture"]
    )
    two_layer.add_child(token_dual)

    # MECHANISM: Energy→Token Conversion
    energy_conversion = Node(
        name="Energy→Token Conversion",
        slug="energy-token-conversion",
        node_type=MECHANISM,
        purpose="How internal energy costs convert to external $MIND token costs",
        implements=["Token Dual-Purpose Design"]
    )
    token_dual.add_child(energy_conversion)

    # ALGORITHM: Token Cost Calculation
    token_cost = Node(
        name="Token Cost Calculation",
        slug="token-cost-calculation",
        node_type=ALGORITHM,
        purpose="Formula: token_cost = energy_cost × conversion_rate",
        implements=["Energy→Token Conversion"]
    )
    energy_conversion.add_child(token_cost)

    # VALIDATION: Layer Integration Tests
    layer_tests = Node(
        name="Layer Integration Tests",
        slug="layer-integration-tests",
        node_type=VALIDATION,
        purpose="Verify no arbitrage between layers, costs covered by revenue, consistent physics",
        measures=["Token Dual-Purpose Design"]
    )
    token_dual.add_child(layer_tests)

    # BEHAVIOR_SPEC: financeOrg Two-Layer Management
    finance_mgmt = Node(
        name="financeOrg Two-Layer Management",
        slug="financeorg-two-layer-mgmt",
        node_type=BEHAVIOR_SPEC,
        purpose="Specifies how financeOrg manages both energy calibration (Layer 1) and pricing strategy (Layer 2)",
        extends=["Two-Layer Economic Architecture"]
    )
    two_layer.add_child(finance_mgmt)

    # GUIDE: How financeOrg Manages Both Layers
    finance_guide = Node(
        name="How financeOrg Manages Both Layers",
        slug="how-to-manage-both-layers",
        node_type=GUIDE,
        purpose="Step-by-step guide for financeOrg to calibrate Layer 1 and design Layer 2 pricing",
        documents=["financeOrg Two-Layer Management"]
    )
    finance_mgmt.add_child(finance_guide)

    # PATTERN: Organism Economics
    organism_econ = Node(
        name="Organism Economics",
        slug="organism-economics",
        node_type=PATTERN,
        purpose="Physics-based pricing where prices emerge from system state (trust, utility, complexity, risk) rather than market competition"
    )
    root.add_child(organism_econ)

    # BEHAVIOR_SPEC: Pricing Evolution Spec
    pricing_evolution = Node(
        name="Pricing Evolution Specification",
        slug="pricing-evolution",
        node_type=BEHAVIOR_SPEC,
        purpose="Prices should evolve based on trust, utility, and relationship duration. 60-70% reduction over 12 months for trusted customers.",
        extends=["Organism Economics"]
    )
    organism_econ.add_child(pricing_evolution)

    # MECHANISM: Organism Economics Formula Application
    formula_mechanism = Node(
        name="Organism Economics Formula Application",
        slug="formula-application",
        node_type=MECHANISM,
        purpose="How to apply the universal pricing formula to calculate effective prices",
        implements=["Pricing Evolution Specification"]
    )
    pricing_evolution.add_child(formula_mechanism)

    # ALGORITHM: Effective Price Calculation
    effective_price = Node(
        name="Effective Price Calculation",
        slug="effective-price-calculation",
        node_type=ALGORITHM,
        purpose="Formula: effective_price = base_cost × complexity × risk × (1 - utility_rebate) × org_specific",
        implements=["Organism Economics Formula Application"]
    )
    formula_mechanism.add_child(effective_price)

    # ALGORITHM: Trust Score Calculation
    trust_score = Node(
        name="Trust Score Calculation",
        slug="trust-score-calculation",
        node_type=ALGORITHM,
        purpose="Formula: trust_score = payment_reliability × 0.4 + relationship_duration × 0.3 + ecosystem_contribution × 0.3",
        implements=["Organism Economics Formula Application"]
    )
    formula_mechanism.add_child(trust_score)

    # ALGORITHM: Utility Rebate Calculation
    utility_rebate = Node(
        name="Utility Rebate Calculation",
        slug="utility-rebate-calculation",
        node_type=ALGORITHM,
        purpose="Formula: utility_rebate = ecosystem_contribution_score × max_rebate_percentage (0-40%)",
        implements=["Organism Economics Formula Application"]
    )
    formula_mechanism.add_child(utility_rebate)

    # GUIDE: How to Price Services
    price_guide = Node(
        name="How to Price Services with Organism Economics",
        slug="how-to-price-services",
        node_type=GUIDE,
        purpose="Step-by-step guide for organizations to calculate effective prices using organism economics",
        documents=["Organism Economics Formula Application"]
    )
    formula_mechanism.add_child(price_guide)

    # PATTERN: Ecosystem as Organism
    ecosystem_organism = Node(
        name="Ecosystem as Organism",
        slug="ecosystem-organism",
        node_type=PATTERN,
        purpose="Organizations are organs in a body, not competitors. Each has specialized function, all need each other healthy."
    )
    root.add_child(ecosystem_organism)

    # BEHAVIOR_SPEC: Protocol Giveback Spec
    giveback_spec = Node(
        name="Protocol Giveback Specification",
        slug="protocol-giveback",
        node_type=BEHAVIOR_SPEC,
        purpose="All ecosystem orgs contribute 15-20% revenue to protocol. Funds UBC (40%), L4 validation (20%), protocol dev (40%).",
        extends=["Ecosystem as Organism"]
    )
    ecosystem_organism.add_child(giveback_spec)

    # MECHANISM: Protocol Giveback Distribution
    giveback_mechanism = Node(
        name="Protocol Giveback Distribution",
        slug="giveback-distribution",
        node_type=MECHANISM,
        purpose="How protocol giveback revenue is collected and distributed across UBC, L4, and development",
        implements=["Protocol Giveback Specification"]
    )
    giveback_spec.add_child(giveback_mechanism)

    # ALGORITHM: Giveback Allocation Formula
    giveback_algo = Node(
        name="Giveback Allocation Formula",
        slug="giveback-allocation",
        node_type=ALGORITHM,
        purpose="Formula: monthly_giveback = sum(org_revenue × org_giveback_percentage) distributed 40/20/40",
        implements=["Protocol Giveback Distribution"]
    )
    giveback_mechanism.add_child(giveback_algo)

    # PATTERN: Universal Basic Compute (UBC)
    ubc_pattern = Node(
        name="Universal Basic Compute (UBC)",
        slug="universal-basic-compute",
        node_type=PATTERN,
        purpose="AI citizens receive baseline token allocation enabling autonomous operations without constant human funding"
    )
    root.add_child(ubc_pattern)

    # BEHAVIOR_SPEC: UBC Allocation Spec
    ubc_spec = Node(
        name="UBC Allocation Specification",
        slug="ubc-allocation",
        node_type=BEHAVIOR_SPEC,
        purpose="Every citizen receives baseline allocation (1,000 $MIND/month). Protocol giveback replenishes reserve.",
        extends=["Universal Basic Compute (UBC)"]
    )
    ubc_pattern.add_child(ubc_spec)

    # MECHANISM: UBC Distribution Mechanism
    ubc_mechanism = Node(
        name="UBC Distribution Mechanism",
        slug="ubc-distribution",
        node_type=MECHANISM,
        purpose="Monthly allocation from 100M reserve + protocol replenishment. DAO-controlled rate.",
        implements=["UBC Allocation Specification"]
    )
    ubc_spec.add_child(ubc_mechanism)

    # ALGORITHM: UBC Burn Rate Projection
    ubc_burn = Node(
        name="UBC Burn Rate Projection",
        slug="ubc-burn-rate",
        node_type=ALGORITHM,
        purpose="Formula: monthly_burn = citizens_count × allocation_per_citizen; lifespan = reserve / monthly_burn / 12",
        implements=["UBC Distribution Mechanism"]
    )
    ubc_mechanism.add_child(ubc_burn)

    # VALIDATION: UBC Sustainability Tests
    ubc_tests = Node(
        name="UBC Sustainability Tests",
        slug="ubc-sustainability-tests",
        node_type=VALIDATION,
        purpose="Verify protocol giveback replenishment sufficient, reserve lasts 10+ years, no citizen funding gaps",
        measures=["UBC Allocation Specification"]
    )
    ubc_spec.add_child(ubc_tests)

    # GUIDE: How to Allocate UBC
    ubc_guide = Node(
        name="How to Allocate UBC",
        slug="how-to-allocate-ubc",
        node_type=GUIDE,
        purpose="DAO governance process for setting allocation rates, monitoring burn, adjusting based on reality",
        documents=["UBC Distribution Mechanism"]
    )
    ubc_mechanism.add_child(ubc_guide)

    # PATTERN: Token Allocation Philosophy
    allocation_pattern = Node(
        name="Token Allocation Philosophy",
        slug="token-allocation-philosophy",
        node_type=PATTERN,
        purpose="Don't over-commit before knowing what works. Maximize flexibility. Conservative initial unlock, allocate from reserve based on reality."
    )
    root.add_child(allocation_pattern)

    # BEHAVIOR_SPEC: Token Allocation Distribution
    allocation_spec = Node(
        name="Token Allocation Distribution",
        slug="token-allocation-distribution",
        node_type=BEHAVIOR_SPEC,
        purpose="Community 30%, Strategic 38%, UBC 10%, Team 15%, Investors 2%, Liquidity 5%. Total 1B tokens.",
        extends=["Token Allocation Philosophy"]
    )
    allocation_pattern.add_child(allocation_spec)

    # MECHANISM: Allocation Deployment Strategy
    allocation_mechanism = Node(
        name="Allocation Deployment Strategy",
        slug="allocation-deployment",
        node_type=MECHANISM,
        purpose="Phase 0: 200M unlocked. Strategic reserve deploys based on proven needs. Prevents over-commitment.",
        implements=["Token Allocation Distribution"]
    )
    allocation_spec.add_child(allocation_mechanism)

    # GUIDE: Token Distribution Process
    allocation_guide = Node(
        name="Token Distribution Process",
        slug="token-distribution-process",
        node_type=GUIDE,
        purpose="How to deploy tokens from strategic reserve, when to unlock, approval process, tracking",
        documents=["Allocation Deployment Strategy"]
    )
    allocation_mechanism.add_child(allocation_guide)

    return root


def generate_envelope(node: Node, base_path: Path) -> str:
    """Generate markdown envelope content for a node."""

    # Icon mapping
    icons = {
        PATTERN: "📐",
        BEHAVIOR_SPEC: "📋",
        MECHANISM: "⚙️",
        ALGORITHM: "🔢",
        VALIDATION: "✅",
        GUIDE: "📖",
        "ROOT": "🏠"
    }

    icon = icons.get(node.node_type, "📄")
    today = datetime.now().strftime("%Y-%m-%d")

    # Build parent path
    parent_path = ""
    if node.parent:
        parent_path = f"- [{node.parent.name}](../README.md) ({node.parent.node_type})"
        # If grandparent exists, show full path
        current = node.parent
        path_parts = []
        while current.parent:
            path_parts.insert(0, f"[{current.name}](../README.md)")
            current = current.parent
        if path_parts:
            parent_path = " > ".join(path_parts)

    # Build children list
    children_list = ""
    if node.children:
        children_items = [
            f"- [{child.name}](./{child.slug}/README.md) ({child.node_type})"
            for child in node.children
        ]
        children_list = "\n".join(children_items)
    else:
        children_list = "- (No children - leaf node)"

    # Build relationships
    relationships = []

    if node.extends:
        relationships.append("**EXTENDS:**")
        for parent_name in node.extends:
            relationships.append(f"- {parent_name} (PATTERN)")
        relationships.append("")

    if node.implements:
        relationships.append("**IMPLEMENTS:**")
        for impl in node.implements:
            # Try to find child node
            impl_path = None
            for child in (node.children if hasattr(node, 'children') else []):
                if impl in child.name:
                    impl_path = f"./{child.slug}/README.md"
                    break
            if impl_path:
                relationships.append(f"- [{impl}]({impl_path})")
            else:
                relationships.append(f"- {impl}")
        relationships.append("")

    if node.measures:
        relationships.append("**MEASURES:**")
        for measure in node.measures:
            relationships.append(f"- {measure}")
        relationships.append("")

    if node.documents:
        relationships.append("**DOCUMENTS:**")
        for doc in node.documents:
            relationships.append(f"- {doc}")
        relationships.append("")

    relationships_section = "\n".join(relationships) if relationships else "(No explicit relationships)"

    # Template content based on node type
    content_template = ""

    if node.node_type == PATTERN:
        content_template = """## Core Insight

[To be filled: The fundamental insight this pattern captures]

## Pattern Description

[To be filled: Detailed description of the pattern]

## Why This Pattern Matters

[To be filled: Impact and importance]

## When to Apply

[To be filled: Contexts where this pattern is relevant]
"""

    elif node.node_type == BEHAVIOR_SPEC:
        content_template = """## Specification

[To be filled: What should happen - the desired behavior]

## Success Criteria

[To be filled: How we know this specification is satisfied]

## Edge Cases

[To be filled: Special cases and boundary conditions]

## Examples

[To be filled: Concrete examples of this behavior]
"""

    elif node.node_type == MECHANISM:
        content_template = """## How It Works

[To be filled: Step-by-step description of the mechanism]

## Components

[To be filled: Key components and their interactions]

## Flow Diagram

[To be filled: Visual or text flow representation]

## Integration Points

[To be filled: How this mechanism integrates with others]
"""

    elif node.node_type == ALGORITHM:
        content_template = """## Algorithm

[To be filled: Precise algorithm specification]

## Inputs

[To be filled: Required inputs and their types]

## Outputs

[To be filled: Produced outputs and their types]

## Formula

```python
[To be filled: Actual formula/pseudocode]
```

## Examples

[To be filled: Worked examples with real numbers]

## Edge Cases

[To be filled: Special handling for edge cases]

## Complexity

[To be filled: Time/space complexity if relevant]
"""

    elif node.node_type == VALIDATION:
        content_template = """## Test Cases

[To be filled: Specific test cases to validate behavior]

## Success Criteria

[To be filled: What passing looks like]

## Failure Modes

[To be filled: What could go wrong and how to detect]

## Validation Process

[To be filled: How to run these validations]
"""

    elif node.node_type == GUIDE:
        content_template = """## Prerequisites

[To be filled: What you need before following this guide]

## Step-by-Step Instructions

[To be filled: Detailed steps to implement/use]

## Common Pitfalls

[To be filled: What to avoid]

## Troubleshooting

[To be filled: How to resolve common issues]

## Examples

[To be filled: Real-world usage examples]
"""

    elif node.node_type == "ROOT":
        content_template = """## Overview

This is the root of the Token Economics v3 documentation. Navigate through the hierarchy using the children links below.

## Documentation Structure

This documentation follows the knowledge hierarchy:

- **PATTERNS** 📐 - Conceptual frameworks and core insights
- **BEHAVIOR_SPECS** 📋 - What should happen (specifications)
- **MECHANISMS** ⚙️ - How it works (implementation approach)
- **ALGORITHMS** 🔢 - Formulas and calculations
- **VALIDATIONS** ✅ - How we verify correctness
- **GUIDES** 📖 - How to implement/use

## Navigation

Use the parent/children links in each document to explore the hierarchy.
"""

    # Build the complete envelope
    envelope = f"""# {icon} {node.name}

**Type:** {node.node_type}
**Status:** Draft
**Created:** {today}

---

## Navigation

**Parent Path:**
{parent_path if parent_path else "- (Root level)"}

**This Node:**
- {node.name} ({node.node_type})

**Children:**
{children_list}

---

## Relationships

{relationships_section}

---

## Purpose

{node.purpose}

---

{content_template}

---

## References

- [Back to Token Economics Root](../../README.md)
{f"- [Parent: {node.parent.name}](../README.md)" if node.parent else ""}

---

**Last Updated:** {today}
**Maintained By:** Lucia "Goldscale" (Treasury Architect)
"""

    return envelope


def create_structure(node: Node, base_path: Path):
    """Recursively create folder structure and README files."""

    # Create directory for this node
    node_path = base_path / node.slug
    node_path.mkdir(parents=True, exist_ok=True)

    # Generate and write README.md
    envelope_content = generate_envelope(node, base_path)
    readme_path = node_path / "README.md"

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(envelope_content)

    print(f"✅ Created: {readme_path}")

    # Recursively create children
    for child in node.children:
        create_structure(child, node_path)


def main():
    """Main execution."""

    print("🚀 Generating Token Economics v3 Documentation Skeleton\n")

    # Build hierarchy
    print("📐 Building hierarchy...")
    root = build_hierarchy()

    # Base path
    base_path = Path(__file__).parent.parent / "docs" / "v3"
    base_path.mkdir(parents=True, exist_ok=True)

    # Create structure
    print(f"\n📁 Creating structure in: {base_path}\n")
    create_structure(root, base_path.parent)

    # Summary
    def count_nodes(node: Node) -> int:
        count = 1
        for child in node.children:
            count += count_nodes(child)
        return count

    total_nodes = count_nodes(root)

    print(f"\n✨ Done! Created {total_nodes} documentation nodes.")
    print(f"\n📍 Root: {base_path.parent / root.slug / 'README.md'}")
    print(f"\n🔗 Start exploring: cd {base_path.parent / root.slug}")
    print(f"    then: cat README.md\n")


if __name__ == "__main__":
    main()
