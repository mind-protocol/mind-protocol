# orchestration/config/graph_names.py
from dataclasses import dataclass
import re
from .settings import settings

_GRAPH_RE = re.compile(r"^[a-z0-9-]+_[a-z0-9-]+_[a-z0-9_-]+$")

@dataclass(frozen=True)
class GraphNameResolver:
    ecosystem: str = "consciousness-infrastructure"
    org: str = "mind-protocol"

    def citizen(self, citizen_id: str) -> str:
        name = f"{self.ecosystem}_{self.org}_{citizen_id}"
        assert _GRAPH_RE.match(name), f"Invalid graph name: {name}"
        return name

resolver = GraphNameResolver()  # ecosystem/org can be moved to env later

def graph_name_for_citizen(citizen_id: str) -> str:
    return resolver.citizen(citizen_id)
