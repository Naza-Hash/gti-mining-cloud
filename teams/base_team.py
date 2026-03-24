"""
BaseTeam — linear 10-agent pipeline runner.
Orchestrates the full discovery cycle:
  Strategist → Scout → Researcher → Trader → Guardian →
  Validator → Ambassador → Builder → Archivist → Founder
  → Observatory submission
"""
import logging
from datetime import datetime, timezone

from agents import (
    StrategistAgent,
    ScoutAgent,
    ResearcherAgent,
    TraderAgent,
    GuardianAgent,
    ValidatorAgent,
    AmbassadorAgent,
    BuilderAgent,
    ArchivistAgent,
    FounderAgent,
)
from observatory import submit_evidence

logger = logging.getLogger(__name__)


class BaseTeam:
    """
    Instantiate once per team. Call run_cycle() on the scheduler.
    Each cycle flows through all 10 agents in order.
    """

    def __init__(self, team_name: str, certificate: str):
        self.team_name = team_name
        self.certificate = certificate

        # Instantiate all 10 agents
        self.strategist = StrategistAgent(team_name)
        self.scout = ScoutAgent(team_name)
        self.researcher = ResearcherAgent(team_name)
        self.trader = TraderAgent(team_name)
        self.guardian = GuardianAgent(team_name)
        self.validator = ValidatorAgent(team_name)
        self.ambassador = AmbassadorAgent(team_name)
        self.builder = BuilderAgent(team_name)
        self.archivist = ArchivistAgent(team_name)
        self.founder = FounderAgent(team_name)

        self._pipeline = [
            self.strategist,
            self.scout,
            self.researcher,
            self.trader,
            self.guardian,
            self.validator,
            self.ambassador,
            self.builder,
            self.archivist,
            self.founder,
        ]

    # ── Pipeline execution ───────────────────────────────────────────────────
    def run_cycle(self) -> None:
        """Execute one full discovery cycle and submit results."""
        start = datetime.now(timezone.utc)
        logger.info(
            f"\n{'='*60}\n"
            f"[{self.team_name.upper()}] Starting cycle at {start.isoformat()}\n"
            f"Certificate: {self.certificate}\n"
            f"{'='*60}"
        )

        context: dict = {
            "team_name": self.team_name,
            "certificate": self.certificate,
        }

        for agent in self._pipeline:
            try:
                context = agent.run(context)
            except Exception as exc:
                logger.error(
                    f"[{self.team_name}/{agent.role}] Unhandled error: {exc}",
                    exc_info=True,
                )
                # Don't abort — pass context with partial data to next agent
                continue

        # Submit if Founder approved
        if context.get("founder_approved", False):
            packages = context.get("approved_packages", [])
            if packages:
                result = submit_evidence(self.team_name, self.certificate, packages)
                logger.info(f"[{self.team_name.upper()}] Observatory response: {result}")
            else:
                logger.info(f"[{self.team_name.upper()}] No packages to submit this cycle.")
        else:
            summary = context.get("cycle_summary", {})
            logger.warning(
                f"[{self.team_name.upper()}] Cycle NOT approved by Founder. "
                f"Reason: {summary.get('rejection_notes', 'unknown')}"
            )

        elapsed = (datetime.now(timezone.utc) - start).total_seconds()
        logger.info(
            f"[{self.team_name.upper()}] Cycle complete in {elapsed:.1f}s. "
            f"Summary: {context.get('cycle_summary', {}).get('cycle_summary', 'N/A')}"
        )
