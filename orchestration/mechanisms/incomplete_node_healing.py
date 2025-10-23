"""
Incomplete Node Healing - Eligibility + Tasking

Prevents schema-incomplete nodes/links from contaminating traversal/WM while
allowing creation (don't block thinking). Bottom-up approach: detect → task → complete → admit.

Key principle: Eligibility is a READ-TIME FILTER, not a second energy channel.
Single-energy E_i remains the physics; eligibility gates SELECTION.

Eligibility predicate:
    eligible(i) := is_complete(i) ∧ status∈{active} ∧ E_i ≥ Θ_i

Author: Felix (Engineer)
Created: 2025-10-22
Spec: docs/specs/v2/learning_and_trace/incomplete_node_healing.md
Architecture: V2 Single-Energy + Read-Time Filter
"""

import uuid
from typing import Dict, List, Optional, Any, Union, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from orchestration.core.node import Node
    from orchestration.core.link import Link
    from orchestration.core.types import NodeType, LinkType
    from orchestration.core.graph import Graph


# --- Required Fields Registry ---

# Core node types with their required fields
# Based on COMPLETE_TYPE_REFERENCE.md and common usage
REQUIRED_NODE_FIELDS: Dict[str, List[str]] = {
    # Personal types
    "Memory": ["name", "description", "timestamp", "participants"],
    "Realization": ["name", "description", "what_i_realized", "context_when_discovered"],
    "Concept": ["name", "description", "definition"],
    "Principle": ["name", "description", "principle_statement", "why_it_matters"],
    "Mechanism": ["name", "description", "how_it_works", "inputs", "outputs"],

    # Task types
    "Task": ["name", "description", "estimated_hours", "priority"],
    "Goal": ["name", "description"],  # Minimal for now

    # Pattern types
    "Pattern": ["name", "description"],
    "Anti_Pattern": ["name", "description"],

    # Subentity types
    "AI_Agent": ["name", "description", "role", "expertise"],
    "Human": ["name", "description", "role", "expertise"],
    "Subentity": ["name", "description"],

    # Default for unknown types
    "default": ["name", "description"]
}

# Core link types with their required fields
REQUIRED_LINK_FIELDS: Dict[str, List[str]] = {
    "ENABLES": ["source_id", "target_id", "subentity", "enabling_type", "degree_of_necessity"],
    "BLOCKS": ["source_id", "target_id", "subentity", "blocking_condition", "severity"],
    "REQUIRES": ["source_id", "target_id", "subentity", "requirement_criticality"],
    "RELATES_TO": ["source_id", "target_id", "subentity"],  # Minimal generic
    "CONTAINS": ["source_id", "target_id", "subentity"],
    "DIFFUSES_TO": ["source_id", "target_id", "subentity"],
    "SUPPRESS": ["source_id", "target_id", "subentity"],

    # Default for unknown types
    "default": ["source_id", "target_id", "subentity"]
}


# --- Completion Strategies ---

class CompletionStrategy(Enum):
    """Strategies for completing missing fields."""
    CONTEXT_INFERENCE = "context_inference"  # Infer from neighbors
    SCHEMA_DEFAULT = "schema_default"  # Use schema defaults
    LLM_FILL = "llm_fill"  # Ask LLM to fill (future)
    MANUAL = "manual"  # Human intervention required


class TaskStatus(Enum):
    """Status of completion task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


# --- Data Structures ---

@dataclass
class CompletionTask:
    """
    Task to complete an incomplete node/link.

    Fields:
        id: Unique task identifier
        task_type: "complete_node" or "complete_link"
        target_id: Node/link ID to complete
        target_type: NodeType or LinkType (as string)
        missing_fields: List of field names that are missing
        created_at: When task was created
        status: Current task status
        completion_strategy: Which strategy to use
        completion_source: Where completed values came from
        confidence: Confidence in completion (0-1)
        completed_at: When task was completed (None if pending)
    """
    id: str
    task_type: str  # "complete_node" or "complete_link"
    target_id: str
    target_type: str
    missing_fields: List[str]
    created_at: datetime = field(default_factory=datetime.now)
    status: TaskStatus = TaskStatus.PENDING
    completion_strategy: Optional[CompletionStrategy] = None
    completion_source: Optional[str] = None
    confidence: float = 0.0
    completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "task_type": self.task_type,
            "target_id": self.target_id,
            "target_type": self.target_type,
            "missing_fields": self.missing_fields,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
            "completion_strategy": self.completion_strategy.value if self.completion_strategy else None,
            "completion_source": self.completion_source,
            "confidence": round(self.confidence, 4),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


@dataclass
class IncompletenessMetrics:
    """Metrics for incomplete node healing system."""
    incomplete_nodes_by_type: Dict[str, int] = field(default_factory=dict)
    incomplete_links_by_type: Dict[str, int] = field(default_factory=dict)
    tasks_pending: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    median_time_to_complete_ms: float = 0.0
    completion_by_strategy: Dict[str, int] = field(default_factory=dict)
    eligibility_hits: int = 0  # Eligible nodes selected
    eligibility_misses: int = 0  # Ineligible nodes filtered


# --- Validation Functions ---

def is_node_complete(node: 'Node') -> bool:
    """
    Check if node has all required fields for its type.

    Args:
        node: Node to validate

    Returns:
        True if all required fields present and non-empty

    Example:
        >>> node = Node(id="n1", name="Test", node_type=NodeType.CONCEPT, description="...")
        >>> is_node_complete(node)
        False  # Missing 'definition' field for CONCEPT type
    """
    # Get required fields for this node type
    node_type_str = node.node_type.value if hasattr(node.node_type, 'value') else str(node.node_type)
    required_fields = REQUIRED_NODE_FIELDS.get(node_type_str, REQUIRED_NODE_FIELDS["default"])

    # Check each required field
    for field_name in required_fields:
        # Try to get field value
        if hasattr(node, field_name):
            value = getattr(node, field_name)
        else:
            # Check in properties dict
            value = node.properties.get(field_name)

        # Field missing or empty
        if value is None:
            return False
        if isinstance(value, str) and value.strip() == "":
            return False

    return True


def is_link_complete(link: 'Link') -> bool:
    """
    Check if link has all required fields for its type.

    Args:
        link: Link to validate

    Returns:
        True if all required fields present and non-empty

    Example:
        >>> link = Link(id="l1", source_id="n1", target_id="n2", link_type=LinkType.ENABLES)
        >>> is_link_complete(link)
        False  # Missing 'enabling_type' and 'degree_of_necessity'
    """
    # Get required fields for this link type
    link_type_str = link.link_type.value if hasattr(link.link_type, 'value') else str(link.link_type)
    required_fields = REQUIRED_LINK_FIELDS.get(link_type_str, REQUIRED_LINK_FIELDS["default"])

    # Check each required field
    for field_name in required_fields:
        # Try to get field value
        if hasattr(link, field_name):
            value = getattr(link, field_name)
        else:
            # Check in properties dict
            value = link.properties.get(field_name)

        # Field missing or empty
        if value is None:
            return False
        if isinstance(value, str) and value.strip() == "":
            return False

    return True


def get_missing_fields(obj: Union['Node', 'Link']) -> List[str]:
    """
    Get list of missing required fields for a node or link.

    Args:
        obj: Node or Link to check

    Returns:
        List of field names that are missing or empty

    Example:
        >>> missing = get_missing_fields(node)
        >>> missing
        ['definition', 'confidence']
    """
    from orchestration.core.node import Node

    # Determine type and get required fields
    if isinstance(obj, Node):
        type_str = obj.node_type.value if hasattr(obj.node_type, 'value') else str(obj.node_type)
        required_fields = REQUIRED_NODE_FIELDS.get(type_str, REQUIRED_NODE_FIELDS["default"])
    else:  # Link
        type_str = obj.link_type.value if hasattr(obj.link_type, 'value') else str(obj.link_type)
        required_fields = REQUIRED_LINK_FIELDS.get(type_str, REQUIRED_LINK_FIELDS["default"])

    missing = []
    for field_name in required_fields:
        # Try to get field value
        if hasattr(obj, field_name):
            value = getattr(obj, field_name)
        else:
            value = obj.properties.get(field_name)

        # Check if missing or empty
        if value is None or (isinstance(value, str) and value.strip() == ""):
            missing.append(field_name)

    return missing


# --- Eligibility Predicate ---

def is_eligible(obj: Union['Node', 'Link']) -> bool:
    """
    Check if node/link is eligible for traversal/WM selection.

    Eligibility predicate (from spec):
        eligible(i) := is_complete(i) ∧ status∈{active} ∧ E_i ≥ Θ_i

    This is a READ-TIME FILTER. Energy dynamics unchanged.

    Args:
        obj: Node or Link to check

    Returns:
        True if eligible for selection

    Example:
        >>> if is_eligible(node):
        ...     candidates.append(node)  # Can be selected
        ... else:
        ...     # Skip incomplete/ineligible node
    """
    from orchestration.core.node import Node

    # 1. Completeness check
    if isinstance(obj, Node):
        if not is_node_complete(obj):
            return False
    else:  # Link
        if not is_link_complete(obj):
            return False

    # 2. Status check (not deleted/archived)
    # Check properties for status field
    status = obj.properties.get('status', 'active')
    if status not in ['active']:
        return False

    # 3. Activation check (only for nodes - links don't have energy)
    if isinstance(obj, Node):
        if obj.E < obj.theta:
            return False

    return True


# --- Task Management ---

def create_completion_task(
    obj: Union['Node', 'Link'],
    missing_fields: Optional[List[str]] = None
) -> CompletionTask:
    """
    Create task to complete an incomplete node/link.

    Args:
        obj: Node or Link that needs completion
        missing_fields: Optional list of missing fields (auto-detected if None)

    Returns:
        CompletionTask ready to be assigned

    Example:
        >>> task = create_completion_task(incomplete_node)
        >>> task_registry.append(task)
        >>> # Later: complete_task(task, graph)
    """
    from orchestration.core.node import Node

    if missing_fields is None:
        missing_fields = get_missing_fields(obj)

    task_type = "complete_node" if isinstance(obj, Node) else "complete_link"

    if isinstance(obj, Node):
        target_type = obj.node_type.value if hasattr(obj.node_type, 'value') else str(obj.node_type)
    else:
        target_type = obj.link_type.value if hasattr(obj.link_type, 'value') else str(obj.link_type)

    task = CompletionTask(
        id=f"task_{uuid.uuid4().hex[:8]}",
        task_type=task_type,
        target_id=obj.id,
        target_type=target_type,
        missing_fields=missing_fields
    )

    return task


# --- Completion Strategies ---

def complete_with_defaults(
    obj: Union['Node', 'Link'],
    missing_fields: List[str]
) -> Dict[str, Any]:
    """
    Complete missing fields with schema defaults.

    Strategy: Use sensible defaults based on field name and type.

    Args:
        obj: Node or Link to complete
        missing_fields: List of field names to fill

    Returns:
        Dictionary of {field_name: default_value}

    Example:
        >>> defaults = complete_with_defaults(node, ["definition", "confidence"])
        >>> defaults
        {"definition": "Auto-generated definition", "confidence": 0.5}
    """
    from orchestration.core.node import Node

    defaults = {}

    for field_name in missing_fields:
        # Type-specific defaults
        if field_name == "definition":
            defaults[field_name] = f"Auto-generated definition for {obj.name if hasattr(obj, 'name') else obj.id}"
        elif field_name == "description":
            defaults[field_name] = f"Auto-generated description for {obj.name if hasattr(obj, 'name') else obj.id}"
        elif field_name == "confidence":
            defaults[field_name] = 0.5  # Medium confidence for auto-filled
        elif field_name == "timestamp":
            defaults[field_name] = datetime.now()
        elif field_name == "participants":
            defaults[field_name] = []
        elif field_name == "what_i_realized":
            defaults[field_name] = "Insight content not yet captured"
        elif field_name == "context_when_discovered":
            defaults[field_name] = "Context not yet recorded"
        elif field_name == "principle_statement":
            defaults[field_name] = "Principle statement to be defined"
        elif field_name == "why_it_matters":
            defaults[field_name] = "Importance to be articulated"
        elif field_name == "how_it_works":
            defaults[field_name] = "Mechanism details to be documented"
        elif field_name == "inputs":
            defaults[field_name] = "Inputs to be specified"
        elif field_name == "outputs":
            defaults[field_name] = "Outputs to be specified"
        elif field_name == "estimated_hours":
            defaults[field_name] = 1.0  # Default 1 hour
        elif field_name == "priority":
            defaults[field_name] = "medium"
        elif field_name == "role":
            defaults[field_name] = "unspecified"
        elif field_name == "expertise":
            defaults[field_name] = []
        elif field_name == "enabling_type":
            defaults[field_name] = "facilitator"
        elif field_name == "degree_of_necessity":
            defaults[field_name] = "helpful"
        elif field_name == "blocking_condition":
            defaults[field_name] = "Blocking condition to be defined"
        elif field_name == "severity":
            defaults[field_name] = "partial"
        elif field_name == "requirement_criticality":
            defaults[field_name] = "important"
        else:
            # Generic default
            defaults[field_name] = f"[Auto-filled: {field_name}]"

    return defaults


def complete_from_context(
    graph: 'Graph',
    obj: Union['Node', 'Link'],
    missing_fields: List[str]
) -> Dict[str, Any]:
    """
    Complete missing fields by inferring from neighboring nodes.

    Strategy: Look at neighbors of same type, find common patterns.

    Args:
        graph: Graph for context
        obj: Node or Link to complete
        missing_fields: List of field names to infer

    Returns:
        Dictionary of {field_name: inferred_value}

    Example:
        >>> inferred = complete_from_context(graph, node, ["definition"])
        >>> inferred
        {"definition": "Similar to neighboring concept X"}
    """
    # TODO: Implement context-based inference
    # For now, fall back to defaults
    return complete_with_defaults(obj, missing_fields)


def complete_task(
    task: CompletionTask,
    graph: 'Graph',
    strategy: CompletionStrategy = CompletionStrategy.SCHEMA_DEFAULT
) -> bool:
    """
    Execute completion task using specified strategy.

    Args:
        task: CompletionTask to execute
        graph: Graph containing the incomplete object
        strategy: Which completion strategy to use

    Returns:
        True if completion successful, False otherwise

    Side effects:
        - Updates object with completed fields
        - Updates task status and metadata

    Example:
        >>> success = complete_task(task, graph, CompletionStrategy.SCHEMA_DEFAULT)
        >>> if success:
        ...     print(f"Completed with confidence {task.confidence}")
    """
    from orchestration.core.node import Node

    # Get target object
    if task.task_type == "complete_node":
        obj = graph.nodes.get(task.target_id)
    else:  # complete_link
        obj = graph.links.get(task.target_id)

    if obj is None:
        task.status = TaskStatus.FAILED
        task.completion_source = "target_not_found"
        return False

    # Apply completion strategy
    if strategy == CompletionStrategy.SCHEMA_DEFAULT:
        completions = complete_with_defaults(obj, task.missing_fields)
        confidence = 0.5  # Medium confidence for defaults
    elif strategy == CompletionStrategy.CONTEXT_INFERENCE:
        completions = complete_from_context(graph, obj, task.missing_fields)
        confidence = 0.7  # Higher confidence for context-based
    else:
        # Strategy not implemented
        task.status = TaskStatus.FAILED
        task.completion_source = f"strategy_{strategy.value}_not_implemented"
        return False

    # Apply completions to object
    for field_name, value in completions.items():
        if hasattr(obj, field_name):
            setattr(obj, field_name, value)
        else:
            # Store in properties
            obj.properties[field_name] = value

    # Update task
    task.status = TaskStatus.COMPLETED
    task.completion_strategy = strategy
    task.completion_source = strategy.value
    task.confidence = confidence
    task.completed_at = datetime.now()

    return True


# --- Validation on Creation ---

def validate_and_mark_incomplete(obj: Union['Node', 'Link']) -> Optional[List[str]]:
    """
    Validate object completeness and mark as incomplete if needed.

    Call this on node/link creation to detect incompleteness early.

    Args:
        obj: Node or Link to validate

    Returns:
        List of missing fields if incomplete, None if complete

    Side effects:
        Sets obj.properties['is_incomplete'] = True if incomplete
        Sets obj.properties['missing_fields'] = missing field list

    Example:
        >>> node = create_node(...)
        >>> missing = validate_and_mark_incomplete(node)
        >>> if missing:
        ...     task = create_completion_task(node, missing)
    """
    missing_fields = get_missing_fields(obj)

    if missing_fields:
        # Mark as incomplete
        obj.properties['is_incomplete'] = True
        obj.properties['missing_fields'] = missing_fields
        return missing_fields
    else:
        # Mark as complete
        obj.properties['is_incomplete'] = False
        obj.properties['missing_fields'] = []
        return None
