"""Cost tracking utility for token usage and cost calculation."""

from typing import Dict, Any
from src.utils.config import config


class CostTracker:
    """Track token usage and calculate costs."""

    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.agent_costs = {}

    def add_usage(
        self,
        agent_name: str,
        input_tokens: int,
        output_tokens: int
    ):
        """Add token usage for an agent."""
        # Update totals
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens

        # Update agent-specific costs
        if agent_name not in self.agent_costs:
            self.agent_costs[agent_name] = {
                "input_tokens": 0,
                "output_tokens": 0,
                "cost": 0.0
            }

        self.agent_costs[agent_name]["input_tokens"] += input_tokens
        self.agent_costs[agent_name]["output_tokens"] += output_tokens

        # Calculate cost for this agent
        input_cost = (input_tokens / 1000) * config.GPT4_INPUT_COST_PER_1K
        output_cost = (output_tokens / 1000) * config.GPT4_OUTPUT_COST_PER_1K
        self.agent_costs[agent_name]["cost"] += input_cost + output_cost

    def get_total_cost(self) -> float:
        """Get total cost across all agents."""
        total_input_cost = (self.total_input_tokens / 1000) * config.GPT4_INPUT_COST_PER_1K
        total_output_cost = (self.total_output_tokens / 1000) * config.GPT4_OUTPUT_COST_PER_1K
        return total_input_cost + total_output_cost

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of costs."""
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_cost": self.get_total_cost(),
            "agent_costs": self.agent_costs
        }

    def reset(self):
        """Reset the cost tracker."""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.agent_costs = {}


# Singleton instance
cost_tracker = CostTracker()


def estimate_tokens(text: str) -> int:
    """Estimate token count for text (rough approximation)."""
    # Rough estimate: ~4 characters per token
    return len(text) // 4


def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    """Calculate cost for given token counts."""
    input_cost = (input_tokens / 1000) * config.GPT4_INPUT_COST_PER_1K
    output_cost = (output_tokens / 1000) * config.GPT4_OUTPUT_COST_PER_1K
    return input_cost + output_cost
