#!/usr/bin/env python3
"""
Generate AI Transformation Playbook from ALL transcripts
"""
import sys
from pathlib import Path
from src.transcript_filter import filter_transcripts
from src.pass1_discovery import discover_frameworks
from src.pass2_synthesis import synthesize_frameworks
from src.pass3_evidence import add_evidence
from src.pass4_actionability import add_actionability
from src.playbook_generator import generate_playbook
from src.cost_tracker import tracker
import json

def run_ai_playbook():
    """Run full pipeline for AI transformation playbook"""

    print("\n" + "="*70)
    print("AI TRANSFORMATION PLAYBOOK GENERATION")
    print("="*70)

    # Step 1: Get all transcripts (except excluded)
    print("\n📋 Step 1: Collecting all transcripts...")
    all_files = filter_transcripts('transcripts_normalized', category='all')
    print(f"   Found {len(all_files)} transcripts (excluding personal)")

    # Step 2: Discovery
    print("\n🔍 Step 2: Running Discovery (Pass 1)...")
    print(f"   Processing ALL {len(all_files)} transcripts")
    print("   Model: claude-sonnet-4-5")
    print("   Estimated cost: $2.00-3.00")

    frameworks_discovered = "frameworks_ai_discovered"
    discover_frameworks(
        'transcripts_normalized',
        frameworks_discovered,
        model='claude-sonnet-4-5',
        limit=len(all_files)  # Process ALL transcripts
    )

    # Step 3: Synthesis
    print("\n🧬 Step 3: Running Synthesis (Pass 2)...")
    print("   Model: claude-opus-4-1")
    print("   Estimated cost: $0.50-1.50")

    frameworks_synthesized_dir = "frameworks_ai_synthesized"
    synthesize_frameworks(
        f"{frameworks_discovered}/framework_candidates.json",
        frameworks_synthesized_dir,
        model='claude-opus-4-1',
        max_frameworks=15  # Generate 15 comprehensive frameworks
    )

    # Step 4: Evidence (simplified for budget)
    print("\n📚 Step 4: Adding Evidence (Pass 3 - simplified)...")
    frameworks_synthesized = f"{frameworks_synthesized_dir}/frameworks_synthesized.json"
    frameworks_with_evidence = "frameworks_synthesized/frameworks_ai_evidence.json"
    add_evidence(
        frameworks_synthesized,
        'transcripts_normalized',
        frameworks_with_evidence
    )

    # Step 5: Actionability
    print("\n✅ Step 5: Adding Actionability (Pass 4)...")
    print("   Model: claude-sonnet-4-5")
    print("   Estimated cost: $0.50-1.00")

    frameworks_final = "frameworks_synthesized/frameworks_ai_final.json"
    add_actionability(
        frameworks_with_evidence,
        frameworks_final,
        model='claude-sonnet-4-5'
    )

    # Step 6: Generate playbook
    print("\n📖 Step 6: Generating Playbook...")
    generate_playbook(
        frameworks_final,
        "playbooks_generated/AI_Transformation_Playbook.md",
        "Section AI Transformation Playbook"
    )

    # Step 7: Generate PDF
    print("\n📄 Step 7: Generating PDF...")
    import subprocess
    subprocess.run([
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "--headless",
        "--disable-gpu",
        "--print-to-pdf=playbooks_generated/AI_Transformation_Playbook.pdf",
        "--no-margins",
        "file://" + str(Path("playbooks_generated/AI_Transformation_Playbook.html").absolute())
    ])

    # Print summary
    print("\n" + "="*70)
    print("AI TRANSFORMATION PLAYBOOK COMPLETE")
    print("="*70)
    print(tracker.get_summary())

    # Count frameworks
    with open(frameworks_final, 'r') as f:
        frameworks = json.load(f)

    print(f"\n✅ Generated AI Transformation Playbook")
    print(f"   Frameworks: {len(frameworks)}")
    print(f"   Files: playbooks_generated/AI_Transformation_Playbook.md")
    print(f"   PDF: playbooks_generated/AI_Transformation_Playbook.pdf")
    print()

if __name__ == "__main__":
    run_ai_playbook()
