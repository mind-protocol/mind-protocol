#!/usr/bin/env bash

# migrate_citizen_keys_to_render_volume.sh
#
# Migrates citizen X25519 key pairs from a git repo directory to the Render
# persistent volume. Keys must NEVER live in git repos — repos are public.
#
# Usage:
#   ./scripts/migrate_citizen_keys_to_render_volume.sh \
#       --source /home/mind-protocol/cities-of-light/citizens \
#       --target /var/data/citizens
#
# What this script does:
#   1. Scans source dir for citizens with .keys/ directories
#   2. Copies each .keys/ to the target dir (preserving permissions)
#   3. Verifies the copy (byte-for-byte comparison)
#   4. Prints instructions for git cleanup (human must execute manually)
#
# What this script does NOT do:
#   - Delete anything from the source directory
#   - Modify git history
#   - Push changes to any remote
#
# IMPORTANT: After running this script, the human must:
#   1. Verify keys work from the new location
#   2. Fix .gitignore in cities-of-light (change **/.keys/private_key.b64 to **/.keys/)
#   3. Delete .keys/ directories from the git repo working tree
#   4. Clean git history if keys were ever committed (see instructions at end)
#
# Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>

set -euo pipefail

# ---------------------------------------------------------------------------
# Colors for output
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ---------------------------------------------------------------------------
# CLI argument parsing
# ---------------------------------------------------------------------------
SOURCE_DIR=""
TARGET_DIR=""
DRY_RUN=false

usage() {
    echo ""
    echo "Usage: $0 --source <git-repo-citizens-dir> --target <render-volume-citizens-dir> [--dry-run]"
    echo ""
    echo "Options:"
    echo "  --source    Path to citizens/ directory inside the git repo"
    echo "              (e.g., /home/mind-protocol/cities-of-light/citizens)"
    echo "  --target    Path to citizens/ directory on Render persistent volume"
    echo "              (e.g., /var/data/citizens)"
    echo "  --dry-run   Show what would be done without copying anything"
    echo "  --help      Show this message"
    echo ""
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --source)
            SOURCE_DIR="$2"
            shift 2
            ;;
        --target)
            TARGET_DIR="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

if [[ -z "$SOURCE_DIR" || -z "$TARGET_DIR" ]]; then
    echo -e "${RED}Error: --source and --target are required.${NC}"
    usage
    exit 1
fi

# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

if [[ ! -d "$SOURCE_DIR" ]]; then
    echo -e "${RED}Error: Source directory does not exist: $SOURCE_DIR${NC}"
    exit 1
fi

echo ""
echo -e "${CYAN}=== Citizen Key Migration ===${NC}"
echo ""
echo "Source (git repo):     $SOURCE_DIR"
echo "Target (Render vol):   $TARGET_DIR"
echo "Dry run:               $DRY_RUN"
echo ""

# ---------------------------------------------------------------------------
# Discover citizens with .keys/
# ---------------------------------------------------------------------------

CITIZENS_WITH_KEYS=()

for citizen_dir in "$SOURCE_DIR"/*/; do
    citizen_name=$(basename "$citizen_dir")

    # Skip non-directories, hidden dirs, and common junk
    [[ "$citizen_name" == "." || "$citizen_name" == ".." ]] && continue
    [[ "$citizen_name" == "node_modules" ]] && continue
    [[ "$citizen_name" == .* ]] && continue

    keys_dir="$citizen_dir.keys"
    if [[ -d "$keys_dir" ]]; then
        CITIZENS_WITH_KEYS+=("$citizen_name")
    fi
done

if [[ ${#CITIZENS_WITH_KEYS[@]} -eq 0 ]]; then
    echo -e "${YELLOW}No citizens with .keys/ directories found in $SOURCE_DIR${NC}"
    echo "Nothing to migrate."
    exit 0
fi

echo -e "Found ${GREEN}${#CITIZENS_WITH_KEYS[@]}${NC} citizen(s) with .keys/:"
for name in "${CITIZENS_WITH_KEYS[@]}"; do
    echo "  - $name"
done
echo ""

# ---------------------------------------------------------------------------
# Check if keys were ever committed to git
# ---------------------------------------------------------------------------

# Try to detect if we're in a git repo
SOURCE_REPO_ROOT=""
if git -C "$SOURCE_DIR" rev-parse --show-toplevel &>/dev/null; then
    SOURCE_REPO_ROOT=$(git -C "$SOURCE_DIR" rev-parse --show-toplevel)
    echo -e "${CYAN}Git repo detected:${NC} $SOURCE_REPO_ROOT"

    # Check if any .keys/ files are tracked
    TRACKED_KEYS=$(git -C "$SOURCE_REPO_ROOT" ls-files -- '*/.keys/*' '**/.keys/*' 2>/dev/null || true)
    if [[ -n "$TRACKED_KEYS" ]]; then
        echo -e "${RED}WARNING: The following key files are TRACKED by git:${NC}"
        echo "$TRACKED_KEYS" | while read -r f; do echo "  $f"; done
        echo ""
        echo -e "${RED}These files are in git history. After migration, you MUST clean git history.${NC}"
        echo -e "${RED}See instructions at the end of this script's output.${NC}"
        echo ""
        KEYS_IN_GIT=true
    else
        echo -e "${GREEN}Good: No .keys/ files are tracked by git.${NC}"
        KEYS_IN_GIT=false
    fi

    # Check git history for any past commits with key files
    HISTORY_KEYS=$(git -C "$SOURCE_REPO_ROOT" log --all --diff-filter=A --name-only --pretty=format:"" -- '*/.keys/*' '**/.keys/*' 2>/dev/null | grep -v '^$' || true)
    if [[ -n "$HISTORY_KEYS" ]]; then
        echo -e "${RED}WARNING: Key files were found in git history (past commits):${NC}"
        echo "$HISTORY_KEYS" | while read -r f; do echo "  $f"; done
        echo ""
        KEYS_IN_HISTORY=true
    else
        echo -e "${GREEN}Good: No .keys/ files found in git history.${NC}"
        KEYS_IN_HISTORY=false
    fi

    # Check .gitignore coverage
    echo ""
    echo -e "${CYAN}Checking .gitignore coverage:${NC}"
    GITIGNORE_FILE="$SOURCE_REPO_ROOT/.gitignore"
    if [[ -f "$GITIGNORE_FILE" ]]; then
        if grep -q '^\*\*/\.keys/$' "$GITIGNORE_FILE" 2>/dev/null; then
            echo -e "  ${GREEN}.gitignore has **/.keys/ (full directory exclusion) -- correct${NC}"
        elif grep -q '\.keys' "$GITIGNORE_FILE" 2>/dev/null; then
            echo -e "  ${YELLOW}.gitignore mentions .keys but may not exclude the full directory:${NC}"
            grep '\.keys' "$GITIGNORE_FILE" | while read -r line; do echo "    $line"; done
            echo -e "  ${YELLOW}RECOMMENDED: Change to **/.keys/ to exclude ALL key files${NC}"
        else
            echo -e "  ${RED}.gitignore does NOT mention .keys at all -- DANGEROUS${NC}"
        fi
    else
        echo -e "  ${RED}No .gitignore found -- DANGEROUS${NC}"
    fi
    echo ""
else
    echo "Source directory is not inside a git repo (or git is not available)."
    echo ""
fi

# ---------------------------------------------------------------------------
# Create target directory structure
# ---------------------------------------------------------------------------

if [[ "$DRY_RUN" == true ]]; then
    echo -e "${YELLOW}[DRY RUN] Would create target directory: $TARGET_DIR${NC}"
else
    if [[ ! -d "$TARGET_DIR" ]]; then
        echo "Creating target directory: $TARGET_DIR"
        mkdir -p "$TARGET_DIR"
    fi
fi

# ---------------------------------------------------------------------------
# Copy keys for each citizen
# ---------------------------------------------------------------------------

COPIED=0
FAILED=0
VERIFIED=0

for citizen_name in "${CITIZENS_WITH_KEYS[@]}"; do
    src_keys="$SOURCE_DIR/$citizen_name/.keys"
    dst_citizen="$TARGET_DIR/$citizen_name"
    dst_keys="$dst_citizen/.keys"

    echo -e "${CYAN}--- $citizen_name ---${NC}"

    # List source key files
    echo "  Source files:"
    for f in "$src_keys"/*; do
        if [[ -f "$f" ]]; then
            echo "    $(basename "$f")  ($(wc -c < "$f") bytes)"
        fi
    done

    if [[ "$DRY_RUN" == true ]]; then
        echo -e "  ${YELLOW}[DRY RUN] Would copy $src_keys -> $dst_keys${NC}"
        continue
    fi

    # Create target citizen directory if needed
    if [[ ! -d "$dst_citizen" ]]; then
        mkdir -p "$dst_citizen"
    fi

    # Copy .keys/ directory, preserving permissions
    if cp -rp "$src_keys" "$dst_citizen/"; then
        echo -e "  ${GREEN}Copied to $dst_keys${NC}"
        COPIED=$((COPIED + 1))

        # Verify the copy
        VERIFY_OK=true
        for src_file in "$src_keys"/*; do
            if [[ ! -f "$src_file" ]]; then continue; fi
            fname=$(basename "$src_file")
            dst_file="$dst_keys/$fname"

            if [[ ! -f "$dst_file" ]]; then
                echo -e "  ${RED}VERIFY FAILED: $dst_file does not exist${NC}"
                VERIFY_OK=false
                continue
            fi

            src_hash=$(sha256sum "$src_file" | cut -d' ' -f1)
            dst_hash=$(sha256sum "$dst_file" | cut -d' ' -f1)

            if [[ "$src_hash" == "$dst_hash" ]]; then
                echo -e "  ${GREEN}Verified: $fname (SHA-256 match)${NC}"
            else
                echo -e "  ${RED}VERIFY FAILED: $fname hash mismatch!${NC}"
                echo "    Source: $src_hash"
                echo "    Target: $dst_hash"
                VERIFY_OK=false
            fi
        done

        if [[ "$VERIFY_OK" == true ]]; then
            VERIFIED=$((VERIFIED + 1))
        else
            FAILED=$((FAILED + 1))
        fi
    else
        echo -e "  ${RED}COPY FAILED for $citizen_name${NC}"
        FAILED=$((FAILED + 1))
    fi

    echo ""
done

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

echo -e "${CYAN}=== Summary ===${NC}"
echo ""
if [[ "$DRY_RUN" == true ]]; then
    echo -e "${YELLOW}DRY RUN — no files were copied.${NC}"
    echo "Would have migrated ${#CITIZENS_WITH_KEYS[@]} citizen(s)."
else
    echo "Citizens processed: ${#CITIZENS_WITH_KEYS[@]}"
    echo -e "Copied:             ${GREEN}$COPIED${NC}"
    echo -e "Verified:           ${GREEN}$VERIFIED${NC}"
    if [[ $FAILED -gt 0 ]]; then
        echo -e "Failed:             ${RED}$FAILED${NC}"
    fi
fi
echo ""

# ---------------------------------------------------------------------------
# Post-migration instructions
# ---------------------------------------------------------------------------

echo -e "${CYAN}=== POST-MIGRATION STEPS (manual) ===${NC}"
echo ""
echo "After verifying keys work from the new location ($TARGET_DIR):"
echo ""
echo -e "${YELLOW}1. Fix .gitignore in cities-of-light:${NC}"
echo ""
echo "   Change this line:"
echo "     **/.keys/private_key.b64"
echo "   To this:"
echo "     **/.keys/"
echo ""
echo "   This excludes the ENTIRE .keys/ directory (public AND private keys)."
echo ""
echo -e "${YELLOW}2. Delete .keys/ directories from the git repo working tree:${NC}"
echo ""
for citizen_name in "${CITIZENS_WITH_KEYS[@]}"; do
    echo "   rm -rf $SOURCE_DIR/$citizen_name/.keys/"
done
echo ""
echo -e "${YELLOW}3. Update any code that reads keys from the git repo path:${NC}"
echo ""
echo "   Change paths like:"
echo "     cities-of-light/citizens/{name}/.keys/"
echo "   To the Render volume path:"
echo "     $TARGET_DIR/{name}/.keys/"
echo ""
echo "   Check these files:"
echo "     - mind-mcp/mcp/tools/place_handler.py"
echo "     - Any service that loads citizen private keys"
echo ""
echo -e "${YELLOW}4. If keys were EVER committed to git history:${NC}"
echo ""
echo "   Use BFG Repo-Cleaner (recommended) or git filter-repo to purge:"
echo ""
echo "   Option A — BFG Repo-Cleaner (fast, simple):"
echo "     cd $SOURCE_REPO_ROOT"
echo "     # First, ensure .keys/ dirs are deleted from working tree (step 2 above)"
echo "     git add -A && git commit -m 'chore: remove citizen keys from repo'"
echo "     # Then run BFG to purge from history:"
echo "     bfg --delete-folders .keys"
echo "     git reflog expire --expire=now --all"
echo "     git gc --prune=now --aggressive"
echo "     git push --force"
echo ""
echo "   Option B — git filter-repo (built-in, slower):"
echo "     cd $SOURCE_REPO_ROOT"
echo "     git filter-repo --path-glob '*/.keys/*' --invert-paths"
echo "     git push --force"
echo ""
echo -e "${RED}   WARNING: Force-pushing rewrites history for all collaborators.${NC}"
echo -e "${RED}   All clones must be re-cloned after history cleanup.${NC}"
echo ""
echo -e "${YELLOW}5. Verify the Render volume path is NOT inside any git repo.${NC}"
echo ""
echo -e "${YELLOW}6. Duplicate public keys in each citizen's L1 graph (encrypted brain):${NC}"
echo ""
echo "   node scripts/generate_all_citizen_keys.js \\"
echo "     --citizens-dir $TARGET_DIR \\"
echo "     --graph venezia"
echo ""
echo "   (This registers public keys on Actor nodes in FalkorDB — keys already exist,"
echo "   so it will skip generation and only register in the graph.)"
echo ""
echo -e "${GREEN}Done. Keys are safe when they exist ONLY on:${NC}"
echo "  1. Render persistent volume ($TARGET_DIR/{name}/.keys/)"
echo "  2. Citizen's L1 graph (public_key on Actor node)"
echo ""
