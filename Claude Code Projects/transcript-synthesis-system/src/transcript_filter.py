#!/usr/bin/env python3
"""
Transcript filtering utility for separating Taylor/strategic vs AI/client transcripts
"""
from pathlib import Path
from typing import List, Set
import json

# Keywords for Taylor/Strategic transcripts
TAYLOR_PATTERNS = {
    'kyra', 'taylor', 'coaching', '1-on-1', 'interview',
    'tom', 'alli', 'bobby', 'scott', 'lauren', 'louise',
    'strategic', 'workshop lead', 'lunch & learn', 'bootcamp',
    'consulting weekly', 'proposal review', 'amanda lennon',
    'ana portugal', 'alyson', 'hannah tsumoto', 'lisa read',
    'patrick johnson', 'stephanie ford', 'valentina',
    'sandra noonan', 'refining ai workflows'
}

# Keywords to EXCLUDE (personal, not work)
EXCLUDE_PATTERNS = {
    'funeral', 'maryland', 'pa nkwate'
}

# Keywords for AI/Client transcripts
CLIENT_PATTERNS = {
    'discovery session', 'prioritization', 'asurion', 'adobe',
    'doordash', 'havas', 'pernod ricard', 'martech',
    'marketing offsite', 'berkeley', 'client', 'deck',
    'product teardown', 'prd'
}

def categorize_transcript(filename: str) -> str:
    """
    Categorize transcript based on filename
    Returns: 'taylor', 'client', or 'exclude'
    """
    lower_name = filename.lower()

    # Check exclusions first
    if any(pattern in lower_name for pattern in EXCLUDE_PATTERNS):
        return 'exclude'

    # Check Taylor patterns
    taylor_score = sum(1 for pattern in TAYLOR_PATTERNS if pattern in lower_name)

    # Check client patterns
    client_score = sum(1 for pattern in CLIENT_PATTERNS if pattern in lower_name)

    # Categorize based on scores
    if taylor_score > client_score:
        return 'taylor'
    elif client_score > 0:
        return 'client'
    else:
        # Default to client for ambiguous cases
        return 'client'

def filter_transcripts(
    input_dir: str,
    category: str = 'taylor'
) -> List[Path]:
    """
    Filter transcripts by category

    Args:
        input_dir: Directory containing normalized transcripts
        category: 'taylor' or 'client' or 'all'

    Returns:
        List of Path objects for matching transcripts
    """
    input_path = Path(input_dir)
    all_files = sorted(input_path.glob("*.json"))

    if category == 'all':
        # Return all except excluded
        return [
            f for f in all_files
            if categorize_transcript(f.stem) != 'exclude'
        ]

    # Filter by category
    filtered = [
        f for f in all_files
        if categorize_transcript(f.stem) == category
    ]

    return filtered

def print_categorization_report(input_dir: str):
    """Print categorization statistics"""
    input_path = Path(input_dir)
    all_files = list(input_path.glob("*.json"))

    taylor_files = []
    client_files = []
    excluded_files = []

    for f in all_files:
        cat = categorize_transcript(f.stem)
        if cat == 'taylor':
            taylor_files.append(f)
        elif cat == 'client':
            client_files.append(f)
        else:
            excluded_files.append(f)

    print("\n📊 Transcript Categorization Report")
    print("=" * 60)
    print(f"Total transcripts: {len(all_files)}")
    print(f"Taylor/Strategic: {len(taylor_files)}")
    print(f"AI/Client: {len(client_files)}")
    print(f"Excluded: {len(excluded_files)}")
    print()

    if excluded_files:
        print("Excluded files:")
        for f in excluded_files:
            print(f"  - {f.stem}")
        print()

    print(f"Sample Taylor transcripts ({min(5, len(taylor_files))}):")
    for f in taylor_files[:5]:
        print(f"  - {f.stem}")
    print()

    print(f"Sample Client transcripts ({min(5, len(client_files))}):")
    for f in client_files[:5]:
        print(f"  - {f.stem}")
    print()

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        input_dir = sys.argv[1]
    else:
        input_dir = "transcripts_normalized"

    print_categorization_report(input_dir)
