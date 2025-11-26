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
