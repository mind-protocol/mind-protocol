#!/bin/bash
# Terminology Normalization Script
# Purpose: Standardize "sub-entity" → "subentity" and "Sub-Entity" → "SubEntity" across repo
# Per TAXONOMY_RECONCILIATION.md §3

set -e

REPO_ROOT="/home/mind-protocol/mindprotocol"
cd "$REPO_ROOT"

echo "🔧 Mind Protocol Terminology Normalization"
echo "=========================================="
echo ""

# Backup marker
BACKUP_TAG=$(date +%Y%m%d_%H%M%S)
echo "📸 Creating backup tag: terminology_backup_$BACKUP_TAG"
git tag "terminology_backup_$BACKUP_TAG" 2>/dev/null || echo "  (git tag failed, continuing anyway)"

echo ""
echo "📊 Analyzing scope..."

# Count occurrences
SUB_ENTITY_COUNT=$(grep -r "sub-entit" --include="*.md" --include="*.py" --include="*.ts" --include="*.tsx" --include="*.json" \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=__pycache__ --exclude-dir=.next . | wc -l)

echo "  Found ~$SUB_ENTITY_COUNT occurrences of 'sub-entity' pattern"
echo ""

# Confirmation
read -p "⚠️  Proceed with replacement? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "❌ Aborted"
    exit 1
fi

echo ""
echo "🔄 Applying replacements..."

# Find all relevant files
FILES=$(find . -type f \( \
    -name "*.md" -o \
    -name "*.py" -o \
    -name "*.ts" -o \
    -name "*.tsx" -o \
    -name "*.json" \
\) \
    -not -path "*/node_modules/*" \
    -not -path "*/.git/*" \
    -not -path "*/__pycache__/*" \
    -not -path "*/.next/*" \
)

# Counter
COUNT=0

for file in $FILES; do
    # Check if file contains the pattern
    if grep -q "sub-entit" "$file" 2>/dev/null; then
        # Apply replacements (case-preserving)
        sed -i 's/sub-entity/subentity/g' "$file"
        sed -i 's/Sub-Entity/SubEntity/g' "$file"
        sed -i 's/sub-entities/subentities/g' "$file"
        sed -i 's/Sub-Entities/SubEntities/g' "$file"
        sed -i 's/SUB-ENTITY/SUBENTITY/g' "$file"
        sed -i 's/SUB-ENTITIES/SUBENTITIES/g' "$file"

        COUNT=$((COUNT + 1))

        # Progress indicator
        if [ $((COUNT % 50)) -eq 0 ]; then
            echo "  Processed $COUNT files..."
        fi
    fi
done

echo "  ✅ Processed $COUNT files"
echo ""

# Verify changes
AFTER_COUNT=$(grep -r "sub-entit" --include="*.md" --include="*.py" --include="*.ts" --include="*.tsx" --include="*.json" \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=__pycache__ --exclude-dir=.next . | wc -l || echo "0")

echo "📈 Results:"
echo "  Before: ~$SUB_ENTITY_COUNT occurrences"
echo "  After:  $AFTER_COUNT occurrences"
echo "  Changed: $((SUB_ENTITY_COUNT - AFTER_COUNT)) occurrences"
echo ""

if [ "$AFTER_COUNT" -gt 0 ]; then
    echo "⚠️  Warning: $AFTER_COUNT occurrences still remain (may be in filenames or special contexts)"
    echo "  Run 'grep -r \"sub-entit\" --include=\"*.md\" --include=\"*.py\" .' to inspect"
fi

echo ""
echo "✅ Terminology normalization complete!"
echo "  Backup tag: terminology_backup_$BACKUP_TAG"
echo "  Run 'git diff --stat' to see changes"
echo "  Run 'git checkout terminology_backup_$BACKUP_TAG' to revert if needed"
