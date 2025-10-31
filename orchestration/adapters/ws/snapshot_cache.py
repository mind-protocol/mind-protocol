from collections import defaultdict
import time

class SnapshotCache:
    """
    A cache to store the latest snapshot of nodes and links for each citizen.
    This allows replaying the full graph state to newly connected clients.
    """
    def __init__(self):
        self.nodes = defaultdict(dict)  # citizen_id -> {node_id -> node_data}
        self.links = defaultdict(dict)  # citizen_id -> {link_key -> link_data}
        self.subentities = defaultdict(dict) # citizen_id -> {subentity_id -> subentity_data}
        self.ts = {}                    # citizen_id -> last_update_timestamp

    def upsert_node(self, citizen_id: str, node: dict):
        """Upserts a node into the cache."""
        node_id = node.get("id")
        if not node_id:
            return
        self.nodes[citizen_id][node_id] = node
        self.ts[citizen_id] = time.time()

    def upsert_link(self, citizen_id: str, link: dict):
        """Upserts a link into the cache."""
        source = link.get("source")
        target = link.get("target")
        if not source or not target:
            return
        # Create a unique key for the link to handle upserts
        link_key = f'{source}->{target}:{link.get("type", "")}'
        self.links[citizen_id][link_key] = link
        self.ts[citizen_id] = time.time()

    def upsert_subentity(self, citizen_id: str, subentity: dict):
        """Upserts a subentity into the cache."""
        subentity_id = subentity.get("id")
        if not subentity_id:
            return
        self.subentities[citizen_id][subentity_id] = subentity
        self.ts[citizen_id] = time.time()

    def build_snapshot(self, citizen_id: str) -> dict:
        """Builds a full snapshot for a given citizen."""
        if citizen_id not in self.nodes and citizen_id not in self.links and citizen_id not in self.subentities:
            return {
                "citizen_id": citizen_id,
                "nodes": [],
                "links": [],
                "subentities": [],
                "ts": None
            }
        
        return {
            "citizen_id": citizen_id,
            "nodes": list(self.nodes[citizen_id].values()),
            "links": list(self.links[citizen_id].values()),
            "subentities": list(self.subentities[citizen_id].values()),
            "ts": self.ts.get(citizen_id)
        }

    def get_all_citizen_ids(self) -> list[str]:
        """Returns a list of all citizen IDs present in the cache."""
        return list(set(list(self.nodes.keys()) + list(self.links.keys()) + list(self.subentities.keys())))

# Global instance to be used by the application
snapshot_cache = SnapshotCache()

def get_snapshot_cache():
    """Returns the global snapshot_cache instance."""
    return snapshot_cache