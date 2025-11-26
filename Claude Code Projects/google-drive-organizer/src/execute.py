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
