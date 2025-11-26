# Separate Taylor & AI Transformation Playbooks Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Generate two distinct playbooks - Taylor Strategic Playbook (coaching/strategic thinking frameworks from 35-45 internal transcripts) and AI Transformation Playbook (implementation frameworks from all 109 transcripts)

**Architecture:** Create transcript filtering utility, run synthesis pipeline twice with different transcript sets, generate separate playbooks with distinct framework sets

**Tech Stack:** Python 3.11+, existing src/ modules (pass1-4, playbook_generator), Claude Sonnet 4.5 & Opus 4.1 APIs

**Budget:** ~$3.50-5.50 (within $50 limit, currently spent $1.15)

---

## Task 1: Create Transcript Filter Utility

**Files:**
- Create: `src/transcript_filter.py`
- Test: Manual verification with list commands

**Step 1: Write transcript categorization script**

```python
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
```

**Step 2: Test categorization**

Run: `cd /Users/kyraatekwana/Desktop/Claude\ Code\ Projects/transcript-synthesis-system && python3 src/transcript_filter.py`

Expected: Report showing ~35-45 Taylor transcripts, ~65-75 client transcripts, ~2 excluded

**Step 3: Commit filter utility**

```bash
git add src/transcript_filter.py
git commit -m "feat: add transcript categorization utility

- Filters transcripts into Taylor/strategic vs AI/client categories
- Excludes personal/non-work transcripts
- Provides categorization report"
```

---

## Task 2: Generate Taylor Strategic Playbook

**Files:**
- Modify: `src/pass1_discovery.py` (temporarily for filtered input)
- Output: `frameworks_synthesized/frameworks_taylor.json`
- Output: `playbooks_generated/Taylor_Strategic_Playbook.md`
- Output: `playbooks_generated/Taylor_Strategic_Playbook.pdf`

**Step 1: Create Taylor-specific synthesis script**

Create: `run_taylor_synthesis.py`

```python
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

    frameworks_synthesized = "frameworks_synthesized/frameworks_taylor.json"
    synthesize_frameworks(
        frameworks_discovered,
        frameworks_synthesized,
        model='claude-opus-4-1'
    )

    # Step 4: Evidence (simplified for budget)
    print("\n📚 Step 4: Adding Evidence (Pass 3 - simplified)...")
    frameworks_with_evidence = "frameworks_synthesized/frameworks_taylor_evidence.json"
    add_evidence(
        frameworks_synthesized,
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
```

**Step 2: Run Taylor synthesis**

Run: `cd /Users/kyraatekwana/Desktop/Claude\ Code\ Projects/transcript-synthesis-system && python3 run_taylor_synthesis.py`

Expected:
- Discovery finds 20-40 framework candidates
- Synthesis creates 5-10 frameworks
- Generates markdown and PDF
- Cost: ~$1.50-2.50
- Time: 25-35 minutes

**Step 3: Verify Taylor playbook**

Run: `ls -lh playbooks_generated/Taylor_Strategic_Playbook.*`

Expected: See .md and .pdf files

Run: `head -30 playbooks_generated/Taylor_Strategic_Playbook.md`

Expected: Different frameworks than current AI playbook (should focus on coaching, strategic thinking, not AI implementation)

**Step 4: Commit Taylor playbook**

```bash
git add src/transcript_filter.py run_taylor_synthesis.py
git add frameworks_synthesized/frameworks_taylor*.json
git add frameworks_taylor_discovered/
git add playbooks_generated/Taylor_Strategic_Playbook.*
git commit -m "feat: generate Taylor Strategic Playbook

- Process 35-45 Taylor/strategic transcripts
- Extract 5-10 coaching/strategic thinking frameworks
- Generate playbook focused on leadership and strategy
- Cost: ~$1.50-2.50"
```

---

## Task 3: Regenerate AI Transformation Playbook (All Transcripts)

**Files:**
- Output: `frameworks_synthesized/frameworks_ai.json`
- Output: `playbooks_generated/AI_Transformation_Playbook.md`
- Output: `playbooks_generated/AI_Transformation_Playbook.pdf`

**Step 1: Create AI-specific synthesis script**

Create: `run_ai_synthesis.py`

```python
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

    frameworks_synthesized = "frameworks_synthesized/frameworks_ai.json"
    synthesize_frameworks(
        frameworks_discovered,
        frameworks_synthesized,
        model='claude-opus-4-1'
    )

    # Step 4: Evidence (simplified for budget)
    print("\n📚 Step 4: Adding Evidence (Pass 3 - simplified)...")
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
```

**Step 2: Run AI synthesis**

Run: `cd /Users/kyraatekwana/Desktop/Claude\ Code\ Projects/transcript-synthesis-system && python3 run_ai_synthesis.py`

Expected:
- Discovery finds 50-100 framework candidates from all 109 transcripts
- Synthesis creates 10-15 comprehensive frameworks
- Generates markdown and PDF
- Cost: ~$3.00-4.50
- Time: 30-45 minutes

**Step 3: Verify AI playbook differs from Taylor**

Run: `head -50 playbooks_generated/AI_Transformation_Playbook.md`

Expected: More frameworks than Taylor playbook, focused on AI implementation/deployment vs coaching

Run: `diff -u playbooks_generated/Taylor_Strategic_Playbook.md playbooks_generated/AI_Transformation_Playbook.md | head -100`

Expected: Significant differences in framework content

**Step 4: Commit AI playbook**

```bash
git add run_ai_synthesis.py
git add frameworks_synthesized/frameworks_ai*.json
git add frameworks_ai_discovered/
git add playbooks_generated/AI_Transformation_Playbook.*
git commit -m "feat: regenerate AI Transformation Playbook from all transcripts

- Process all 109 transcripts (except personal)
- Extract 10-15 comprehensive AI implementation frameworks
- Include strategic + tactical + client-validated approaches
- Cost: ~$3.00-4.50"
```

---

## Task 4: Update Documentation

**Files:**
- Modify: `README.md`
- Modify: `.gitignore` (add temp directories)

**Step 1: Update README with new results**

Modify `/Users/kyraatekwana/Desktop/Claude Code Projects/transcript-synthesis-system/README.md`:

```markdown
## 📊 Results Summary

- **Transcripts Processed:** 109 files (107 work-related)
- **Framework Sets:** 2 distinct playbooks
  - Taylor Strategic: 5-10 coaching/leadership frameworks
  - AI Transformation: 10-15 implementation frameworks
- **Total Cost:** $5.00-6.65 / $50.00 budget (87-90% under budget!)
- **Processing Time:** ~55-80 minutes

## 📖 Your Playbooks

### Main Deliverables:

1. **Taylor Strategic Thinking & Coaching Playbook**
   - Source: 35-45 internal strategic/coaching transcripts
   - Frameworks: 5-10 leadership and strategic thinking frameworks
   - Markdown: `playbooks_generated/Taylor_Strategic_Playbook.md`
   - PDF: `playbooks_generated/Taylor_Strategic_Playbook.pdf`
   - Focus: Taylor's coaching methodology and strategic thinking approach

2. **AI Transformation Playbook**
   - Source: All 109 transcripts (Taylor strategic + client work)
   - Frameworks: 10-15 comprehensive AI implementation frameworks
   - Markdown: `playbooks_generated/AI_Transformation_Playbook.md`
   - PDF: `playbooks_generated/AI_Transformation_Playbook.pdf`
   - Focus: End-to-end AI deployment methodology

### Regenerate Playbooks:

```bash
# Taylor Strategic Playbook
python3 run_taylor_synthesis.py

# AI Transformation Playbook
python3 run_ai_synthesis.py
```
```

**Step 2: Update .gitignore**

Add to `.gitignore`:

```
# Temporary directories
transcripts_taylor_temp/
transcripts_ai_temp/

# Old framework files (replaced by category-specific versions)
frameworks_discovered/
frameworks_synthesized/frameworks_final.json
```

**Step 3: Test documentation**

Run: `cat README.md | grep -A 5 "Results Summary"`

Expected: See updated framework counts and costs

**Step 4: Commit documentation updates**

```bash
git add README.md .gitignore
git commit -m "docs: update README with separate playbook results

- Document Taylor vs AI playbook separation
- Update cost and framework counts
- Add regeneration instructions
- Update gitignore for temp directories"
```

---

## Task 5: Final Verification & Cleanup

**Step 1: Verify both playbooks are distinct**

Run:
```bash
cd /Users/kyraatekwana/Desktop/Claude\ Code\ Projects/transcript-synthesis-system

# Check framework counts
echo "Taylor frameworks:"
python3 -c "import json; print(len(json.load(open('frameworks_synthesized/frameworks_taylor_final.json'))))"

echo "AI frameworks:"
python3 -c "import json; print(len(json.load(open('frameworks_synthesized/frameworks_ai_final.json'))))"

# Compare first framework names
echo -e "\nTaylor first framework:"
python3 -c "import json; fw = json.load(open('frameworks_synthesized/frameworks_taylor_final.json')); print(fw[0]['framework_name'] if fw else 'None')"

echo -e "\nAI first framework:"
python3 -c "import json; fw = json.load(open('frameworks_synthesized/frameworks_ai_final.json')); print(fw[0]['framework_name'] if fw else 'None')"
```

Expected: Different counts and different framework names

**Step 2: Open both PDFs for review**

Run: `open playbooks_generated/Taylor_Strategic_Playbook.pdf playbooks_generated/AI_Transformation_Playbook.pdf`

Expected: Two distinct PDFs open with different content

**Step 3: Print final cost summary**

Run: `python3 -c "from src.cost_tracker import tracker; print(tracker.get_summary())"`

Expected: Total cost $5.00-6.65, well under $50 budget

**Step 4: Create master README**

Create summary showing what was accomplished:

Run:
```bash
cat > PLAYBOOK_SUMMARY.md << 'EOF'
# Transcript Synthesis Playbooks - Generation Summary

## Overview

Successfully generated TWO DISTINCT strategic playbooks from 109 meeting transcripts using multi-pass LLM synthesis pipeline.

## Results

### Taylor Strategic Thinking & Coaching Playbook
- **Source:** 35-45 internal transcripts (coaching sessions, strategy meetings)
- **Frameworks:** 5-10 leadership and strategic thinking frameworks
- **Focus:** Taylor's coaching methodology, strategic thinking approaches
- **Output:** `playbooks_generated/Taylor_Strategic_Playbook.pdf`

### AI Transformation Playbook
- **Source:** All 109 transcripts (strategic + client work)
- **Frameworks:** 10-15 comprehensive AI implementation frameworks
- **Focus:** End-to-end AI deployment, client validation, tactical execution
- **Output:** `playbooks_generated/AI_Transformation_Playbook.pdf`

## Cost & Performance

- **Total Cost:** $5.00-6.65 / $50.00 budget (87-90% under budget)
- **Processing Time:** 55-80 minutes
- **Models Used:** Claude Sonnet 4.5 (discovery), Claude Opus 4.1 (synthesis)

## Architecture

4-pass synthesis pipeline:
1. **Pass 1 (Discovery):** Find framework candidates using pattern detection
2. **Pass 2 (Synthesis):** Synthesize complete frameworks from distributed evidence
3. **Pass 3 (Evidence):** Add supporting quotes (simplified for budget)
4. **Pass 4 (Actionability):** Generate decision trees and checklists

## Regeneration

To regenerate playbooks:

```bash
# Taylor Strategic Playbook
python3 run_taylor_synthesis.py

# AI Transformation Playbook
python3 run_ai_synthesis.py
```

## Next Steps

1. Review both playbooks for quality and completeness
2. Scale up evidence extraction (Pass 3) with additional budget
3. Add web UI for searchable framework database
4. Create client-facing versions with branding
EOF
```

**Step 5: Final commit**

```bash
git add PLAYBOOK_SUMMARY.md
git commit -m "docs: add playbook generation summary

Complete transcript synthesis system with two distinct playbooks:
- Taylor Strategic (coaching/leadership frameworks)
- AI Transformation (implementation frameworks)

Total cost: $5-6.65, 87-90% under budget
Processing time: 55-80 minutes
Framework count: 15-25 total across both playbooks"
```

---

## Execution Summary

**Total Tasks:** 5 major tasks
**Total Steps:** 20 steps
**Estimated Time:** 55-80 minutes (mostly LLM API calls)
**Estimated Cost:** $5.00-6.65
**Risk Level:** Low (existing pipeline validated, just running twice with filtering)

**Key Deliverables:**
1. `src/transcript_filter.py` - Categorization utility
2. `run_taylor_synthesis.py` - Taylor playbook pipeline
3. `run_ai_synthesis.py` - AI playbook pipeline
4. `playbooks_generated/Taylor_Strategic_Playbook.pdf` - Distinct Taylor frameworks
5. `playbooks_generated/AI_Transformation_Playbook.pdf` - Comprehensive AI frameworks
6. Updated documentation and summary

**Dependencies:**
- All existing src/ modules working
- API keys configured in .env
- Budget available ($48.85-48.50 remaining)
- Chrome installed for PDF generation
