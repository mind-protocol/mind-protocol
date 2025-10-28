"""
Budget policy loader.
"""

from __future__ import annotations

import asyncio
import ast
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from falkordb import FalkorDB  # type: ignore

from orchestration.core import settings as core_settings

logger = logging.getLogger(__name__)


_SAFE_NAMES = {
    "min": min,
    "max": max,
    "abs": abs,
    "pow": pow,
}


class PolicyExpressionError(Exception):
    """Raised when a policy formula cannot be evaluated safely."""


def _compile_formula(formula: str) -> ast.AST:
    try:
        expr = ast.parse(formula, mode="eval")
    except SyntaxError as exc:  # pragma: no cover - defensive
        raise PolicyExpressionError(f"Invalid policy formula: {formula!r}") from exc

    for node in ast.walk(expr):
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in _SAFE_NAMES:
                raise PolicyExpressionError(f"Disallowed function in policy formula: {formula!r}")
        elif isinstance(
            node,
            (
                ast.Expression,
                ast.BinOp,
                ast.UnaryOp,
                ast.Num,
                ast.Name,
                ast.Compare,
                ast.BoolOp,
                ast.IfExp,
                ast.Load,
            ),
        ):
            continue
        else:
            raise PolicyExpressionError(f"Disallowed expression in policy formula: {formula!r}")

    return expr


def _safe_eval(expr: ast.AST, context: Dict[str, Any]) -> float:
    value = eval(compile(expr, "<policy>", "eval"), {"__builtins__": {}}, {**_SAFE_NAMES, **context})  # noqa: P204
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise PolicyExpressionError(f"Policy formula produced non-numeric value {value!r}") from exc


@dataclass(order=True)
class BudgetPolicy:
    """Represents a budget policy node from FalkorDB."""

    priority: int
    lane: str = field(compare=False)
    formula_raw: str = field(compare=False)
    min_floor_mind: float = field(compare=False, default=0.0)
    extras: Dict[str, Any] = field(compare=False, default_factory=dict)
    _expr: ast.AST = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        self._expr = _compile_formula(self.formula_raw)

    def evaluate(self, context: Dict[str, Any]) -> float:
        return _safe_eval(self._expr, context)


class BudgetPolicyManager:
    """Loads and caches budget policies for an organization."""

    def __init__(self, *, graph: str) -> None:
        self._db = FalkorDB(host=core_settings.FALKORDB_HOST, port=core_settings.FALKORDB_PORT)
        self._graph = self._db.select_graph(graph)
        self._policies: List[BudgetPolicy] = []
        self._lock = asyncio.Lock()
        self._last_refresh: float = 0.0

    @property
    def policies(self) -> List[BudgetPolicy]:
        return list(self._policies)

    async def refresh(self) -> None:
        async with self._lock:
            result = await asyncio.to_thread(self._graph.query, "MATCH (p:Budget_Policy) RETURN p")
            rows = getattr(result, "result_set", result)
            policies: List[BudgetPolicy] = []

            if rows:
                for row in rows:
                    node = row[0]
                    props = getattr(node, "properties", {})
                    lane = props.get("lane")
                    formula = props.get("policy_formula")
                    if not lane or not formula:
                        continue
                    min_floor = float(props.get("min_floor_mind", 0.0))
                    priority = int(props.get("priority", 0))
                    extras = {
                        key: value
                        for key, value in props.items()
                        if key not in {"lane", "policy_formula", "min_floor_mind", "priority"}
                    }
                    try:
                        policies.append(
                            BudgetPolicy(
                                priority=priority,
                                lane=str(lane),
                                formula_raw=str(formula),
                                min_floor_mind=min_floor,
                                extras=extras,
                            )
                        )
                    except PolicyExpressionError as exc:
                        logger.warning("Skipping invalid budget policy (%s): %s", lane, exc)

            policies.sort()
            self._policies = policies
            self._last_refresh = time.time()
            logger.info("Budget policies loaded: %s", [p.lane for p in policies])

    async def ensure_loaded(self) -> None:
        if not self._policies:
            await self.refresh()

    def needs_refresh(self, interval_seconds: int) -> bool:
        return (time.time() - self._last_refresh) >= interval_seconds
