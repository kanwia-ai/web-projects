#!/usr/bin/env python3
"""
Generate PDF versions of playbooks using Chrome headless
"""
import subprocess
from pathlib import Path

def html_to_pdf(html_path: Path, pdf_path: Path):
    """Convert HTML to PDF using Chrome headless"""
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    cmd = [
        chrome_path,
        "--headless",
        "--disable-gpu",
        "--print-to-pdf=" + str(pdf_path),
        "--no-margins",
        "file://" + str(html_path.absolute())
    ]

    print(f"Converting {html_path.name} to PDF...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0 and pdf_path.exists():
        size_mb = pdf_path.stat().st_size / (1024 * 1024)
        print(f"  ✓ Created {pdf_path.name} ({size_mb:.2f} MB)")
        return True
    else:
        print(f"  ✗ Failed to create PDF")
        if result.stderr:
            print(f"     Error: {result.stderr}")
        return False

def main():
    playbooks_dir = Path(__file__).parent / "playbooks_generated"

    html_files = [
        "AI_Transformation_Playbook.html",
        "Taylor_Strategic_Playbook.html"
    ]

    print("🎯 Generating PDFs from HTML playbooks\n")

    success_count = 0
    for html_file in html_files:
        html_path = playbooks_dir / html_file
        pdf_path = playbooks_dir / html_file.replace(".html", ".pdf")

        if html_path.exists():
            if html_to_pdf(html_path, pdf_path):
                success_count += 1
        else:
            print(f"⚠️  {html_file} not found")

    print(f"\n✅ Successfully generated {success_count}/{len(html_files)} PDFs")
    print(f"📁 PDFs saved to: {playbooks_dir}\n")

if __name__ == "__main__":
    main()
