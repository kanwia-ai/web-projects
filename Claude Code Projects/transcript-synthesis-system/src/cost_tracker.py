import os
from datetime import datetime
from typing import Dict, List

class CostTracker:
    """Track API costs and alert when thresholds exceeded"""

    def __init__(self, budget_limit: float = 50.0, alert_threshold: float = 15.0):
        self.budget_limit = budget_limit
        self.alert_threshold = alert_threshold
        self.costs: List[Dict] = []
        self.total_cost = 0.0
        self.alerted = False

    def log_cost(self, model: str, operation: str, input_tokens: int,
                 output_tokens: int, cost: float):
        """Log a single API call cost"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "operation": operation,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost
        }
        self.costs.append(entry)
        self.total_cost += cost

        # Check thresholds
        if not self.alerted and self.total_cost >= self.alert_threshold:
            print(f"\n⚠️  COST ALERT: ${self.total_cost:.2f} / ${self.budget_limit:.2f}")
            print(f"   Threshold of ${self.alert_threshold:.2f} exceeded")
            self.alerted = True

        if self.total_cost >= self.budget_limit:
            raise Exception(f"❌ BUDGET EXCEEDED: ${self.total_cost:.2f} / ${self.budget_limit:.2f}")

    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost based on model pricing"""
        pricing = {
            "claude-sonnet-4-5": {"input": 3/1_000_000, "output": 15/1_000_000},
            "claude-opus-4-1": {"input": 15/1_000_000, "output": 75/1_000_000},
            "gpt-5.1-instant": {"input": 2/1_000_000, "output": 10/1_000_000},
        }

        if model not in pricing:
            return 0.0

        cost = (input_tokens * pricing[model]["input"] +
                output_tokens * pricing[model]["output"])
        return cost

    def get_summary(self) -> str:
        """Get cost summary"""
        summary = f"\n📊 Cost Summary\n"
        summary += f"   Total: ${self.total_cost:.2f} / ${self.budget_limit:.2f}\n"
        summary += f"   Calls: {len(self.costs)}\n"

        by_model = {}
        for entry in self.costs:
            model = entry["model"]
            by_model[model] = by_model.get(model, 0) + entry["cost"]

        for model, cost in by_model.items():
            summary += f"   {model}: ${cost:.2f}\n"

        return summary

# Global instance
tracker = CostTracker(
    budget_limit=float(os.getenv("BUDGET_LIMIT", 50.0)),
    alert_threshold=float(os.getenv("ALERT_THRESHOLD", 15.0))
)
