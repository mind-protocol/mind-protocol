#!/bin/bash
#
# mp.sh - Mind Protocol Documentation Ingestion CLI
#
# CLI entrypoint for documentation ingestion pipeline.
# Provides commands for processing corpus, viewing status, and linting graph.
#
# Usage:
#   mp.sh process <manifest.json> [options]
#   mp.sh status [options]
#   mp.sh lint [options]
#   mp.sh config
#
# Author: Atlas (Infrastructure Engineer)
# Date: 2025-10-29
# Spec: docs/SPEC DOC INPUT.md

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Python command
PYTHON="${PYTHON:-python3}"

# Functions
print_usage() {
    cat << EOF
mp.sh - Mind Protocol Documentation Ingestion CLI

Usage:
  mp.sh process <manifest.json> [options]    Process documentation corpus
  mp.sh status [options]                     View processing status
  mp.sh lint [options]                       Run graph structure linter
  mp.sh config                               Display current configuration

Commands:
  process       Process documents from manifest
  status        Show processing progress and statistics
  lint          Validate graph structure (C1-C7 checks)
  config        Display configuration settings

Process Options:
  --max-files N         Process at most N files
  --no-resume           Start fresh (ignore checkpoint)
  --dry-run             Validate manifest without processing
  --lint                Run linter after processing

Status Options:
  --db PATH             Path to state database (default: .doc_ingestion_state.db)
  --json                Output as JSON

Lint Options:
  --json                Output as JSON
  --fail-on-error       Exit 1 if errors found

Environment Variables:
  DOC_INGEST_MANIFEST_PATH      Default manifest path
  DOC_INGEST_CHUNK_TARGET_TOKENS   Chunk target size (default: 250)
  DOC_INGEST_CHUNK_MAX_TOKENS      Chunk max size (default: 480)
  DOC_INGEST_CONF_CREATE_TASK      Confidence threshold for task creation
  DOC_INGEST_CONF_PROPOSE_LINK     Confidence threshold for link proposal
  DOC_INGEST_CONF_AUTOCONFIRM      Confidence threshold for auto-confirm
  (See config.py for full list)

Examples:
  # Process all documents from manifest
  mp.sh process docs/manifest.json

  # Process first 10 documents
  mp.sh process docs/manifest.json --max-files 10

  # View processing status
  mp.sh status

  # Lint graph structure
  mp.sh lint

  # Display configuration
  mp.sh config

EOF
}

print_error() {
    echo -e "${RED}ERROR:${NC} $1" >&2
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

validate_manifest() {
    local manifest="$1"

    if [ ! -f "$manifest" ]; then
        print_error "Manifest not found: $manifest"
        return 1
    fi

    # Validate JSON structure
    if ! $PYTHON -c "import json; json.load(open('$manifest'))" 2>/dev/null; then
        print_error "Invalid JSON in manifest: $manifest"
        return 1
    fi

    # Check for 'files' key
    if ! $PYTHON -c "import json; data = json.load(open('$manifest')); assert 'files' in data" 2>/dev/null; then
        print_error "Manifest missing 'files' key: $manifest"
        return 1
    fi

    print_success "Manifest validated: $manifest"
    return 0
}

cmd_process() {
    local manifest=""
    local max_files=""
    local no_resume=""
    local dry_run=""
    local run_lint=""

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --max-files)
                max_files="$2"
                shift 2
                ;;
            --no-resume)
                no_resume="--no-resume"
                shift
                ;;
            --dry-run)
                dry_run="true"
                shift
                ;;
            --lint)
                run_lint="--lint"
                shift
                ;;
            *)
                if [ -z "$manifest" ]; then
                    manifest="$1"
                else
                    print_error "Unknown argument: $1"
                    return 1
                fi
                shift
                ;;
        esac
    done

    # Check manifest provided
    if [ -z "$manifest" ]; then
        print_error "Manifest path required"
        echo "Usage: mp.sh process <manifest.json> [options]"
        return 1
    fi

    # Validate manifest
    validate_manifest "$manifest" || return 1

    # Dry run: just validate
    if [ -n "$dry_run" ]; then
        print_info "Dry run: Manifest valid, no processing performed"
        return 0
    fi

    # Build command
    local cmd="$PYTHON $TOOLS_DIR/process_corpus.py $manifest"

    if [ -n "$max_files" ]; then
        cmd="$cmd --max-files $max_files"
    fi

    if [ -n "$no_resume" ]; then
        cmd="$cmd $no_resume"
    fi

    if [ -n "$run_lint" ]; then
        cmd="$cmd $run_lint"
    fi

    # Run processor
    print_info "Starting corpus processing..."
    if $cmd; then
        print_success "Processing complete"
        return 0
    else
        print_error "Processing failed"
        return 1
    fi
}

cmd_status() {
    local db_path=".doc_ingestion_state.db"
    local json_output=""

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --db)
                db_path="$2"
                shift 2
                ;;
            --json)
                json_output="--json"
                shift
                ;;
            *)
                print_error "Unknown argument: $1"
                return 1
                ;;
        esac
    done

    # Run status reporter
    $PYTHON "$TOOLS_DIR/status.py" --db "$db_path" $json_output
}

cmd_lint() {
    local json_output=""
    local fail_on_error=""

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --json)
                json_output="--json"
                shift
                ;;
            --fail-on-error)
                fail_on_error="--fail-on-error"
                shift
                ;;
            *)
                print_error "Unknown argument: $1"
                return 1
                ;;
        esac
    done

    # Run linter
    print_info "Running graph structure checks..."

    # Call lint_graph.py directly
    if $PYTHON "$TOOLS_DIR/lint_graph.py" $json_output $fail_on_error; then
        print_success "All checks passed"
        return 0
    else
        print_error "Lint checks failed"
        return 1
    fi
}

cmd_config() {
    # Display configuration
    print_info "Current configuration:"
    echo ""

    # Run config.py to print configuration
    $PYTHON -c "
import sys
sys.path.insert(0, '$TOOLS_DIR')
from config import get_config
config = get_config()
print(config.pretty_print())
"
}

# Main dispatch
main() {
    if [ $# -eq 0 ]; then
        print_usage
        exit 0
    fi

    local command="$1"
    shift

    case "$command" in
        process)
            cmd_process "$@"
            ;;
        status)
            cmd_status "$@"
            ;;
        lint)
            cmd_lint "$@"
            ;;
        config)
            cmd_config "$@"
            ;;
        help|--help|-h)
            print_usage
            exit 0
            ;;
        *)
            print_error "Unknown command: $command"
            echo ""
            print_usage
            exit 1
            ;;
    esac
}

main "$@"
