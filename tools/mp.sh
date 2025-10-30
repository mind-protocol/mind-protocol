#!/usr/bin/env bash
#
# mp.sh - Mind Protocol CLI
#
# Usage:
#   mp.sh ask "<question>"
#
# Question Format (context + intent + problem + ask):
#   "I'm implementing <context>.
#    I need to <intent>.
#    Current approach <problem>.
#    What <specific ask>?"
#
# Example:
#   mp.sh ask "I'm implementing entity persistence for the consciousness substrate.
#              I need to ensure subentities reload correctly after restart.
#              Current approach uses FalkorDB MERGE but shows empty entity counts.
#              What are the proven patterns for reliable graph persistence?"
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Subcommand dispatch
case "${1:-}" in
    ask)
        shift
        if [ $# -eq 0 ]; then
            echo "Usage: mp.sh ask \"<question>\"" >&2
            exit 1
        fi
        python3 "$SCRIPT_DIR/doc_ingestion/ask.py" "$@"
        ;;

    *)
        echo "Mind Protocol CLI" >&2
        echo "" >&2
        echo "Usage:" >&2
        echo "  mp.sh ask \"<question>\"    - Semantic graph traversal query" >&2
        echo "" >&2
        echo "Question Format (context + intent + problem + ask):" >&2
        echo "  I'm implementing <context>." >&2
        echo "  I need to <intent>." >&2
        echo "  Current approach <problem>." >&2
        echo "  What <specific ask>?" >&2
        echo "" >&2
        echo "Example:" >&2
        echo "  mp.sh ask \"I'm implementing entity persistence. I need subentities" >&2
        echo "            to reload after restart. Current MERGE shows empty counts." >&2
        echo "            What are proven patterns for graph persistence?\"" >&2
        echo "" >&2
        exit 1
        ;;
esac
