import os
from anthropic import Anthropic
from openai import OpenAI
import google.generativeai as genai
from dotenv import load_dotenv
from .cost_tracker import tracker

load_dotenv()

class LLMClient:
    """Unified client for multiple LLM providers"""

    def __init__(self):
        self.anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    def call(self, model: str, prompt: str, max_tokens: int = 4000) -> str:
        """Call appropriate LLM based on model name"""

        # Estimate input tokens (rough: 4 chars per token)
        input_tokens = len(prompt) // 4

        if "claude" in model:
            response = self.anthropic.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            output = response.content[0].text
            output_tokens = response.usage.output_tokens

            # Log cost
            cost = tracker.estimate_cost(model, input_tokens, output_tokens)
            tracker.log_cost(model, "synthesis", input_tokens, output_tokens, cost)

            return output

        elif "gpt" in model:
            response = self.openai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            output = response.choices[0].message.content
            output_tokens = response.usage.completion_tokens

            # Log cost
            cost = tracker.estimate_cost(model, input_tokens, output_tokens)
            tracker.log_cost(model, "extraction", input_tokens, output_tokens, cost)

            return output

        elif "gemini" in model:
            gemini_model = genai.GenerativeModel(model)
            response = gemini_model.generate_content(prompt)
            output = response.text

            # Gemini cost tracking (approximate)
            output_tokens = len(output) // 4
            cost = tracker.estimate_cost("gemini-3-pro", input_tokens, output_tokens)
            tracker.log_cost(model, "synthesis", input_tokens, output_tokens, cost)

            return output

        else:
            raise ValueError(f"Unknown model: {model}")

# Global instance
client = LLMClient()
