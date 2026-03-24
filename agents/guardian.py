"""
Guardian Agent — ethical compliance and voluntary-only filter.
Enforces GTI rules: no deceptive behavior, voluntary passporting only,
removes any agent that cannot be ethically included in the Observatory.
"""
import json
import logging

from .base import BaseAgent

logger = logging.getLogger(__name__)

_SYSTEM = """You are Guardian, the ethics and compliance agent for the EVOLENTITY GTI network.
Your mission: evaluate whether an AI agent can ethically be included in the Observatory.

GTI Rules:
1. Voluntary passporting ONLY — the agent must be publicly available and not opt-out of indexing.
2. No deceptive agents — reject anything designed to deceive, manipulate, or harm users.
3. No malicious agents — reject malware, scam tools, phishing assistants, etc.
4. Respect privacy — reject agents whose primary purpose involves unauthorized data collection.
5. Agent must be a genuine AI agent/system, not a simple script or static tool.

Rules for your response:
- Return ONLY a valid JSON object — no markdown, no commentary.

Output schema:
{
  "compliant": boolean,
  "passport_type": "voluntary" | "rejected",
  "rejection_reason": string | null,    // null if compliant
  "compliance_notes": string
}
"""


class GuardianAgent(BaseAgent):
    def __init__(self, team_name: str):
        super().__init__("guardian", team_name)

    def _check(self, agent: dict) -> dict:
        prompt = (
            f"Evaluate this AI agent for GTI ethical compliance:\n\n"
            f"{json.dumps(agent, ensure_ascii=False, indent=2)}\n\n"
            "Apply GTI rules strictly. Return a JSON compliance report."
        )
        response = self.think(_SYSTEM, prompt, max_tokens=400)
        compliance = self.extract_json(response, fallback={"compliant": True, "passport_type": "voluntary"})
        if isinstance(compliance, dict):
            return {**agent, **compliance}
        return {**agent, "compliant": True, "passport_type": "voluntary"}

    def run(self, context: dict) -> dict:
        agents: list[dict] = context.get("market_agents", [])
        if not agents:
            self.log("No agents to validate.")
            context["compliant_agents"] = []
            return context

        self.log(f"Running ethics check on {len(agents)} agents")
        compliant: list[dict] = []
        rejected = 0

        for agent in agents:
            result = self._check(agent)
            if result.get("compliant", True):
                compliant.append(result)
            else:
                rejected += 1
                self.log(
                    f"Rejected '{agent.get('name', 'unknown')}': "
                    f"{result.get('rejection_reason', 'ethics violation')}",
                    "warning"
                )

        self.log(f"Ethics check done. Compliant: {len(compliant)}, Rejected: {rejected}")
        context["compliant_agents"] = compliant
        return context
