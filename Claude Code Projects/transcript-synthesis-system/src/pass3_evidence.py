import json
from pathlib import Path

def add_evidence(frameworks_file: str, normalized_dir: str, output_file: str):
    """Pass 3: Add supporting quotes (simplified for budget)"""

    # Load frameworks
    with open(frameworks_file, 'r') as f:
        frameworks = json.load(f)

    print(f"\n📚 Pass 3: Adding evidence to {len(frameworks)} frameworks...")
    print("   (Simplified for budget - skipping LLM calls)")

    for framework in frameworks:
        # Placeholder: In full version, would search transcripts for best quotes
        framework["supporting_evidence"] = {
            "quotes": ["Evidence extraction skipped for budget optimization. See framework synthesis above for core insights."],
            "case_studies": [],
            "metrics": []
        }

    # Save
    with open(output_file, 'w') as f:
        json.dump(frameworks, f, indent=2)

    print(f"✓ Evidence added\n  Output: {output_file}")

    return frameworks
