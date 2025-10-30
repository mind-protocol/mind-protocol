"""
Configuration Management for Doc Ingestion Pipeline

Single source of truth for all thresholds, chunk sizes, URIs, and operational parameters.
Supports environment variable overrides and runtime CLI overrides.

Key features:
- Centralized thresholds (confidence levels, QA cadence)
- Chunk size configuration (target, max)
- FalkorDB connection settings
- Environment variable support with defaults
- Runtime override support for CLI flags
- Pretty-print for status reporting

Author: Atlas (Infrastructure Engineer)
Date: 2025-10-29
Spec: docs/SPEC DOC INPUT.md
"""

import os
import json
from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any


@dataclass
class ChunkConfig:
    """Markdown chunking configuration."""
    target_tokens: int = 250  # Target chunk size
    max_tokens: int = 480     # Maximum chunk size (hard limit)
    preserve_code_fences: bool = True  # Keep ``` blocks intact


@dataclass
class ConfidenceThresholds:
    """Confidence thresholds for link operations."""
    create_task: float = 0.5          # MIN_CONF_CREATE_TASK: Below this → create QA task
    propose_link: float = 0.6         # MIN_CONF_PROPOSE_LINK: Above this → propose link
    autoconfirm: float = 0.9          # MIN_CONF_AUTOCONFIRM: Above this → auto-confirm link


@dataclass
class QAConfig:
    """Quality assurance configuration."""
    batch_size: int = 5               # QA_BATCH: Review every N proposed links
    enabled: bool = True              # Enable QA task generation


@dataclass
class FalkorDBConfig:
    """FalkorDB connection configuration."""
    host: str = "localhost"
    port: int = 6379
    graph_name: str = "consciousness-infrastructure_mind-protocol"  # Target graph for ingestion

    @property
    def connection_string(self) -> str:
        """Get Redis connection string."""
        return f"redis://{self.host}:{self.port}"


@dataclass
class ProcessingConfig:
    """Document processing configuration."""
    manifest_path: str = ""           # Path to manifest.json (required at runtime)
    state_db_path: str = ".doc_ingestion_state.db"  # SQLite state file
    checkpoint_interval: int = 10     # Checkpoint every N documents
    qa_check_interval: int = 3        # Run QA quality check every N documents
    enable_resume: bool = True        # Enable checkpoint/resume


@dataclass
class LintConfig:
    """Graph linting configuration."""
    enable_c1_check: bool = True      # C1: Valid node/link types
    enable_c2_check: bool = True      # C2: Required metadata present
    enable_c3_check: bool = True      # C3: Confidence in valid range
    enable_c4_check: bool = True      # C4: No orphan nodes
    enable_c5_check: bool = True      # C5: No duplicate edges
    enable_c6_check: bool = True      # C6: No self-loops (except allowed types)
    enable_c7_check: bool = True      # C7: Bidirectional edge consistency
    fail_on_error: bool = False       # Fail processing on lint errors (vs warn)


@dataclass
class LoggingConfig:
    """Logging and telemetry configuration."""
    jsonl_output: bool = True         # Emit JSONL logs (@@-prefixed)
    log_level: str = "INFO"           # Log level: DEBUG, INFO, WARNING, ERROR
    log_to_file: bool = False         # Also log to file
    log_file_path: str = "doc_ingestion.log"


@dataclass
class DocIngestionConfig:
    """
    Master configuration for documentation ingestion pipeline.

    All configuration sections consolidated here. Supports:
    - Environment variable overrides (DOC_INGEST_*)
    - Runtime overrides via set_override()
    - Pretty-print for status reporting
    """

    chunk: ChunkConfig = field(default_factory=ChunkConfig)
    confidence: ConfidenceThresholds = field(default_factory=ConfidenceThresholds)
    qa: QAConfig = field(default_factory=QAConfig)
    falkordb: FalkorDBConfig = field(default_factory=FalkorDBConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    lint: LintConfig = field(default_factory=LintConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    # Runtime overrides (from CLI flags)
    _overrides: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_env(cls) -> 'DocIngestionConfig':
        """
        Load configuration with environment variable overrides.

        Environment variables:
        - DOC_INGEST_CHUNK_TARGET_TOKENS
        - DOC_INGEST_CHUNK_MAX_TOKENS
        - DOC_INGEST_CONF_CREATE_TASK
        - DOC_INGEST_CONF_PROPOSE_LINK
        - DOC_INGEST_CONF_AUTOCONFIRM
        - DOC_INGEST_QA_BATCH
        - DOC_INGEST_QA_ENABLED
        - DOC_INGEST_FALKORDB_HOST
        - DOC_INGEST_FALKORDB_PORT
        - DOC_INGEST_FALKORDB_GRAPH
        - DOC_INGEST_MANIFEST_PATH
        - DOC_INGEST_STATE_DB_PATH
        - DOC_INGEST_LOG_LEVEL

        Returns:
            DocIngestionConfig with env var overrides applied
        """
        config = cls()

        # Chunk config
        if val := os.getenv('DOC_INGEST_CHUNK_TARGET_TOKENS'):
            config.chunk.target_tokens = int(val)
        if val := os.getenv('DOC_INGEST_CHUNK_MAX_TOKENS'):
            config.chunk.max_tokens = int(val)

        # Confidence thresholds
        if val := os.getenv('DOC_INGEST_CONF_CREATE_TASK'):
            config.confidence.create_task = float(val)
        if val := os.getenv('DOC_INGEST_CONF_PROPOSE_LINK'):
            config.confidence.propose_link = float(val)
        if val := os.getenv('DOC_INGEST_CONF_AUTOCONFIRM'):
            config.confidence.autoconfirm = float(val)

        # QA config
        if val := os.getenv('DOC_INGEST_QA_BATCH'):
            config.qa.batch_size = int(val)
        if val := os.getenv('DOC_INGEST_QA_ENABLED'):
            config.qa.enabled = val.lower() in ('true', '1', 'yes')

        # FalkorDB config
        if val := os.getenv('DOC_INGEST_FALKORDB_HOST'):
            config.falkordb.host = val
        if val := os.getenv('DOC_INGEST_FALKORDB_PORT'):
            config.falkordb.port = int(val)
        if val := os.getenv('DOC_INGEST_FALKORDB_GRAPH'):
            config.falkordb.graph_name = val

        # Processing config
        if val := os.getenv('DOC_INGEST_MANIFEST_PATH'):
            config.processing.manifest_path = val
        if val := os.getenv('DOC_INGEST_STATE_DB_PATH'):
            config.processing.state_db_path = val

        # Logging config
        if val := os.getenv('DOC_INGEST_LOG_LEVEL'):
            config.logging.log_level = val.upper()

        return config

    def set_override(self, key: str, value: Any) -> None:
        """
        Set runtime override (from CLI flags).

        Args:
            key: Dotted path (e.g., 'chunk.target_tokens', 'confidence.autoconfirm')
            value: Override value

        Example:
            config.set_override('chunk.target_tokens', 300)
            config.set_override('qa.enabled', False)
        """
        self._overrides[key] = value

        # Apply override to actual config
        parts = key.split('.')
        if len(parts) != 2:
            raise ValueError(f"Invalid override key: {key}. Expected format: 'section.field'")

        section, field = parts
        section_obj = getattr(self, section, None)
        if section_obj is None:
            raise ValueError(f"Unknown config section: {section}")

        if not hasattr(section_obj, field):
            raise ValueError(f"Unknown field '{field}' in section '{section}'")

        setattr(section_obj, field, value)

    def get_overrides(self) -> Dict[str, Any]:
        """Get all runtime overrides."""
        return self._overrides.copy()

    def validate(self) -> list[str]:
        """
        Validate configuration.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Chunk validation
        if self.chunk.target_tokens <= 0:
            errors.append(f"chunk.target_tokens must be > 0, got {self.chunk.target_tokens}")
        if self.chunk.max_tokens <= self.chunk.target_tokens:
            errors.append(f"chunk.max_tokens ({self.chunk.max_tokens}) must be > target_tokens ({self.chunk.target_tokens})")

        # Confidence validation
        for field_name in ['create_task', 'propose_link', 'autoconfirm']:
            val = getattr(self.confidence, field_name)
            if not (0.0 <= val <= 1.0):
                errors.append(f"confidence.{field_name} must be in [0, 1], got {val}")

        if self.confidence.create_task >= self.confidence.propose_link:
            errors.append(f"confidence.create_task ({self.confidence.create_task}) must be < propose_link ({self.confidence.propose_link})")
        if self.confidence.propose_link >= self.confidence.autoconfirm:
            errors.append(f"confidence.propose_link ({self.confidence.propose_link}) must be < autoconfirm ({self.confidence.autoconfirm})")

        # QA validation
        if self.qa.batch_size <= 0:
            errors.append(f"qa.batch_size must be > 0, got {self.qa.batch_size}")

        # FalkorDB validation
        if not self.falkordb.host:
            errors.append("falkordb.host is required")
        if self.falkordb.port <= 0 or self.falkordb.port > 65535:
            errors.append(f"falkordb.port must be in [1, 65535], got {self.falkordb.port}")
        if not self.falkordb.graph_name:
            errors.append("falkordb.graph_name is required")

        # Processing validation
        if not self.processing.manifest_path:
            errors.append("processing.manifest_path is required")

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary (for JSON serialization)."""
        return {
            'chunk': asdict(self.chunk),
            'confidence': asdict(self.confidence),
            'qa': asdict(self.qa),
            'falkordb': asdict(self.falkordb),
            'processing': asdict(self.processing),
            'lint': asdict(self.lint),
            'logging': asdict(self.logging),
            'overrides': self._overrides
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert config to pretty JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def pretty_print(self) -> str:
        """
        Generate human-readable configuration summary.

        Used by `mp.sh status` to display current configuration.

        Returns:
            Multi-line string with formatted config
        """
        lines = ["=== Doc Ingestion Configuration ===", ""]

        lines.append("[Chunking]")
        lines.append(f"  Target tokens:       {self.chunk.target_tokens}")
        lines.append(f"  Max tokens:          {self.chunk.max_tokens}")
        lines.append(f"  Preserve code fence: {self.chunk.preserve_code_fences}")
        lines.append("")

        lines.append("[Confidence Thresholds]")
        lines.append(f"  Create task:    < {self.confidence.create_task:.2f}")
        lines.append(f"  Propose link:   ≥ {self.confidence.propose_link:.2f}")
        lines.append(f"  Auto-confirm:   ≥ {self.confidence.autoconfirm:.2f}")
        lines.append("")

        lines.append("[QA]")
        lines.append(f"  Batch size:     {self.qa.batch_size}")
        lines.append(f"  Enabled:        {self.qa.enabled}")
        lines.append("")

        lines.append("[FalkorDB]")
        lines.append(f"  Host:           {self.falkordb.host}")
        lines.append(f"  Port:           {self.falkordb.port}")
        lines.append(f"  Graph:          {self.falkordb.graph_name}")
        lines.append(f"  Connection:     {self.falkordb.connection_string}")
        lines.append("")

        lines.append("[Processing]")
        lines.append(f"  Manifest:       {self.processing.manifest_path or '(not set)'}")
        lines.append(f"  State DB:       {self.processing.state_db_path}")
        lines.append(f"  Checkpoint:     every {self.processing.checkpoint_interval} docs")
        lines.append(f"  Resume enabled: {self.processing.enable_resume}")
        lines.append("")

        lines.append("[Linting]")
        enabled_checks = [f"C{i+1}" for i in range(7) if getattr(self.lint, f"enable_c{i+1}_check")]
        lines.append(f"  Enabled checks: {', '.join(enabled_checks) if enabled_checks else 'none'}")
        lines.append(f"  Fail on error:  {self.lint.fail_on_error}")
        lines.append("")

        lines.append("[Logging]")
        lines.append(f"  JSONL output:   {self.logging.jsonl_output}")
        lines.append(f"  Level:          {self.logging.log_level}")
        lines.append(f"  Log to file:    {self.logging.log_to_file}")
        if self.logging.log_to_file:
            lines.append(f"  File path:      {self.logging.log_file_path}")
        lines.append("")

        if self._overrides:
            lines.append("[Runtime Overrides]")
            for key, value in self._overrides.items():
                lines.append(f"  {key} = {value}")
            lines.append("")

        return "\n".join(lines)


# Singleton instance for global access
_global_config: Optional[DocIngestionConfig] = None


def get_config() -> DocIngestionConfig:
    """
    Get global configuration instance.

    Loads from environment on first call, then returns cached instance.

    Returns:
        DocIngestionConfig singleton
    """
    global _global_config
    if _global_config is None:
        _global_config = DocIngestionConfig.from_env()
    return _global_config


def reload_config() -> DocIngestionConfig:
    """
    Force reload configuration from environment.

    Useful for testing or when environment changes.

    Returns:
        Fresh DocIngestionConfig instance
    """
    global _global_config
    _global_config = DocIngestionConfig.from_env()
    return _global_config


if __name__ == "__main__":
    # Quick test: Load config and print
    config = get_config()

    # Test validation
    errors = config.validate()
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Configuration valid!")

    print()
    print(config.pretty_print())

    # Test override
    print("\n=== Testing Runtime Override ===")
    config.set_override('chunk.target_tokens', 300)
    config.set_override('qa.enabled', False)
    print(config.pretty_print())

    # Test JSON export
    print("\n=== JSON Export ===")
    print(config.to_json())
