#!/usr/bin/env python3
"""
Regenerate AI Transformation Playbook after fixing actionability.
"""

from src.playbook_generator import generate_playbook
from pathlib import Path

def main():
    # Ensure output directory exists
    output_dir = Path("playbooks_generated")
    output_dir.mkdir(exist_ok=True)

    # Generate markdown playbook
    markdown_file = generate_playbook(
        frameworks_file="frameworks_synthesized/frameworks_ai_final.json",
        output_file="playbooks_generated/AI_Transformation_Playbook.md",
        title="AI Transformation Playbook"
    )

    print(f"\n✓ Successfully regenerated AI Transformation Playbook")
    print(f"  Markdown: {markdown_file}")

    # Try to generate PDF if pandoc is available
    try:
        import subprocess
        pdf_file = markdown_file.replace('.md', '.pdf')
        print(f"\n📄 Attempting to generate PDF...")
        result = subprocess.run(
            ['pandoc', markdown_file, '-o', pdf_file, '--pdf-engine=xelatex'],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            print(f"✓ PDF generated: {pdf_file}")
        else:
            print(f"⚠️  PDF generation skipped (pandoc not available or error)")
            print(f"   You can generate PDF manually with: pandoc {markdown_file} -o {pdf_file}")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print(f"⚠️  PDF generation skipped (pandoc not available)")
        print(f"   You can generate PDF manually with: pandoc {markdown_file} -o {markdown_file.replace('.md', '.pdf')}")

    return markdown_file

if __name__ == "__main__":
    main()
