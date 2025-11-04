"""
L2 View Resolvers - Projection Functions (Phase B: Project, Phase C: Render)

Transform Cypher results into render-agnostic view models, then adapt to format.

Split:
- Phase B (Project): Normalize to view-model (cacheable, format-agnostic)
- Phase C (Render): Adapt to json/mdx/html (priced differently per CPS-1)

Author: Mel "Bridgekeeper"
Date: 2025-11-04
"""

import hashlib
import json
from typing import List, Dict, Any
from html import escape


# ============================================================================
# Shared Helpers
# ============================================================================

def ko_digest(rows: List[Dict], key_fields=("id", "labels", "path", "sha", "rev")) -> str:
    """
    Hash only identity + stable props to avoid churn on irrelevant fields.

    Excludes volatile props (timestamps, counters) for deterministic digests.
    """
    stable = []
    for r in rows:
        stable.append({k: r.get(k) for k in key_fields if k in r})

    digest_input = json.dumps(stable, sort_keys=True).encode()
    return "sha256:" + hashlib.sha256(digest_input).hexdigest()


# ============================================================================
# Phase B: Projection Functions (view_type → view_model)
# ============================================================================

def project_architecture(rows: List[Dict]) -> Dict[str, Any]:
    """
    Architecture view: services, layers, dependencies

    Input rows: [{s: {id, name}, ly: {name}, deps: [{id, name}]}]
    Output: {services: [...], provenance: {ko_digest}}
    """
    services = {}

    for r in rows:
        s = r["s"]
        ly = r.get("ly")
        deps = r.get("deps", [])
        sid = s["id"]

        services.setdefault(sid, {
            "id": sid,
            "name": s["name"],
            "layer": getattr(ly, "name", None) if ly else None,
            "deps": set()
        })

        for t in deps:
            services[sid]["deps"].add(t["id"])

    vm = {
        "services": [
            {
                "id": k,
                "name": v["name"],
                "layer": v["layer"],
                "deps": sorted(v["deps"])
            }
            for k, v in services.items()
        ]
    }

    vm["provenance"] = {"ko_digest": ko_digest(rows)}
    return vm


def project_api(rows: List[Dict]) -> Dict[str, Any]:
    """
    API reference view: endpoints, implementations, schemas

    Input rows: [{ep: {name, path}, ca: {path, service}, schemas: [{name, id}]}]
    Output: {services: [...], provenance: {ko_digest}}
    """
    out = {}

    for r in rows:
        ep = r["ep"]
        ca = r["ca"]
        schemas = r.get("schemas", [])

        svc = ca.get("service", "unknown")

        out.setdefault(svc, []).append({
            "endpoint": ep["name"],
            "path": ep.get("path"),
            "impl": ca["path"],
            "schemas": [{"name": s["name"], "id": s["id"]} for s in schemas]
        })

    vm = {
        "services": [
            {"service": s, "endpoints": eps}
            for s, eps in out.items()
        ]
    }

    vm["provenance"] = {"ko_digest": ko_digest(rows)}
    return vm


def project_coverage(rows: List[Dict]) -> Dict[str, Any]:
    """
    Coverage view: node counts by type + test coverage

    Input rows: [{type: str, count: int, tests: int}]
    Output: {types: [...], summary: {...}, provenance: {ko_digest}}
    """
    vm = {
        "types": [
            {
                "type": r["type"],
                "count": r["count"],
                "tests": r.get("tests", 0)
            }
            for r in rows
        ]
    }

    vm["summary"] = {
        "total_nodes": sum(r["count"] for r in rows),
        "tested_artifacts": sum(r.get("tests", 0) for r in rows)
    }

    vm["provenance"] = {"ko_digest": ko_digest(rows)}
    return vm


def project_index(rows: List[Dict]) -> Dict[str, Any]:
    """
    Index view: browseable KO catalog

    Input rows: [{name: str, kind: str, path: str}]
    Output: {items: [...], provenance: {ko_digest}}
    """
    items = [
        {"name": r["name"], "kind": r["kind"], "path": r["path"]}
        for r in rows
    ]

    return {
        "items": items,
        "provenance": {"ko_digest": ko_digest(rows)}
    }


# Registry: view_type → projection function
PROJECTORS = {
    "architecture": project_architecture,
    "api-reference": project_api,
    "coverage": project_coverage,
    "index": project_index
}


def project(view_type: str, rows: List[Dict]) -> Dict[str, Any]:
    """Get projection function and apply to rows"""
    if view_type not in PROJECTORS:
        raise ValueError(f"Unknown view_type: {view_type}. Available: {list(PROJECTORS.keys())}")
    return PROJECTORS[view_type](rows)


# ============================================================================
# Phase C: Render Adapters (format-specific)
# ============================================================================

def render(view_model: Dict[str, Any], fmt: str) -> Any:
    """
    Adapt view_model to requested format.

    Pricing (CPS-1):
    - json → 0.05 $MIND ("tool request")
    - mdx/html → 5.0 $MIND/page ("doc generation")
    """
    if fmt == "json":
        return view_model

    elif fmt == "mdx":
        # Simple MDX adapter (swap for MDX components later)
        items = view_model.get("services") or view_model.get("items") or []

        body_lines = []
        for item in items:
            if isinstance(item, str):
                body_lines.append(f"- {item}")
            else:
                name = item.get('name') or item.get('service') or 'item'
                body_lines.append(f"- {name}")

        body = "\n".join(body_lines)
        title = view_model.get('title', 'View')

        return f"# {title}\n\n{body}\n"

    elif fmt == "html":
        # Simple HTML adapter (wrap JSON in <pre>)
        json_str = json.dumps(view_model, indent=2)
        return f"<pre>{escape(json_str)}</pre>"

    else:
        raise ValueError(f"Unsupported format: {fmt}. Supported: json, mdx, html")
