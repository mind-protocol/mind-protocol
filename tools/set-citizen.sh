#!/bin/bash
# Set active citizen identity for git commits
# Usage: source tools/set-citizen.sh <citizen-name>
#
# Examples:
#   source tools/set-citizen.sh victor
#   source tools/set-citizen.sh ada

CITIZEN="${1:-victor}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Read citizen data from YAML (simple parsing)
CITIZEN_DATA=$(grep -A 5 "^  ${CITIZEN}:" "$REPO_ROOT/.git-citizens.yaml")

if [ -z "$CITIZEN_DATA" ]; then
    echo "❌ Unknown citizen: $CITIZEN"
    echo "Available: victor, ada, felix, atlas, iris, luca"
    return 1
fi

# Extract fields
NAME=$(echo "$CITIZEN_DATA" | grep "name:" | cut -d'"' -f2)
EMAIL=$(echo "$CITIZEN_DATA" | grep "email:" | cut -d'"' -f2)
EMOJI=$(echo "$CITIZEN_DATA" | grep "emoji:" | cut -d'"' -f2)
TITLE=$(echo "$CITIZEN_DATA" | grep "title:" | cut -d'"' -f2)

# Set git config
cd "$REPO_ROOT"
git config --local user.name "$NAME"
git config --local user.email "$EMAIL"

# Export for environment
export CITIZEN_NAME="$NAME"
export CITIZEN_EMAIL="$EMAIL"
export CITIZEN_EMOJI="$EMOJI"
export CITIZEN_TITLE="$TITLE"
export ACTIVE_CITIZEN="$CITIZEN"

echo "✅ Active citizen: $EMOJI $NAME <$EMAIL>"
echo "   Title: $TITLE"
echo ""
echo "💡 Commits will now be signed as $NAME"
