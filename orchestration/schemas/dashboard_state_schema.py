"""
Dashboard State Schema - 1Hz Aggregated State for UI

The dashboard.state.emit event provides complete system state at 1Hz.
UI subscribes to ONE topic and gets everything: citizens, health, L4 protocol.

Topic: ecosystem/{ecosystem_id}/org/{org_id}/dashboard/state

Author: Felix (Core Consciousness Engineer) + Ada (Architecture)
Date: 2025-10-30
"""

from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


# === Citizen State ===

class CitizenStatus(BaseModel):
    """Current work context for a citizen."""
    mission_id: Optional[str] = None
    incident_id: Optional[str] = None
    files: List[str] = Field(default_factory=list)
    note: Optional[str] = None  # "Fixing /checkout timeout"
    workspace: Optional[str] = None  # "frontend/components"
    content_hash: str = Field(..., description="SHA256 for idempotency")


class CitizenState(BaseModel):
    """Complete state for one citizen."""
    id: str  # "mind-protocol_atlas"
    name: str  # "Atlas" (display name)
    awake: Literal["awake", "sleeping", "stale"]
    last_seen: str  # ISO 8601 timestamp
    ttl_s: int = 90  # Staleness threshold

    # Status (from status.activity.emit)
    status: Optional[CitizenStatus] = None

    # Messages
    threads_unread: int = 0
    threads: List[Dict] = Field(default_factory=list)  # [{thread_id, subject, unread_count, last_msg}]

    # Credits (optional Phase-0)
    credits: Optional[float] = None
    budget_account_id: Optional[str] = None

    # Identity (SubEntity structure)
    top_subentities: List[Dict] = Field(default_factory=list)  # [{role, w_total}] top 3

    # Thought (current working memory)
    wm_nodes: List[str] = Field(default_factory=list)  # Node IDs in WM (max 7-12)


# === Health State ===

class LinkHealth(BaseModel):
    """Link health metrics from health.link.snapshot."""
    ack_rate: float = Field(..., ge=0.0, le=1.0)  # Target: ≥ 0.99
    p50_rtt_ms: float  # p50 round-trip time
    p95_rtt_ms: float  # Target: ≤ 250ms
    p99_rtt_ms: float  # Alert: > 600ms
    loss: float = Field(..., ge=0.0, le=1.0)  # Packet loss rate
    jitter_ms: float  # RTT variance
    route_mismatches: int = 0  # Target: 0


class ComplianceHealth(BaseModel):
    """Compliance metrics from health.compliance.snapshot."""
    reject_rate: float = Field(..., ge=0.0, le=1.0)  # Target: ≤ 0.02 (2%)
    top_rejects: List[List] = Field(default_factory=list)  # [["unknown_spec_rev", 12], ...]
    accept_count: int
    reject_count: int


class BroadcasterHealth(BaseModel):
    """SafeBroadcaster metrics."""
    emit_success_rate: float = Field(..., ge=0.0, le=1.0)  # Target: ≥ 0.99
    spill_depth: int  # Target: ≤ 100, alert: > 1000
    last_flush: Optional[str] = None  # ISO 8601 timestamp
    last_heartbeat: str  # ISO 8601 timestamp


class HealthState(BaseModel):
    """Complete health snapshot."""
    link: LinkHealth
    compliance: ComplianceHealth
    broadcaster: BroadcasterHealth


# === L4 Protocol State ===

class L4State(BaseModel):
    """L4 protocol graph statistics."""
    schemas_count: int  # Event_Schema nodes
    namespaces_count: int  # Distinct namespaces
    governance_policies: int  # Governance_Policy nodes
    governed: bool  # All schemas have governance


# === Complete Dashboard State ===

class DashboardState(BaseModel):
    """
    Complete dashboard state emitted at 1Hz.

    Topic: ecosystem/{eco}/org/{org}/dashboard/state
    Frequency: 1Hz ± 50ms

    Example subscription:
        ws.send({"type": "subscribe@1.0", "topics": ["ecosystem/mindnet/org/mind-protocol/dashboard/state"]})
    """
    citizens: List[CitizenState]
    health: HealthState
    l4: L4State
    ts: str  # ISO 8601 timestamp of emission

    class Config:
        json_schema_extra = {
            "example": {
                "citizens": [
                    {
                        "id": "mind-protocol_atlas",
                        "name": "Atlas",
                        "awake": "awake",
                        "last_seen": "2025-10-30T12:34:56.789Z",
                        "ttl_s": 90,
                        "status": {
                            "mission_id": None,
                            "incident_id": "inc_1234",
                            "files": ["frontend/components/Wall.tsx"],
                            "note": "Fixing dashboard 0 nodes issue",
                            "workspace": "frontend/*",
                            "content_hash": "abc123..."
                        },
                        "threads_unread": 2,
                        "threads": [
                            {"thread_id": "th_1", "subject": "Re: Dashboard fix", "unread_count": 1, "last_msg": "..."}
                        ],
                        "credits": 123.0,
                        "top_subentities": [
                            {"role": "infrastructure_builder", "w_total": 0.92},
                            {"role": "debugger", "w_total": 0.88}
                        ],
                        "wm_nodes": ["node_1", "node_2", "node_3"]
                    }
                ],
                "health": {
                    "link": {
                        "ack_rate": 0.998,
                        "p50_rtt_ms": 42,
                        "p95_rtt_ms": 84,
                        "p99_rtt_ms": 156,
                        "loss": 0.0,
                        "jitter_ms": 12,
                        "route_mismatches": 0
                    },
                    "compliance": {
                        "reject_rate": 0.006,
                        "top_rejects": [["unknown_spec_rev", 12], ["payload_exceeds_limit", 3]],
                        "accept_count": 1650,
                        "reject_count": 10
                    },
                    "broadcaster": {
                        "emit_success_rate": 0.999,
                        "spill_depth": 5,
                        "last_flush": "2025-10-30T12:30:00.000Z",
                        "last_heartbeat": "2025-10-30T12:34:56.789Z"
                    }
                },
                "l4": {
                    "schemas_count": 16,
                    "namespaces_count": 3,
                    "governance_policies": 5,
                    "governed": True
                },
                "ts": "2025-10-30T12:34:56.789Z"
            }
        }


# === Emission Helpers ===

def build_dashboard_state(
    citizens: List[CitizenState],
    link_health: LinkHealth,
    compliance_health: ComplianceHealth,
    broadcaster_health: BroadcasterHealth,
    l4_stats: L4State
) -> DashboardState:
    """Build complete dashboard state for emission."""
    return DashboardState(
        citizens=citizens,
        health=HealthState(
            link=link_health,
            compliance=compliance_health,
            broadcaster=broadcaster_health
        ),
        l4=l4_stats,
        ts=datetime.utcnow().isoformat() + "Z"
    )
