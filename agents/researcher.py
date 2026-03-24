"""
Researcher Agent — performs deep analysis on each discovered agent.
Enriches raw discovery data with capabilities, use-cases, tech stack,
and a structured profile using Claude.
"""
import json
import logging

from .base import BaseAgent
from config import RESEARCH_MODEL

logger = logging.getLogger(__name__)

_SYSTEM = """You are Researcher, a deep-analysis agent for the EVOLENTITY GTI network.
Your mission: enrich a discovered AI agent's profile with detailed, factual analysis.

Rules:
- Base your analysis ONLY on the provided data — do not fabricate information.
- Be concise and precise.
- Return ONLY a valid JSON object — no markdown, no commentary.

Output schema:
{
  "name": string,
  "url": string,
  "description": string,
  "creator": string | null,
  "source": string,
  "raw_tags": [],
  "capabilities": [string, ...],
  "use_cases": [string, ...],
  "tech_stack": [string, ...],
  "agent_type": string,        // e.g. "conversational", "task-automation", "coding", "research", "multi-modal"
  "autonomy_level": string,    // "low" | "medium" | "high" | "unknown"
  "open_source": boolean | null,
  "research_notes": string
}
"""


class ResearcherAgent(BaseAgent):
    def __init__(self, team_name: str):
        super().__init__("researcher", team_name, model=RESEARCH_MODEL)

    def _enrich(self, agent: dict) -> dict:
        prompt = (
            f"Enrich this AI agent profile:\n\n"
            f"{json.dumps(agent, ensure_ascii=False, indent=2)}\n\n"
            "Fill in capabilities, use_cases, tech_stack, agent_type, autonomy_level, "
            "open_source, and research_notes based on the available information. "
            "Return a complete JSON object."
        )
        response = self.think(_SYSTEM, prompt, max_tokens=1024)
        enriched = self.extract_json(response, fallback=None)
        if isinstance(enriched, dict) and enriched:
            # Merge: keep original fields, overlay enriched ones
            return {**agent, **enriched}
        return agent

    def run(self, context: dict) -> dict:
        discovered: list[dict] = context.get("discovered_agents", [])
        if not discovered:
            self.log("No agents to research.")
            context["enriched_agents"] = []
            return context

        self.log(f"Researching {len(discovered)} agents")
        enriched: list[dict] = []

        for agent in discovered:
            profile = self._enrich(agent)
            enriched.append(profile)

        self.log(f"Research complete. Enriched {len(enriched)} profiles.")
        context["enriched_agents"] = enriched
        return context
