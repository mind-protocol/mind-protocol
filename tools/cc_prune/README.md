# cc_prune - Code Cleanup & Asset Pruning Tool

## ⚠️ **CRITICAL SAFETY WARNING** ⚠️

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║  🚨 DO NOT USE THIS TOOL IN PRODUCTION ENVIRONMENTS 🚨      ║
║                                                              ║
║  This tool performs IRREVERSIBLE FILE DELETIONS             ║
║                                                              ║
║  Status: EXPERIMENTAL - Known safety issues exist           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

### Known Safety Issues

**CRITICAL (As of 2025-10-31):**

1. **Parse failures now logged but still risky**
   - Fixed: Errors are now logged with context
   - Risk: Incomplete dependency analysis could mark active files as "unused"
   - Mitigation: **Always use `--dry-run` first and manually verify ALL candidates**

2. **No undo mechanism**
   - Deleted files are archived, not removed
   - Recovery requires manual restoration from archive
   - **RECOMMENDATION:** Commit all work to git before running sweep

3. **Dependency detection limitations**
   - Dynamic imports may not be detected
   - Reflection-based references may be missed
   - Configuration file references may be incomplete

### Required Precautions

**BEFORE using cc_prune:**

1. ✅ **Commit all changes to git** (for easy recovery)
2. ✅ **Run `--dry-run` first** (review planned deletions)
3. ✅ **Manually verify each file** marked for deletion
4. ✅ **Check file permissions** (tool should log errors, but verify logs)
5. ✅ **Run tests after sweep** (verify nothing broke)
6. ✅ **Keep archive for 30+ days** (in case of missed dependencies)

---

## What This Tool Does

`cc_prune` identifies and removes unused files from a repository by:

1. **Building a dependency graph** - Scans code files (Python, TypeScript, JavaScript, shell scripts, docs) to map file relationships
2. **Scoring candidates** - Ranks files by "unused-ness" based on incoming reference count
3. **Review & approval** - Optionally uses Codex AI or manual review to approve deletions
4. **Archiving files** - Moves approved files to archive directory (NOT permanent deletion)

### Use Cases

- Cleaning up stale documentation
- Removing orphaned utility scripts
- Archiving superseded code
- Repository maintenance after major refactors

---

## Installation

```bash
# From repository root
cd tools/cc_prune

# No installation needed - run directly with Python 3.10+
python3 -m cc_prune --help
```

**Dependencies:**
- Python 3.10+
- Optional: `pyyaml` (for YAML manifest parsing)

---

## Usage

### Step 1: Mark Candidates

Scan repository and identify deletion candidates:

```bash
python3 -m cc_prune mark --out /tmp/prune-bundle --quantile 0.85
```

**Options:**
- `--repo PATH` - Repository root (default: current directory)
- `--out DIR` - Output directory for review bundle (required)
- `--quantile FLOAT` - Score threshold 0-1 (default: 0.85, higher = more aggressive)

**Output:** Creates bundle directory with:
- `candidates.json` - List of files with scores
- `graph.json` - Dependency graph
- `metadata.json` - Scan metadata

### Step 2: Review Candidates

Review marked files before deletion:

**Option A: Manual Review**
```bash
# Examine candidates.json
cat /tmp/prune-bundle/candidates.json | python3 -m json.tool | less

# For each file:
# 1. Check if actually unused
# 2. Verify no dynamic references
# 3. Grep for string references: git grep "filename"
```

**Option B: Codex AI Review** (requires Codex access)
```bash
python3 -m cc_prune review --bundle /tmp/prune-bundle --codex-script sdk/providers/run_codex.py
```

**Option C: Auto-approve (highest risk)**
```bash
python3 -m cc_prune review --bundle /tmp/prune-bundle --auto-approve
```

**Output:** Creates `review_decisions.json` with approve/reject decisions

### Step 3: Sweep (Archive Files)

Archive approved files:

**DRY RUN FIRST (mandatory):**
```bash
python3 -m cc_prune sweep --bundle /tmp/prune-bundle --dry-run
```

Review output carefully, then:

```bash
python3 -m cc_prune sweep --bundle /tmp/prune-bundle --archive-root .archive
```

**Options:**
- `--bundle DIR` - Path to review bundle (required)
- `--archive-root DIR` - Archive destination (default: `archive/`)
- `--dry-run` - Show planned actions without executing (ALWAYS USE FIRST)

**What happens:**
- Approved files moved to `archive/YYYY-MM-DD/original/path/file.ext`
- Documentation manifests updated (removes archived files from lists)
- Git working tree modified (use `git status` to review changes)

---

## Recovery

### Restoring an Archived File

```bash
# Files are moved, not deleted
# Archive structure: archive/YYYY-MM-DD/original/path/file.ext

# Find file in archive
find .archive -name "my_file.py"

# Restore to original location
cp .archive/2025-10-31/path/to/my_file.py path/to/my_file.py

# Or restore entire directory
cp -r .archive/2025-10-31/path/to/dir path/to/dir
```

### Emergency Rollback

```bash
# If you committed before sweeping:
git reset --hard HEAD^

# If you didn't commit:
# Manually restore from .archive/ directory
```

---

## How It Works

### Dependency Detection

**Python files (`.py`):**
- Detects: `import foo`, `from foo import bar`
- Limitation: Dynamic imports like `importlib.import_module()` not detected

**TypeScript/JavaScript (`.ts`, `.tsx`, `.js`, `.jsx`):**
- Detects: `import ... from "path"`, `require("path")`, `import("path")`
- Limitation: Dynamically computed imports not detected

**Shell scripts (`.sh`):**
- Detects: File references in commands via regex pattern matching
- Limitation: Variable-based paths not detected

**Documentation (`.md`, `.mdx`):**
- Detects: Markdown links `[text](path)`, HTML links `href="path"`
- Limitation: Broken links not distinguished from valid references

**Configuration files (`.json`, `.yaml`, `.yml`):**
- Detects: Any string values that look like file paths
- Limitation: May produce false positives on non-path strings

### Scoring Algorithm

Files are scored 0-1 based on:
- **Incoming references**: Fewer references = higher score
- **File type**: Some types weighted more "prunable" than others
- **Location**: Files in certain directories may be weighted differently

**Score interpretation:**
- `0.0-0.5`: Actively used
- `0.5-0.8`: Moderately used
- `0.8-0.95`: Likely unused
- `0.95-1.0`: Very likely unused

**Default threshold:** `0.85` (only marks files with score ≥ 0.85)

---

## Logging & Debugging

### Error Logging

As of 2025-10-31, parse errors are now logged:

```bash
# Run with logging to see errors
python3 -m cc_prune mark --out /tmp/bundle 2>&1 | tee prune.log

# Check for parse failures
grep "Failed to" prune.log
```

**Common errors:**
- `Failed to read TS/JS file X: [Errno 13] Permission denied` - Check file permissions
- `Failed to parse JSON manifest X: Expecting value` - Malformed JSON
- `Failed to read documentation file X: [Errno 2] No such file or directory` - Broken symlink

### Debugging False Positives

If a file is marked for deletion but shouldn't be:

```bash
# Check why file was marked
cat /tmp/prune-bundle/candidates.json | python3 -m json.tool | grep -A 5 "filename"

# Find all references to file
git grep -i "filename" | grep -v ".archive"

# Check import graph
cat /tmp/prune-bundle/graph.json | python3 -m json.tool | grep "filename"
```

---

## Safety Checklist

**Before Every Sweep:**

- [ ] Committed all changes to git (`git status` clean)
- [ ] Ran `mark` step successfully (no errors in logs)
- [ ] Reviewed `candidates.json` manually
- [ ] Checked for dynamic references with `git grep`
- [ ] Ran `sweep --dry-run` and verified output
- [ ] Prepared to run tests after sweep
- [ ] Backup important work outside git (if critical)

**After Sweep:**

- [ ] Run `git status` to review changes
- [ ] Run full test suite: `pytest` / `npm test`
- [ ] Check application starts: `python main.py` / `npm start`
- [ ] Monitor logs for import errors
- [ ] Keep archive for 30 days minimum

---

## Limitations & Known Issues

### Current Limitations (2025-10-31)

1. **No failure.emit integration** - Errors logged to stderr only (not membrane events)
2. **No git integration** - Doesn't check git history to find recently used files
3. **No test coverage detection** - Doesn't detect files used only in tests
4. **No runtime profiling** - Can't detect files loaded dynamically at runtime
5. **Codex review optional** - Can auto-approve without AI review

### Future Improvements

- [ ] Integrate with Mind Protocol membrane (emit failure.emit on errors)
- [ ] Add git history analysis (mark recently-used files as active)
- [ ] Add test coverage integration (pytest --cov)
- [ ] Add runtime tracing (detect dynamically loaded modules)
- [ ] Add interactive confirmation prompts
- [ ] Add rollback command (undo last sweep)
- [ ] Add confidence scoring (quantify risk per candidate)

---

## Development

### Running Tests

```bash
# No tests currently exist
# TODO: Add pytest test suite
```

### Contributing

1. **DO NOT** ship features that increase deletion risk
2. **DO** add more safety checks (confirmation prompts, git checks, etc.)
3. **DO** improve dependency detection accuracy
4. **DO** add comprehensive test coverage

**Code quality:** Fixed R-301 violations (silent failures) as of 2025-10-31

---

## Support

**Issues:** Report bugs to Mind Protocol team
**Status:** Experimental - use at own risk
**License:** (See repository root)

---

## Changelog

### 2025-10-31
- 🔴 **SAFETY FIX:** Added error logging to prevent silent parse failures (TICKET-CODEX-001)
- 📝 **Added:** This README with prominent safety warnings (TICKET-CODEX-002)
- ⚠️ **STATUS:** Still not recommended for production use

### 2025-10-30 (Original commit)
- Initial implementation by Codex
- Three-step pipeline: mark → review → sweep
- Dependency detection for Python, TS/JS, shell, docs, manifests
- Quantile-based scoring

---

**Remember: Always `--dry-run` first! This tool deletes files!**
