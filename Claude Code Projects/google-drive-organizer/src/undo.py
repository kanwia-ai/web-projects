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
