"""
Core package for Mind Protocol orchestration layer.

Data Structures (pure):
- Node: Graph nodes with multi-energy + bitemporal tracking
- Link: Directed relationships with bitemporal tracking
- Subentity: Multi-scale consciousness neighborhoods (Phase 7)
- Graph: Container for nodes, subentities, and links

Infrastructure:
- settings: Centralized configuration
- logging: Structured JSON logging
- events: Event schemas (Python ↔ TypeScript contract)
- health: Health check utilities

These are PURE DATA STRUCTURES + INFRASTRUCTURE - no mechanism logic.
All behavior is implemented in mechanisms/ and services/ packages.

Authors: Felix (Engineer), Ada (Architect)
Created: 2025-10-19
Updated: 2025-10-22 (Ada: added infrastructure modules)
Architecture: Phase 1 Clean Break + Phase 7 Multi-Scale
"""

# Data structures
from .node import Node
from .link import Link
from .subentity import Subentity
from .graph import Graph
from .types import NodeType, LinkType

# Infrastructure
from .settings import Settings, settings
from .logging import configure_logging, log_with_fields
from .events import (
    EventType,
    BaseEvent,
    FrameStartEvent,
    FrameCompleteEvent,
    NodeActivatedEvent,
    LinkTraversedEvent,
    EntityActivatedEvent,
    EntityEnergyUpdateEvent,
    SystemStatusEvent,
    ErrorEvent,
    GraphUpdateEvent,
    create_event,
)
from .health import HealthStatus, HealthCheckResult, HealthProbe, run_health_server

__all__ = [
    # Data structures
    'Node',
    'Link',
    'Subentity',
    'Graph',
    'NodeType',
    'LinkType',
    # Infrastructure
    'Settings',
    'settings',
    'configure_logging',
    'log_with_fields',
    'EventType',
    'BaseEvent',
    'FrameStartEvent',
    'FrameCompleteEvent',
    'NodeActivatedEvent',
    'LinkTraversedEvent',
    'EntityActivatedEvent',
    'EntityEnergyUpdateEvent',
    'SystemStatusEvent',
    'ErrorEvent',
    'GraphUpdateEvent',
    'create_event',
    'HealthStatus',
    'HealthCheckResult',
    'HealthProbe',
    'run_health_server',
]
