#!/usr/bin/env python3
"""
Merge Taylor and AI playbooks into a single comprehensive playbook
Removes duplicate frameworks and organizes by type
"""
import json
from pathlib import Path
from src.playbook_generator import generate_playbook

def merge_playbooks():
    """Merge Taylor and AI frameworks, removing duplicates"""

    # Load both framework sets
    with open('frameworks_synthesized/frameworks_taylor_final.json', 'r') as f:
        taylor_frameworks = json.load(f)

    with open('frameworks_synthesized/frameworks_ai_final.json', 'r') as f:
        ai_frameworks = json.load(f)

    print(f"📊 Input:")
    print(f"   Taylor frameworks: {len(taylor_frameworks)}")
    print(f"   AI frameworks: {len(ai_frameworks)}")

    # Create merged set using framework names as keys to avoid duplicates
    frameworks_dict = {}

    # Add AI frameworks first (more comprehensive as they processed all transcripts)
    for fw in ai_frameworks:
        frameworks_dict[fw['framework_name']] = fw

    # Add Taylor frameworks, but skip duplicates
    for fw in taylor_frameworks:
        name = fw['framework_name']
        if name not in frameworks_dict:
            frameworks_dict[name] = fw
        else:
            print(f"   ⚠️  Skipping duplicate: {name}")

    # Convert back to list and sort by type, then name
    merged_frameworks = list(frameworks_dict.values())

    # Sort by framework type, then by name
    type_order = {
        'process_framework': 1,
        'model_framework': 2,
        'decision_framework': 3,
        'measurement_framework': 4,
        'scaling_framework': 5,
        'engagement_framework': 6
    }

    merged_frameworks.sort(key=lambda x: (
        type_order.get(x.get('type', 'process_framework'), 99),
        x['framework_name']
    ))

    print(f"\n📋 Output:")
    print(f"   Unique frameworks: {len(merged_frameworks)}")
    print(f"   Duplicates removed: {len(taylor_frameworks) + len(ai_frameworks) - len(merged_frameworks)}")

    # Save merged frameworks
    output_file = 'frameworks_synthesized/frameworks_combined.json'
    with open(output_file, 'w') as f:
        json.dump(merged_frameworks, f, indent=2)

    print(f"\n✅ Merged frameworks saved to: {output_file}")

    # Generate combined playbook
    print(f"\n📖 Generating Combined Strategic Playbook...")
    generate_playbook(
        output_file,
        'playbooks_generated/Combined_Strategic_Playbook.md',
        'Section Strategic Playbook - Complete Framework Collection'
    )

    # Print framework breakdown by type
    print(f"\n📊 Framework Breakdown:")
    type_counts = {}
    for fw in merged_frameworks:
        fw_type = fw.get('type', 'unknown')
        type_counts[fw_type] = type_counts.get(fw_type, 0) + 1

    for fw_type, count in sorted(type_counts.items()):
        print(f"   {fw_type}: {count} frameworks")

    return merged_frameworks

if __name__ == "__main__":
    merged = merge_playbooks()

    print(f"\n🎉 Combined playbook ready!")
    print(f"   File: playbooks_generated/Combined_Strategic_Playbook.md")
    print(f"   Total frameworks: {len(merged)}")
