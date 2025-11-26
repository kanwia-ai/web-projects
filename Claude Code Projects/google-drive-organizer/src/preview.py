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
