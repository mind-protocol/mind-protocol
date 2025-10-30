"""
MPSv3 - Mind Protocol Supervisor v3

Centralized process management replacing guardian.py + launcher.py.

Components:
- singleton.py: OS-level lease (Windows mutex / POSIX flock)
- backoff.py: Exponential backoff with quarantine
- runner.py: Service lifecycle with process groups
- watcher.py: Centralized file watching
- registry.py: Service coordination
- services.yaml: Service specifications

Author: Atlas
Date: 2025-10-25
"""

from .singleton import SingletonLease
from .backoff import BackoffState, QuarantineRequired
from .runner import ServiceRunner, ServiceSpec
from .watcher import CentralizedFileWatcher
from .registry import ServiceRegistry

__all__ = [
    "SingletonLease",
    "BackoffState",
    "QuarantineRequired",
    "ServiceRunner",
    "ServiceSpec",
    "CentralizedFileWatcher",
    "ServiceRegistry",
]
