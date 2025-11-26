#!/usr/bin/env python3
"""
Fix failed actionability generation for specific AI frameworks.
Re-runs Pass 4 only on frameworks with "Decision tree generation failed".
"""

import json
from pathlib import Path
from tqdm import tqdm
from src.llm_client import client

ACTIONABILITY_PROMPT = """Given this framework, create actionable implementation guidance:

Framework: {framework_name}
Type: {framework_type}
Definition: {definition}
Components: {components}

Create:
1. A decision tree (in text format) showing when and how to apply this framework
2. An implementation checklist
3. Common decision points and how to resolve them

Output JSON:
{{
  "decision_tree": "IF [condition] THEN [action] ELSE [alternative]\\nIF [condition2] THEN [action2]...",
  "implementation_checklist": ["☐ Task 1", "☐ Task 2", "☐ Task 3"],
  "decision_points": [
    {{
      "question": "Decision to make",
      "options": ["Option A", "Option B"],
      "criteria": "How to decide"
    }}
  ],
  "risk_mitigation": ["Risk 1: Mitigation approach", "Risk 2: Mitigation approach"]
}}
"""

def fix_failed_frameworks(frameworks_file: str, model: str = "claude-sonnet-4-5"):
    """Re-run actionability generation for failed frameworks"""

    # Load frameworks
    with open(frameworks_file, 'r') as f:
        frameworks = json.load(f)

    # Find failed frameworks
    failed_frameworks = []
    for idx, framework in enumerate(frameworks):
        if framework.get("actionability", {}).get("decision_tree") == "Decision tree generation failed":
            failed_frameworks.append((idx, framework))

    print(f"\n⚡ Fixing {len(failed_frameworks)} failed frameworks...")
    print(f"   Model: {model}")
    print(f"   Max tokens: 8000\n")

    fixed_count = 0
    still_failed = []

    for idx, framework in tqdm(failed_frameworks, desc="Fixing actionability"):
        print(f"\n  Processing: {framework['framework_name']}")

        # Build component summary
        comp_summary = ""
        for i, comp in enumerate(framework.get("components", [])[:5], 1):
            comp_summary += f"{i}. {comp['name']}: {comp['purpose']}\n"

        prompt = ACTIONABILITY_PROMPT.format(
            framework_name=framework["framework_name"],
            framework_type=framework["framework_type"],
            definition=framework["definition"],
            components=comp_summary
        )

        try:
            response = client.call(model, prompt, max_tokens=8000)

            # Clean response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            actionability = json.loads(response)

            # Validate the response has all required fields
            required_fields = ["decision_tree", "implementation_checklist", "decision_points", "risk_mitigation"]
            if all(field in actionability for field in required_fields):
                if actionability["decision_tree"] != "Decision tree generation failed":
                    frameworks[idx]["actionability"] = actionability
                    fixed_count += 1
                    print(f"  ✓ Fixed: {framework['framework_name']}")
                else:
                    still_failed.append(framework['framework_name'])
                    print(f"  ✗ Still failed (decision tree empty): {framework['framework_name']}")
            else:
                still_failed.append(framework['framework_name'])
                print(f"  ✗ Missing fields: {framework['framework_name']}")

        except json.JSONDecodeError as e:
            print(f"  ✗ JSON error for {framework['framework_name']}: {e}")
            still_failed.append(framework['framework_name'])
        except Exception as e:
            print(f"  ✗ Error: {e}")
            still_failed.append(framework['framework_name'])

    # Save updated frameworks
    with open(frameworks_file, 'w') as f:
        json.dump(frameworks, f, indent=2)

    print(f"\n\n{'='*60}")
    print(f"✓ Fixed {fixed_count} frameworks")
    if still_failed:
        print(f"✗ Still failed: {len(still_failed)}")
        for name in still_failed:
            print(f"  - {name}")
    else:
        print(f"✓ All frameworks fixed!")
    print(f"{'='*60}\n")

    return fixed_count, still_failed

if __name__ == "__main__":
    frameworks_file = "frameworks_synthesized/frameworks_ai_final.json"
    fixed, failed = fix_failed_frameworks(frameworks_file)

    if failed:
        print("\n⚠️  Some frameworks still need attention. Try increasing max_tokens further.")
        exit(1)
    else:
        print("\n✓ All frameworks successfully fixed!")
        exit(0)
