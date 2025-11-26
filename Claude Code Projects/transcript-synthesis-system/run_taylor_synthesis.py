#!/usr/bin/env python3
"""
Generate Taylor Strategic Playbook from coaching/strategic transcripts
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

def run_taylor_playbook():
    """Run full pipeline for Taylor strategic playbook"""

    print("\n" + "="*70)
    print("TAYLOR STRATEGIC PLAYBOOK GENERATION")
    print("="*70)

    # Step 1: Filter Taylor transcripts
    print("\n📋 Step 1: Filtering Taylor/strategic transcripts...")
    taylor_files = filter_transcripts('transcripts_normalized', category='taylor')
    print(f"   Found {len(taylor_files)} Taylor transcripts")

    # Create temp directory with Taylor transcripts
    temp_dir = Path("transcripts_taylor_temp")
    temp_dir.mkdir(exist_ok=True)

    # Copy Taylor transcripts to temp directory
    for f in taylor_files:
        import shutil
        shutil.copy(f, temp_dir / f.name)

    print(f"   Copied to {temp_dir}/")

    # Step 2: Discovery
    print("\n🔍 Step 2: Running Discovery (Pass 1)...")
    print(f"   Processing {len(taylor_files)} transcripts")
    print("   Model: claude-sonnet-4-5")
    print("   Estimated cost: $0.80-1.20")

    frameworks_discovered = "frameworks_taylor_discovered"
    discover_frameworks(
        str(temp_dir),
        frameworks_discovered,
        model='claude-sonnet-4-5',
        limit=len(taylor_files)  # Process all Taylor transcripts
    )

    # Step 3: Synthesis
    print("\n🧬 Step 3: Running Synthesis (Pass 2)...")
    print("   Model: claude-opus-4-1")
    print("   Estimated cost: $0.25-1.00")

    frameworks_candidates_file = f"{frameworks_discovered}/framework_candidates.json"
    frameworks_synthesized_dir = "frameworks_synthesized"
    synthesize_frameworks(
        frameworks_candidates_file,
        frameworks_synthesized_dir,
        model='claude-opus-4-1'
    )

    # Step 4: Evidence (simplified for budget)
    print("\n📚 Step 4: Adding Evidence (Pass 3 - simplified)...")
    frameworks_synthesized_file = f"{frameworks_synthesized_dir}/frameworks_synthesized.json"
    frameworks_with_evidence = "frameworks_synthesized/frameworks_taylor_evidence.json"
    add_evidence(
        frameworks_synthesized_file,
        str(temp_dir),
        frameworks_with_evidence
    )

    # Step 5: Actionability
    print("\n✅ Step 5: Adding Actionability (Pass 4)...")
    print("   Model: claude-sonnet-4-5")
    print("   Estimated cost: $0.30-0.50")

    frameworks_final = "frameworks_synthesized/frameworks_taylor_final.json"
    add_actionability(
        frameworks_with_evidence,
        frameworks_final,
        model='claude-sonnet-4-5'
    )

    # Step 6: Generate playbook
    print("\n📖 Step 6: Generating Playbook...")
    generate_playbook(
        frameworks_final,
        "playbooks_generated/Taylor_Strategic_Playbook.md",
        "Taylor Strategic Thinking & Coaching Playbook"
    )

    # Step 7: Generate PDF
    print("\n📄 Step 7: Generating PDF...")
    import subprocess
    subprocess.run([
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "--headless",
        "--disable-gpu",
        "--print-to-pdf=playbooks_generated/Taylor_Strategic_Playbook.pdf",
        "--no-margins",
        "file://" + str(Path("playbooks_generated/Taylor_Strategic_Playbook.html").absolute())
    ])

    # Cleanup temp directory
    import shutil
    shutil.rmtree(temp_dir)

    # Print summary
    print("\n" + "="*70)
    print("TAYLOR PLAYBOOK COMPLETE")
    print("="*70)
    print(tracker.get_summary())

    # Count frameworks
    with open(frameworks_final, 'r') as f:
        frameworks = json.load(f)

    print(f"\n✅ Generated Taylor Strategic Playbook")
    print(f"   Frameworks: {len(frameworks)}")
    print(f"   Files: playbooks_generated/Taylor_Strategic_Playbook.md")
    print(f"   PDF: playbooks_generated/Taylor_Strategic_Playbook.pdf")
    print()

if __name__ == "__main__":
    run_taylor_playbook()
