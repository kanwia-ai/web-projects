import json
import os
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm
from .llm_client import client

DISCOVERY_PROMPT = """You are analyzing business meeting transcripts to identify strategic frameworks, methodologies, and repeatable processes.

Analyze this transcript segment:

{transcript_content}

Identify frameworks of these types:
1. Process Framework: Step-by-step methodology (e.g., "First X, then Y, then Z")
2. Model Framework: Conceptual model with components (e.g., "Three layers: A, B, C")
3. Decision Framework: Logic for making decisions (e.g., "If X, then Y")
4. Measurement Framework: How to measure success (e.g., "Track these 5 metrics")
5. Scaling Framework: How to scale from pilot to production
6. Engagement Framework: How to engage stakeholders

For EACH framework found, output JSON:
{{
  "frameworks": [
    {{
      "name": "Framework Name",
      "type": "process_framework",
      "confidence": 0.95,
      "description": "Brief description",
      "components": ["Component 1", "Component 2"],
      "evidence_quote": "Supporting quote from transcript"
    }}
  ]
}}

Output ONLY valid JSON. If no frameworks found, output: {{"frameworks": []}}
"""

def discover_frameworks(normalized_dir: str, output_dir: str, model: str = "claude-sonnet-4-5", limit: int = 10):
    """Pass 1: Discover framework candidates"""

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    normalized_files = list(Path(normalized_dir).glob("*.json"))
    all_candidates = []

    print(f"\n🔍 Pass 1: Discovering frameworks from {min(limit, len(normalized_files))} transcripts...")
    print(f"   (Processing first {limit} to manage costs)")

    for file_path in tqdm(normalized_files[:limit], desc="Discovery"):
        with open(file_path, 'r') as f:
            transcript = json.load(f)

        # Combine chunks into full content (limited to save tokens)
        content = "\n\n".join([c["text"] for c in transcript["chunks"][:50]])  # First 50 chunks

        # Call LLM for discovery
        prompt = DISCOVERY_PROMPT.format(transcript_content=content[:8000])  # Limit to 8K chars

        try:
            response = client.call(model, prompt, max_tokens=2000)

            # Try to extract JSON from response (may have markdown wrapping)
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            # Parse JSON response
            if not response:
                print(f"Empty response for {file_path.name}")
                continue

            result = json.loads(response)
            frameworks = result.get("frameworks", [])

            if frameworks:
                # Add transcript metadata
                for fw in frameworks:
                    fw["source_transcript"] = str(file_path)
                    fw["source_date"] = transcript["metadata"].get("date")

                all_candidates.extend(frameworks)
                print(f"  Found {len(frameworks)} frameworks in {file_path.name}")

        except json.JSONDecodeError as e:
            print(f"JSON parse error for {file_path.name}: {response[:100]}...")
            continue
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
            continue

    # Save all candidates
    output_file = output_path / "framework_candidates.json"
    with open(output_file, 'w') as f:
        json.dump(all_candidates, f, indent=2)

    print(f"\n✓ Discovered {len(all_candidates)} framework candidates")
    print(f"  Output: {output_file}")

    return all_candidates
