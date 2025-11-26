import json
from pathlib import Path
from tqdm import tqdm
from .llm_client import client

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

def add_actionability(frameworks_file: str, output_file: str, model: str = "claude-sonnet-4-5"):
    """Pass 4: Make frameworks actionable"""

    with open(frameworks_file, 'r') as f:
        frameworks = json.load(f)

    print(f"\n⚡ Pass 4: Adding actionability to {len(frameworks)} frameworks...")
    print(f"   Model: {model}")

    for framework in tqdm(frameworks, desc="Actionability"):

        # Build component summary
        comp_summary = ""
        for i, comp in enumerate(framework.get("components", [])[:3], 1):
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
            framework["actionability"] = actionability

            print(f"  ✓ Added actionability for: {framework['framework_name']}")

        except json.JSONDecodeError as e:
            print(f"  ✗ JSON error for {framework['framework_name']}")
            framework["actionability"] = {
                "decision_tree": "Decision tree generation failed",
                "implementation_checklist": [],
                "decision_points": [],
                "risk_mitigation": []
            }
        except Exception as e:
            print(f"  ✗ Error: {e}")
            framework["actionability"] = {"error": str(e)}

    # Save
    with open(output_file, 'w') as f:
        json.dump(frameworks, f, indent=2)

    print(f"✓ Actionability added\n  Output: {output_file}")

    return frameworks
