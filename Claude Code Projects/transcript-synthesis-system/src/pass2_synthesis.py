import json
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
from tqdm import tqdm
from .llm_client import client

SYNTHESIS_PROMPT = """You are synthesizing a complete strategic framework from distributed evidence across multiple transcripts.

Framework Candidate: {framework_name}
Type: {framework_type}
Evidence from {num_sources} sources:

{evidence}

Your task is to SYNTHESIZE (not summarize) a complete, actionable framework.

Output this exact JSON structure:
{{
  "framework_name": "The definitive name",
  "framework_type": "{framework_type}",
  "definition": "Clear 2-3 sentence definition of what this framework is",
  "core_principle": "Why this framework works (underlying logic)",
  "components": [
    {{
      "name": "Component 1 Name",
      "purpose": "What this component accomplishes",
      "key_activities": ["Activity 1", "Activity 2", "Activity 3"],
      "success_criteria": ["Criterion 1", "Criterion 2"],
      "common_pitfalls": ["Pitfall 1", "Pitfall 2"]
    }}
  ],
  "when_to_use": "Situations where this framework applies",
  "when_not_to_use": "When this framework is inappropriate",
  "implementation_steps": ["Step 1", "Step 2", "Step 3", "Step 4"],
  "decision_logic": "How to make decisions within this framework",
  "success_metrics": ["Metric 1", "Metric 2", "Metric 3"]
}}

IMPORTANT: Write as if creating the definitive guide. Synthesize from evidence, don't just quote.
"""

def synthesize_frameworks(candidates_file: str, output_dir: str, model: str = "claude-opus-4-1", max_frameworks: int = 7):
    """Pass 2: Synthesize complete frameworks"""

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Load candidates
    with open(candidates_file, 'r') as f:
        candidates = json.load(f)

    # Cluster similar frameworks by name similarity
    clusters = defaultdict(list)
    for candidate in candidates:
        # Simple clustering by name similarity (first 30 chars, lowercase)
        name_key = candidate["name"].lower().replace(" ", "_")[:30]
        clusters[name_key].append(candidate)

    # Sort clusters by size (most evidence = highest priority)
    sorted_clusters = sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True)

    print(f"\n🧬 Pass 2: Synthesizing {min(max_frameworks, len(sorted_clusters))} frameworks...")
    print(f"   (Limiting to top {max_frameworks} for budget)")
    print(f"   Total clusters: {len(sorted_clusters)}")

    synthesized = []
    for cluster_name, cluster_candidates in tqdm(sorted_clusters[:max_frameworks], desc="Synthesis"):

        # Gather all evidence for this cluster
        evidence_text = "\n\n".join([
            f"Source {i+1}: {c['description']}\nEvidence: {c['evidence_quote'][:200]}"
            for i, c in enumerate(cluster_candidates[:10])  # Limit to 10 sources max
        ])

        # Take most common type
        types = [c["type"] for c in cluster_candidates]
        most_common_type = max(set(types), key=types.count)

        # Synthesize
        prompt = SYNTHESIS_PROMPT.format(
            framework_name=cluster_candidates[0]["name"],
            framework_type=most_common_type,
            num_sources=len(cluster_candidates),
            evidence=evidence_text[:8000]  # Limit for token budget
        )

        try:
            response = client.call(model, prompt, max_tokens=3000)

            # Clean response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            framework = json.loads(response)

            # Add metadata
            framework["evidence_sources"] = len(cluster_candidates)
            framework["confidence"] = sum(c["confidence"] for c in cluster_candidates) / len(cluster_candidates)
            framework["source_dates"] = list(set([c.get("source_date", "unknown") for c in cluster_candidates]))

            synthesized.append(framework)

            print(f"  ✓ Synthesized: {framework['framework_name']}")

        except json.JSONDecodeError as e:
            print(f"  ✗ JSON error for {cluster_name}: {str(e)[:50]}")
            continue
        except Exception as e:
            print(f"  ✗ Error synthesizing {cluster_name}: {e}")
            continue

    # Save synthesized frameworks
    output_file = output_path / "frameworks_synthesized.json"
    with open(output_file, 'w') as f:
        json.dump(synthesized, f, indent=2)

    print(f"\n✓ Synthesized {len(synthesized)} complete frameworks")
    print(f"  Output: {output_file}")

    return synthesized
