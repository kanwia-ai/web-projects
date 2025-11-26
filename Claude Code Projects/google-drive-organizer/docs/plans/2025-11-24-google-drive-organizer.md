# Google Drive Organizer Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python tool that scans My Drive, matches files to client folders by filename patterns, generates a preview for human review, and executes moves after approval.

**Architecture:** Two-phase approach with human-in-the-loop. Phase 1 scans files and generates a CSV preview showing proposed moves. Phase 2 reads the approved CSV and executes file moves. All operations logged for reversibility.

**Tech Stack:** Python 3 (standard library only - os, shutil, csv, pathlib, re)

---

## Configuration Constants

These paths are specific to this Google Drive setup:

```python
GDRIVE_ROOT = "/Users/kyraatekwana/Library/CloudStorage/GoogleDrive-katekwana@sectionai.com"
MY_DRIVE = f"{GDRIVE_ROOT}/My Drive"
CLIENTS_FOLDER = f"{GDRIVE_ROOT}/Shared drives/Enterprise/Clients"
PROJECT_DIR = "/Users/kyraatekwana/Documents/Claude Projects/google-drive-organizer"
```

---

### Task 1: Create Project Structure

**Files:**
- Create: `src/__init__.py`
- Create: `src/config.py`

**Step 1: Create empty __init__.py**

```python
# src/__init__.py
# Google Drive Organizer
```

**Step 2: Create config.py with paths**

```python
# src/config.py
"""Configuration constants for Google Drive Organizer."""

from pathlib import Path

# Google Drive paths
GDRIVE_ROOT = Path("/Users/kyraatekwana/Library/CloudStorage/GoogleDrive-katekwana@sectionai.com")
MY_DRIVE = GDRIVE_ROOT / "My Drive"
CLIENTS_FOLDER = GDRIVE_ROOT / "Shared drives/Enterprise/Clients"

# Project paths
PROJECT_DIR = Path("/Users/kyraatekwana/Documents/Claude Projects/google-drive-organizer")
OUTPUT_DIR = PROJECT_DIR / "output"

# Bracket prefixes that are NOT client names (should be ignored)
NON_CLIENT_PREFIXES = [
    "ARCHIVED",
    "INTERNAL",
    "OLD",
    "CUSTOMIZATION TEMPLATE",
    "MAKE A COPY",
    "NEW",
    "PUBLIC",
    "SECTION VERSION",
    "SPEAKER",
    "KYRA'S NOTES",
    "OLD DO NOT USE",
]
```

**Step 3: Create output directory**

Run: `mkdir -p "/Users/kyraatekwana/Documents/Claude Projects/google-drive-organizer/output"`

**Step 4: Commit**

```bash
cd "/Users/kyraatekwana/Documents/Claude Projects/google-drive-organizer"
git init
git add src/
git commit -m "feat: add project structure and config"
```

---

### Task 2: Build Client Name Extractor

**Files:**
- Create: `src/clients.py`

**Step 1: Create clients.py**

```python
# src/clients.py
"""Extract client folder names from Enterprise/Clients."""

import os
from pathlib import Path
from config import CLIENTS_FOLDER

def get_client_folders() -> list[str]:
    """
    Get list of client folder names from Enterprise/Clients.
    Excludes files (only returns directories).
    """
    clients = []
    for item in os.listdir(CLIENTS_FOLDER):
        item_path = CLIENTS_FOLDER / item
        if item_path.is_dir():
            clients.append(item)
    return sorted(clients)


def build_client_variations(clients: list[str]) -> dict[str, str]:
    """
    Build a mapping of normalized client name variations to folder names.

    For example:
    - "AB InBev" -> variations include "ab inbev", "abinbev", "ab-inbev"
    - "e.l.f. Beauty" -> variations include "elf", "e.l.f."

    Returns: dict mapping lowercase variation -> original folder name
    """
    variations = {}

    for client in clients:
        # Original (lowercase)
        lower = client.lower()
        variations[lower] = client

        # Remove spaces
        no_spaces = lower.replace(" ", "")
        variations[no_spaces] = client

        # Replace spaces with common separators
        variations[lower.replace(" ", "-")] = client
        variations[lower.replace(" ", "_")] = client

        # Remove punctuation (for e.l.f. -> elf)
        import re
        no_punct = re.sub(r'[^\w\s]', '', lower)
        variations[no_punct] = client
        variations[no_punct.replace(" ", "")] = client

    return variations


if __name__ == "__main__":
    clients = get_client_folders()
    print(f"Found {len(clients)} client folders:")
    for c in clients[:10]:
        print(f"  - {c}")
    print("  ...")
```

**Step 2: Test the client extractor**

Run: `cd "/Users/kyraatekwana/Documents/Claude Projects/google-drive-organizer" && python3 src/clients.py`

Expected: List of client folders printed

**Step 3: Commit**

```bash
git add src/clients.py
git commit -m "feat: add client folder extraction"
```

---

### Task 3: Build File Scanner

**Files:**
- Create: `src/scanner.py`

**Step 1: Create scanner.py**

```python
# src/scanner.py
"""Scan My Drive and match files to client folders."""

import os
import re
from pathlib import Path
from config import MY_DRIVE, NON_CLIENT_PREFIXES
from clients import get_client_folders, build_client_variations


def get_my_drive_files() -> list[Path]:
    """
    Get all files from My Drive root (not recursive into folders for now).
    Returns list of Path objects.
    """
    files = []
    for item in os.listdir(MY_DRIVE):
        item_path = MY_DRIVE / item
        if item_path.is_file():
            files.append(item_path)
    return files


def extract_bracket_prefix(filename: str) -> str | None:
    """
    Extract text inside brackets at start of filename.
    "[UNILEVER] AI Workshop.gdoc" -> "UNILEVER"
    "Regular file.gdoc" -> None
    """
    match = re.match(r'^\[([^\]]+)\]', filename)
    if match:
        return match.group(1)
    return None


def is_non_client_prefix(prefix: str) -> bool:
    """Check if bracket prefix is a known non-client prefix."""
    return prefix.upper() in [p.upper() for p in NON_CLIENT_PREFIXES]


def match_file_to_client(filename: str, client_variations: dict[str, str]) -> str | None:
    """
    Try to match a filename to a client folder.

    Strategy:
    1. Check for bracket prefix first (highest confidence)
    2. Check if any client name appears in filename

    Returns: client folder name or None
    """
    # Strategy 1: Bracket prefix
    prefix = extract_bracket_prefix(filename)
    if prefix:
        if is_non_client_prefix(prefix):
            return None
        # Try to match prefix to a client
        prefix_lower = prefix.lower()
        if prefix_lower in client_variations:
            return client_variations[prefix_lower]
        # Try partial match
        for variation, client in client_variations.items():
            if variation in prefix_lower or prefix_lower in variation:
                return client

    # Strategy 2: Client name in filename
    filename_lower = filename.lower()

    # Remove common prefixes/patterns that might cause false matches
    # Check for longer client names first (more specific)
    sorted_clients = sorted(client_variations.keys(), key=len, reverse=True)

    for variation in sorted_clients:
        # Only match if it's a word boundary (not part of another word)
        # Minimum 3 chars to avoid false matches
        if len(variation) >= 3 and variation in filename_lower:
            return client_variations[variation]

    return None


def scan_and_match() -> list[dict]:
    """
    Scan all My Drive files and match them to clients.

    Returns: list of dicts with file info and match results
    """
    files = get_my_drive_files()
    clients = get_client_folders()
    variations = build_client_variations(clients)

    results = []
    for file_path in files:
        filename = file_path.name
        matched_client = match_file_to_client(filename, variations)

        results.append({
            "filename": filename,
            "source_path": str(file_path),
            "matched_client": matched_client,
            "status": "MATCHED" if matched_client else "UNMATCHED"
        })

    return results


if __name__ == "__main__":
    results = scan_and_match()
    matched = [r for r in results if r["status"] == "MATCHED"]
    unmatched = [r for r in results if r["status"] == "UNMATCHED"]

    print(f"Total files: {len(results)}")
    print(f"Matched: {len(matched)}")
    print(f"Unmatched: {len(unmatched)}")
    print("\nSample matches:")
    for r in matched[:10]:
        print(f"  {r['filename'][:50]}... -> {r['matched_client']}")
```

**Step 2: Test the scanner**

Run: `cd "/Users/kyraatekwana/Documents/Claude Projects/google-drive-organizer" && python3 src/scanner.py`

Expected: Summary of matched vs unmatched files

**Step 3: Commit**

```bash
git add src/scanner.py
git commit -m "feat: add file scanner with client matching"
```

---

### Task 4: Build Preview Generator

**Files:**
- Create: `src/preview.py`

**Step 1: Create preview.py**

```python
# src/preview.py
"""Generate preview CSV of proposed file moves."""

import csv
from datetime import datetime
from pathlib import Path
from config import OUTPUT_DIR, CLIENTS_FOLDER
from scanner import scan_and_match


def generate_preview() -> Path:
    """
    Generate a CSV preview of all proposed moves.

    CSV columns:
    - filename: Original filename
    - source_path: Full path to source file
    - matched_client: Client folder name (or empty)
    - destination_path: Proposed destination (or empty)
    - status: MATCHED or UNMATCHED
    - approved: Empty column for human to fill in (Y/N)

    Returns: Path to generated CSV file
    """
    results = scan_and_match()

    # Add destination paths
    for r in results:
        if r["matched_client"]:
            r["destination_path"] = str(CLIENTS_FOLDER / r["matched_client"] / r["filename"])
        else:
            r["destination_path"] = ""
        r["approved"] = ""  # Human fills this in

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"preview_{timestamp}.csv"

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Write CSV
    fieldnames = ["status", "approved", "filename", "matched_client", "source_path", "destination_path"]

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # Write matched first, then unmatched
        matched = sorted([r for r in results if r["status"] == "MATCHED"], key=lambda x: x["matched_client"])
        unmatched = sorted([r for r in results if r["status"] == "UNMATCHED"], key=lambda x: x["filename"])

        for r in matched + unmatched:
            writer.writerow({k: r[k] for k in fieldnames})

    return output_file


def print_summary(results: list[dict]):
    """Print summary statistics."""
    matched = [r for r in results if r["status"] == "MATCHED"]
    unmatched = [r for r in results if r["status"] == "UNMATCHED"]

    print("\n" + "="*60)
    print("GOOGLE DRIVE ORGANIZER - PREVIEW SUMMARY")
    print("="*60)
    print(f"\nTotal files scanned: {len(results)}")
    print(f"Matched to clients:  {len(matched)}")
    print(f"Unmatched:           {len(unmatched)}")

    if matched:
        print(f"\nTop clients by file count:")
        client_counts = {}
        for r in matched:
            client = r["matched_client"]
            client_counts[client] = client_counts.get(client, 0) + 1

        for client, count in sorted(client_counts.items(), key=lambda x: -x[1])[:10]:
            print(f"  {client}: {count} files")


if __name__ == "__main__":
    print("Scanning My Drive and matching to clients...")
    results = scan_and_match()
    print_summary(results)

    print("\nGenerating preview CSV...")
    output_file = generate_preview()
    print(f"\nPreview saved to: {output_file}")
    print("\nNEXT STEPS:")
    print("1. Open the CSV in Google Sheets or Excel")
    print("2. Review the MATCHED files - correct any wrong matches")
    print("3. Mark 'approved' column with 'Y' for files to move")
    print("4. Save the CSV")
    print("5. Run: python3 src/execute.py <path-to-approved-csv>")
```

**Step 2: Test preview generation**

Run: `cd "/Users/kyraatekwana/Documents/Claude Projects/google-drive-organizer" && python3 src/preview.py`

Expected: CSV file created in output/ directory

**Step 3: Commit**

```bash
git add src/preview.py
git commit -m "feat: add preview CSV generator"
```

---

### Task 5: Build Move Executor

**Files:**
- Create: `src/execute.py`

**Step 1: Create execute.py**

```python
# src/execute.py
"""Execute approved file moves from preview CSV."""

import csv
import shutil
import sys
from datetime import datetime
from pathlib import Path
from config import OUTPUT_DIR


def load_approved_moves(csv_path: Path) -> list[dict]:
    """
    Load moves that have been approved (approved column = 'Y' or 'y').
    """
    approved = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("approved", "").upper() == "Y":
                approved.append(row)

    return approved


def execute_moves(approved_moves: list[dict], dry_run: bool = True) -> tuple[list[dict], list[dict]]:
    """
    Execute the approved file moves.

    Args:
        approved_moves: List of move dicts from CSV
        dry_run: If True, only simulate (don't actually move)

    Returns: (successful_moves, failed_moves)
    """
    successful = []
    failed = []

    for move in approved_moves:
        source = Path(move["source_path"])
        dest = Path(move["destination_path"])

        try:
            if not source.exists():
                raise FileNotFoundError(f"Source file not found: {source}")

            if dest.exists():
                raise FileExistsError(f"Destination already exists: {dest}")

            if not dry_run:
                # Ensure destination directory exists
                dest.parent.mkdir(parents=True, exist_ok=True)
                # Move the file
                shutil.move(str(source), str(dest))

            move["result"] = "SUCCESS" if not dry_run else "DRY_RUN_OK"
            successful.append(move)

        except Exception as e:
            move["result"] = f"FAILED: {str(e)}"
            failed.append(move)

    return successful, failed


def write_log(successful: list[dict], failed: list[dict], dry_run: bool) -> Path:
    """Write execution log for reversibility."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = "dryrun" if dry_run else "executed"
    log_file = OUTPUT_DIR / f"{prefix}_{timestamp}.csv"

    all_moves = successful + failed

    with open(log_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ["result", "filename", "source_path", "destination_path", "matched_client"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for move in all_moves:
            writer.writerow({k: move.get(k, "") for k in fieldnames})

    return log_file


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 src/execute.py <preview_csv_path> [--execute]")
        print("\nBy default, runs in dry-run mode (no files moved)")
        print("Add --execute flag to actually move files")
        sys.exit(1)

    csv_path = Path(sys.argv[1])
    dry_run = "--execute" not in sys.argv

    if not csv_path.exists():
        print(f"Error: CSV file not found: {csv_path}")
        sys.exit(1)

    print(f"\nLoading approved moves from: {csv_path}")
    approved = load_approved_moves(csv_path)

    if not approved:
        print("No approved moves found (mark 'approved' column with 'Y')")
        sys.exit(0)

    print(f"Found {len(approved)} approved moves")

    if dry_run:
        print("\n*** DRY RUN MODE - No files will be moved ***")
        print("Add --execute flag to actually move files\n")
    else:
        print("\n*** EXECUTE MODE - Files WILL be moved ***")
        confirm = input("Type 'YES' to confirm: ")
        if confirm != "YES":
            print("Aborted.")
            sys.exit(0)

    print("\nProcessing moves...")
    successful, failed = execute_moves(approved, dry_run=dry_run)

    print(f"\nResults:")
    print(f"  Successful: {len(successful)}")
    print(f"  Failed: {len(failed)}")

    if failed:
        print("\nFailed moves:")
        for move in failed:
            print(f"  {move['filename']}: {move['result']}")

    log_file = write_log(successful, failed, dry_run)
    print(f"\nLog saved to: {log_file}")

    if dry_run and successful:
        print("\nTo execute for real, run:")
        print(f"  python3 src/execute.py {csv_path} --execute")


if __name__ == "__main__":
    main()
```

**Step 2: Verify execute.py syntax**

Run: `python3 -m py_compile "/Users/kyraatekwana/Documents/Claude Projects/google-drive-organizer/src/execute.py"`

Expected: No output (syntax OK)

**Step 3: Commit**

```bash
git add src/execute.py
git commit -m "feat: add move executor with dry-run mode"
```

---

### Task 6: Create Main Entry Point

**Files:**
- Create: `organize.py` (in project root)

**Step 1: Create organize.py**

```python
#!/usr/bin/env python3
# organize.py
"""
Google Drive Organizer - Main Entry Point

Usage:
    python3 organize.py preview    # Generate preview CSV
    python3 organize.py execute <csv_path>  # Dry run
    python3 organize.py execute <csv_path> --execute  # Actually move files
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from preview import generate_preview, scan_and_match, print_summary
from execute import main as execute_main


def show_help():
    print(__doc__)


def cmd_preview():
    print("="*60)
    print("GOOGLE DRIVE ORGANIZER")
    print("="*60)
    print("\nScanning My Drive...")

    results = scan_and_match()
    print_summary(results)

    print("\nGenerating preview CSV...")
    output_file = generate_preview()

    print(f"\n>>> Preview saved to: {output_file}")
    print("\nNEXT STEPS:")
    print("1. Open the CSV in Google Sheets or Excel")
    print("2. Review MATCHED files - correct any wrong matches")
    print("3. For files you want to move, put 'Y' in the 'approved' column")
    print("4. Save the CSV")
    print(f"5. Run: python3 organize.py execute {output_file}")


def main():
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)

    command = sys.argv[1]

    if command == "preview":
        cmd_preview()
    elif command == "execute":
        # Pass remaining args to execute
        sys.argv = ["execute.py"] + sys.argv[2:]
        execute_main()
    else:
        show_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
```

**Step 2: Make executable**

Run: `chmod +x "/Users/kyraatekwana/Documents/Claude Projects/google-drive-organizer/organize.py"`

**Step 3: Test help**

Run: `cd "/Users/kyraatekwana/Documents/Claude Projects/google-drive-organizer" && python3 organize.py`

Expected: Help text displayed

**Step 4: Commit**

```bash
git add organize.py
git commit -m "feat: add main entry point"
```

---

### Task 7: Test Full Preview Flow

**Step 1: Run preview command**

Run: `cd "/Users/kyraatekwana/Documents/Claude Projects/google-drive-organizer" && python3 organize.py preview`

Expected:
- Summary of matched/unmatched files
- CSV file path printed

**Step 2: Verify CSV was created**

Run: `ls -la "/Users/kyraatekwana/Documents/Claude Projects/google-drive-organizer/output/"`

Expected: preview_*.csv file exists

**Step 3: Check first few lines of CSV**

Run: `head -20 "/Users/kyraatekwana/Documents/Claude Projects/google-drive-organizer/output/preview_"*.csv`

Expected: CSV with headers and file data

---

### Task 8: Test Dry Run Execute Flow

**Step 1: Create a test CSV with one approved move**

For testing, manually mark one row in the preview CSV with 'Y' in approved column, then run:

Run: `cd "/Users/kyraatekwana/Documents/Claude Projects/google-drive-organizer" && python3 organize.py execute output/preview_*.csv`

Expected:
- Dry run summary
- No files actually moved
- Log file created

---

### Task 9: Add Undo Script

**Files:**
- Create: `src/undo.py`

**Step 1: Create undo.py**

```python
# src/undo.py
"""Undo executed moves using the execution log."""

import csv
import shutil
import sys
from pathlib import Path
from config import OUTPUT_DIR


def undo_moves(log_path: Path, dry_run: bool = True) -> tuple[list, list]:
    """
    Undo moves by reading an execution log and reversing them.

    Only undoes rows where result was SUCCESS.
    """
    successful = []
    failed = []

    with open(log_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["result"] != "SUCCESS":
                continue

            # Reverse: destination -> source
            current_path = Path(row["destination_path"])
            original_path = Path(row["source_path"])

            try:
                if not current_path.exists():
                    raise FileNotFoundError(f"File not at destination: {current_path}")

                if original_path.exists():
                    raise FileExistsError(f"Original location occupied: {original_path}")

                if not dry_run:
                    shutil.move(str(current_path), str(original_path))

                row["undo_result"] = "UNDONE" if not dry_run else "DRY_RUN_OK"
                successful.append(row)

            except Exception as e:
                row["undo_result"] = f"FAILED: {str(e)}"
                failed.append(row)

    return successful, failed


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 src/undo.py <execution_log.csv> [--execute]")
        print("\nBy default, runs in dry-run mode")
        sys.exit(1)

    log_path = Path(sys.argv[1])
    dry_run = "--execute" not in sys.argv

    if not log_path.exists():
        print(f"Error: Log file not found: {log_path}")
        sys.exit(1)

    print(f"\nReading execution log: {log_path}")

    if dry_run:
        print("\n*** DRY RUN MODE - No files will be moved ***\n")
    else:
        print("\n*** EXECUTE MODE - Files WILL be moved back ***")
        confirm = input("Type 'UNDO' to confirm: ")
        if confirm != "UNDO":
            print("Aborted.")
            sys.exit(0)

    successful, failed = undo_moves(log_path, dry_run=dry_run)

    print(f"\nResults:")
    print(f"  Undone: {len(successful)}")
    print(f"  Failed: {len(failed)}")

    if failed:
        print("\nFailed undos:")
        for row in failed:
            print(f"  {row['filename']}: {row['undo_result']}")


if __name__ == "__main__":
    main()
```

**Step 2: Commit**

```bash
git add src/undo.py
git commit -m "feat: add undo script for reversibility"
```

---

### Task 10: Final Commit and Documentation

**Step 1: Create minimal README**

```bash
cat > "/Users/kyraatekwana/Documents/Claude Projects/google-drive-organizer/README.md" << 'EOF'
# Google Drive Organizer

Organizes files from My Drive into Enterprise/Clients folders based on filename patterns.

## Usage

```bash
# Step 1: Generate preview
python3 organize.py preview

# Step 2: Review CSV, mark approved moves with 'Y'

# Step 3: Dry run
python3 organize.py execute output/preview_TIMESTAMP.csv

# Step 4: Execute for real
python3 organize.py execute output/preview_TIMESTAMP.csv --execute

# If needed: Undo
python3 src/undo.py output/executed_TIMESTAMP.csv --execute
```
EOF
```

**Step 2: Final commit**

```bash
git add README.md
git commit -m "docs: add README"
```

---

## Summary

After completing all tasks, you will have:

1. **`organize.py preview`** - Scans My Drive, matches files to clients, generates CSV
2. **`organize.py execute`** - Dry run or execute approved moves from CSV
3. **`src/undo.py`** - Reverse moves if something went wrong
4. All operations logged in `output/` directory

**Workflow for users:**
1. Run preview
2. Open CSV in Google Sheets
3. Review matches, mark approved with 'Y'
4. Run dry run to verify
5. Run execute to move files
6. Manually organize within client folders
