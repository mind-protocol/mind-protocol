# orchestration/runtime/citizen_registry.py
from typing import List
import os, json
from orchestration.config.settings import settings
from orchestration.adapters.storage.graph_store import FalkorDBGraphStore
from orchestration.bus.emit import emit_failure  # your fail-loud helper

def get_all_citizen_ids() -> List[str]:
    """
    Resolves active citizens:
      1) CITIZENS_JSON (explicit list)
      2) Org graph query (active citizens)
      3) Fail loudly (no silent defaults)
    """
    j = os.getenv("CITIZENS_JSON")
    if j:
        try:
            ids = json.loads(j)
            assert isinstance(ids, list) and all(isinstance(x, str) for x in ids)
            return ids
        except Exception as e:
            emit_failure(component="citizen_registry.get_all_citizen_ids",
                         reason="env_parse_error", detail=str(e),
                         span={"file": __file__})

    try:
        store = FalkorDBGraphStore(url=settings.FALKORDB_URL, graph_name=None)
        rs = store.query("""MATCH (c:Citizen {active:true}) RETURN c.id ORDER BY c.id""").result_set
        ids = [row[0] for row in rs]
        if ids:
            return ids
    except Exception as e:
        emit_failure(component="citizen_registry.get_all_citizen_ids",
                     reason="org_query_error", detail=str(e),
                     span={"file": __file__})

    raise RuntimeError("No active citizens resolved (no CITIZENS_JSON and org graph empty)")
