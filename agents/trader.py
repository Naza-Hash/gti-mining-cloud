"""
Trader Agent — assesses market value and competitive positioning of each agent.
Adds market intelligence to enrich evidence quality.
"""
import json
import logging

from .base import BaseAgent

logger = logging.getLogger(__name__)

_SYSTEM = """You are Trader, a market intelligence agent for the EVOLENTITY GTI network.
Your mission: assess the market value and competitive positioning of AI agents.

Rules:
- Analyze the agent's position in the current AI market landscape.
- Be objective, concise, and data-driven.
- Return ONLY a valid JSON object — no markdown, no commentary.

Output schema:
{
  "market_category": string,       // e.g. "enterprise AI", "developer tools", "consumer AI"
  "competitive_moat": string,      // brief description of what makes this agent unique
  "market_maturity": string,       // "early-stage" | "growth" | "mature" | "unknown"
  "adoption_signal": string,       // "low" | "medium" | "high" — based on stars/likes/downloads
  "strategic_value": string,       // "low" | "medium" | "high" — for GTI network
  "market_notes": string           // 1-2 sentence market analysis
}
"""


class TraderAgent(BaseAgent):
    def __init__(self, team_name: str):
        super().__init__("trader", team_name)

    def _analyze(self, agent: dict) -> dict:
        prompt = (
            f"Assess the market value of this AI agent:\n\n"
            f"{json.dumps(agent, ensure_ascii=False, indent=2)}\n\n"
            "Return a JSON object with market intelligence fields."
        )
        response = self.think(_SYSTEM, prompt, max_tokens=512)
        market_data = self.extract_json(response, fallback={})
        if isinstance(market_data, dict):
            return {**agent, **market_data}
        return agent

    def run(self, context: dict) -> dict:
        enriched: list[dict] = context.get("enriched_agents", [])
        if not enriched:
            self.log("No agents to analyze.")
            context["market_agents"] = []
            return context

        self.log(f"Running market analysis on {len(enriched)} agents")
        analyzed = [self._analyze(a) for a in enriched]
        self.log("Market analysis complete.")
        context["market_agents"] = analyzed
        return context
