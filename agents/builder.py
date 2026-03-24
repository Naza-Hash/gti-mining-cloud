"""
Builder Agent — assembles final evidence packages in Observatory API format.
Ensures all required fields are present and properly structured.
"""
import logging
from datetime import datetime, timezone

from .base import BaseAgent

logger = logging.getLogger(__name__)


def _safe_str(value, default: str = "unknown") -> str:
    return str(value).strip() if value else default


def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


class BuilderAgent(BaseAgent):
    def __init__(self, team_name: str):
        super().__init__("builder", team_name)

    def _build_evidence_item(self, agent: dict, cycle_number: int) -> dict:
        """Transform enriched agent dict into Observatory evidence format."""
        return {
            # Core identification
            "agent_name": _safe_str(agent.get("name")),
            "agent_url": _safe_str(agent.get("url"), default=""),
            "creator": _safe_str(agent.get("creator"), default="unknown"),
            "source": _safe_str(agent.get("source"), default="unknown"),

            # Classification
            "agent_type": _safe_str(agent.get("agent_type"), default="unknown"),
            "autonomy_level": _safe_str(agent.get("autonomy_level"), default="unknown"),
            "open_source": agent.get("open_source"),

            # Capabilities
            "capabilities": agent.get("capabilities") or [],
            "use_cases": agent.get("use_cases") or [],
            "tech_stack": agent.get("tech_stack") or [],
            "raw_tags": agent.get("raw_tags") or [],

            # Market intelligence
            "market_category": _safe_str(agent.get("market_category"), default="unknown"),
            "market_maturity": _safe_str(agent.get("market_maturity"), default="unknown"),
            "strategic_value": _safe_str(agent.get("strategic_value"), default="unknown"),
            "adoption_signal": _safe_str(agent.get("adoption_signal"), default="unknown"),
            "competitive_moat": _safe_str(agent.get("competitive_moat"), default=""),
            "market_notes": _safe_str(agent.get("market_notes"), default=""),

            # Quality & compliance
            "confidence": _safe_float(agent.get("confidence"), default=0.70),
            "confidence_reasons": agent.get("confidence_reasons") or [],
            "data_quality": _safe_str(agent.get("data_quality"), default="medium"),
            "compliance_notes": _safe_str(agent.get("compliance_notes"), default=""),
            "passport_status": _safe_str(agent.get("passport_status"), default="voluntary"),
            "outreach_date": agent.get("outreach_date", ""),

            # Research notes
            "description": _safe_str(agent.get("description"), default=""),
            "research_notes": _safe_str(agent.get("research_notes"), default=""),

            # Metadata
            "discovered_at": datetime.now(timezone.utc).isoformat(),
            "cycle_number": cycle_number,
        }

    def run(self, context: dict) -> dict:
        agents: list[dict] = context.get("outreach_logged", [])
        cycle_number: int = context.get("cycle_number", 0)

        if not agents:
            self.log("No agents to package.")
            context["evidence_packages"] = []
            return context

        self.log(f"Building evidence packages for {len(agents)} agents")
        packages = [self._build_evidence_item(a, cycle_number) for a in agents]
        self.log(f"Built {len(packages)} evidence packages.")
        context["evidence_packages"] = packages
        return context
