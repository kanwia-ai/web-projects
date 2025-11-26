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
