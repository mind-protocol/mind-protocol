# orchestration/config/graph_names.py
from dataclasses import dataclass
import re

_GRAPH_RE = re.compile(r"^[a-z0-9-]+(_[a-z0-9_-]+)?$")

@dataclass(frozen=True)
class GraphNameResolver:
    org: str = "mind-protocol"

    def citizen(self, citizen_id: str) -> str:
        """mind-protocol_felix"""
        name = f"{self.org}_{citizen_id}"
        assert _GRAPH_RE.match(name), f"Invalid graph name: {name}"
        return name

    def collective(self) -> str:
        """mind-protocol_collective (L2 org graph)"""
        return f"{self.org}_collective"

    def org_base(self) -> str:
        """mind-protocol_org (org base graph)"""
        return f"{self.org}_org"

    @staticmethod
    def protocol() -> str:
        """protocol (L4 schemas)"""
        return "protocol"

    @staticmethod
    def schema_registry() -> str:
        """schema_registry"""
        return "schema_registry"

resolver = GraphNameResolver()

def graph_name_for_citizen(citizen_id: str) -> str:
    return resolver.citizen(citizen_id)
