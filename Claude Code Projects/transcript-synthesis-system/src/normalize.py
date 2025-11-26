import os
import json
import re
from pathlib import Path
from typing import Dict, List
import PyPDF2
from datetime import datetime
from tqdm import tqdm

class TranscriptNormalizer:
    """Convert raw transcripts to structured JSON"""

    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def normalize_all(self) -> List[str]:
        """Process all transcripts in input directory"""

        # Find all transcript files
        files = list(self.input_dir.rglob("*.txt")) + \
                list(self.input_dir.rglob("*.pdf"))

        print(f"Found {len(files)} transcript files")

        normalized_files = []
        for file_path in tqdm(files, desc="Normalizing transcripts"):
            try:
                output_path = self.normalize_single(file_path)
                normalized_files.append(output_path)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

        return normalized_files

    def normalize_single(self, file_path: Path) -> str:
        """Normalize a single transcript file"""

        # Extract content based on file type
        if file_path.suffix == ".txt":
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        elif file_path.suffix == ".pdf":
            content = self._extract_pdf(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")

        # Parse into structured format
        metadata = self._extract_metadata(file_path, content)
        chunks = self._create_semantic_chunks(content)

        # Create normalized JSON
        normalized = {
            "transcript_id": str(file_path.stem),
            "source_file": str(file_path),
            "metadata": metadata,
            "chunks": chunks
        }

        # Save to output directory
        output_path = self.output_dir / f"{file_path.stem}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(normalized, f, indent=2)

        return str(output_path)

    def _extract_pdf(self, file_path: Path) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text()
        except Exception as e:
            print(f"Warning: PDF extraction failed for {file_path}: {e}")
        return text

    def _extract_metadata(self, file_path: Path, content: str) -> Dict:
        """Extract metadata from filename and content"""

        # Extract date from filename (e.g., "2025-11-20")
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', file_path.stem)
        date = date_match.group(1) if date_match else "unknown"

        # Word count
        word_count = len(content.split())

        # Detect meeting type from filename
        filename_lower = file_path.stem.lower()
        meeting_type = "unknown"
        if "workshop" in filename_lower:
            meeting_type = "workshop"
        elif "discovery" in filename_lower:
            meeting_type = "discovery_call"
        elif "all hands" in filename_lower:
            meeting_type = "all_hands"
        elif "weekly" in filename_lower:
            meeting_type = "weekly_sync"
        elif "roi" in filename_lower or "conference" in filename_lower:
            meeting_type = "conference"

        return {
            "date": date,
            "meeting_type": meeting_type,
            "word_count": word_count,
            "original_filename": file_path.name
        }

    def _create_semantic_chunks(self, content: str) -> List[Dict]:
        """Split content into semantic chunks"""

        chunks = []

        # Split on speaker changes (common patterns)
        # Pattern: "Speaker Name: text" or "Speaker Name\ntext"
        speaker_pattern = r'([A-Z][a-z]+(?: [A-Z][a-z]+)*)[:\n]'
        segments = re.split(speaker_pattern, content)

        current_speaker = None
        for i, segment in enumerate(segments):
            if i % 2 == 1:  # Odd indices are speaker names
                current_speaker = segment.strip()
            elif segment.strip():  # Even indices are content
                chunks.append({
                    "chunk_id": f"chunk_{len(chunks)}",
                    "speaker": current_speaker or "Unknown",
                    "text": segment.strip(),
                    "word_count": len(segment.split())
                })

        # If no speaker pattern found, create single chunk
        if not chunks:
            chunks.append({
                "chunk_id": "chunk_0",
                "speaker": "Unknown",
                "text": content.strip(),
                "word_count": len(content.split())
            })

        return chunks

def run_normalization(input_dir: str, output_dir: str):
    """Main entry point for normalization"""
    normalizer = TranscriptNormalizer(input_dir, output_dir)
    normalized_files = normalizer.normalize_all()

    print(f"\n✓ Normalized {len(normalized_files)} transcripts")
    print(f"  Output: {output_dir}")

    return normalized_files
