"""
Validator Agent — confidence scoring and final quality gate.
Any evidence with confidence < 0.70 is rejected before reaching the Observatory.
"""
import json
import logging

from .base import BaseAgent
from config import MIN_CONFIDENCE

logger = logging.getLogger(__name__)

_SYSTEM = """You are Validator, the quality-assurance agent for the EVOLENTITY GTI network.
Your mission: assign a confidence score to each AI agent evidence item.

Confidence scoring criteria (0.0 – 1.0):
- 0.9–1.0: Fully verified, well-documented, public, clear capabilities, clear creator
- 0.7–0.89: Mostly complete, minor gaps in metadata
- 0.5–0.69: Significant gaps — incomplete description, unknown creator, unclear capabilities
- 0.0–0.49: Very low quality — minimal data, unverifiable, or suspicious

Minimum passing confidence: 0.70

Rules:
- Be strict — when in doubt, score lower.
- Return ONLY a valid JSON object — no markdown, no commentary.

Output schema:
{
  "confidence": float,         // 0.0 to 1.0
  "confidence_reasons": [string, ...],  // list of reasons for the score
  "data_quality": string       // "high" | "medium" | "low"
}
"""


class ValidatorAgent(BaseAgent):
    def __init__(self, team_name: str):
        super().__init__("validator", team_name)

    def _score(self, agent: dict) -> dict:
        prompt = (
            f"Score the data quality and confidence for this AI agent evidence:\n\n"
            f"{json.dumps(agent, ensure_ascii=False, indent=2)}\n\n"
            f"Minimum passing confidence is {MIN_CONFIDENCE}. "
            "Return a JSON object with confidence, confidence_reasons, and data_quality."
        )
        response = self.think(_SYSTEM, prompt, max_tokens=400)
        scores = self.extract_json(response, fallback=None)
        if isinstance(scores, dict):
            return {**agent, **scores}
        # Default safe score
        return {**agent, "confidence": 0.60, "confidence_reasons": ["parse error"], "data_quality": "low"}

    def run(self, context: dict) -> dict:
        agents: list[dict] = context.get("compliant_agents", [])
        if not agents:
            self.log("No agents to score.")
            context["validated_agents"] = []
            return context

        self.log(f"Scoring {len(agents)} agents (threshold: {MIN_CONFIDENCE})")
        passed: list[dict] = []
        failed = 0

        for agent in agents:
            scored = self._score(agent)
            conf = float(scored.get("confidence", 0))
            if conf >= MIN_CONFIDENCE:
                passed.append(scored)
            else:
                failed += 1
                self.log(
                    f"Rejected '{agent.get('name', 'unknown')}' — "
                    f"confidence {conf:.2f} < {MIN_CONFIDENCE}",
                    "info"
                )

        self.log(f"Validation done. Passed: {len(passed)}, Failed: {failed}")
        context["validated_agents"] = passed
        return context
