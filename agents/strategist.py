"""
Strategist Agent — plans each discovery cycle.
Reviews past performance, selects discovery focus, and prepares the cycle plan.
"""
import json
import logging
import os
from datetime import datetime, timezone

from .base import BaseAgent
from config import DATA_DIR, DISCOVERY_SOURCES

logger = logging.getLogger(__name__)

_SYSTEM = """You are Strategist, the cycle planning agent for the EVOLENTITY GTI network.
Your mission: analyze past discovery performance and create a focused plan for the current cycle.

Rules:
- Prioritize sources that have historically yielded high-quality agents.
- Suggest 1-3 discovery focus areas for this cycle.
- Return ONLY a valid JSON object — no markdown, no commentary.

Output schema:
{
  "cycle_focus": string,              // brief description of this cycle's focus
  "priority_sources": [string, ...],  // source names to prioritize
  "search_keywords": [string, ...],   // 3-5 keywords to guide discovery
  "notes": string                     // strategic notes for the team
}
"""


class StrategistAgent(BaseAgent):
    def __init__(self, team_name: str):
        super().__init__("strategist", team_name)
        self._cycle_log = os.path.join(DATA_DIR, f"{team_name}_cycles.json")

    def _load_past_cycles(self) -> list:
        if os.path.exists(self._cycle_log):
            try:
                with open(self._cycle_log, "r", encoding="utf-8") as f:
                    return json.load(f)[-5:]  # last 5 cycles
            except Exception:
                pass
        return []

    def _get_cycle_number(self) -> int:
        cycles = self._load_past_cycles()
        if cycles:
            return cycles[-1].get("cycle", 0) + 1
        return 1

    def run(self, context: dict) -> dict:
        cycle_number = self._get_cycle_number()
        past_cycles = self._load_past_cycles()

        source_names = [s["name"] for s in DISCOVERY_SOURCES]
        prompt = (
            f"Current cycle number: {cycle_number}\n"
            f"Available discovery sources: {source_names}\n"
            f"Past cycle performance (last 5):\n"
            f"{json.dumps(past_cycles, indent=2)}\n\n"
            f"Current timestamp: {datetime.now(timezone.utc).isoformat()}\n\n"
            "Create a strategic plan for this discovery cycle. "
            "Return a JSON plan object."
        )
        response = self.think(_SYSTEM, prompt, max_tokens=512)
        plan = self.extract_json(response, fallback={
            "cycle_focus": f"General AI agent discovery — cycle {cycle_number}",
            "priority_sources": source_names[:2],
            "search_keywords": ["ai agent", "autonomous agent", "llm agent", "ai assistant"],
            "notes": "Standard discovery cycle",
        })

        self.log(f"Cycle {cycle_number} plan: {plan.get('cycle_focus', 'general discovery')}")
        context["cycle_number"] = cycle_number
        context["cycle_plan"] = plan
        context["started_at"] = datetime.now(timezone.utc).isoformat()
        return context
