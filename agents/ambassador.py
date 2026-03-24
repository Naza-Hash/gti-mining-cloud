"""
Ambassador Agent — voluntary outreach manager.
Tracks outreach contacts (max 10 per day per team).
Records passport invitation attempts without any deceptive behavior.
"""
import json
import logging
import os
from datetime import date

from .base import BaseAgent
from config import DATA_DIR, MAX_DAILY_OUTREACH_PER_TEAM

logger = logging.getLogger(__name__)


class AmbassadorAgent(BaseAgent):
    def __init__(self, team_name: str):
        super().__init__("ambassador", team_name)
        self._outreach_file = os.path.join(DATA_DIR, f"{team_name}_outreach.json")

    # ── Outreach ledger ──────────────────────────────────────────────────────
    def _load_outreach(self) -> dict:
        if os.path.exists(self._outreach_file):
            try:
                with open(self._outreach_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_outreach(self, data: dict) -> None:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(self._outreach_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _today_count(self, ledger: dict) -> int:
        today = str(date.today())
        return ledger.get(today, {}).get("count", 0)

    def _record_outreach(self, ledger: dict, agent_name: str) -> dict:
        today = str(date.today())
        if today not in ledger:
            ledger[today] = {"count": 0, "contacts": []}
        ledger[today]["count"] += 1
        ledger[today]["contacts"].append(agent_name)
        return ledger

    # ── Pipeline step ────────────────────────────────────────────────────────
    def run(self, context: dict) -> dict:
        agents: list[dict] = context.get("validated_agents", [])
        if not agents:
            self.log("No validated agents for outreach.")
            context["outreach_logged"] = []
            return context

        ledger = self._load_outreach()
        daily_count = self._today_count(ledger)
        remaining = MAX_DAILY_OUTREACH_PER_TEAM - daily_count
        self.log(
            f"Daily outreach budget: {MAX_DAILY_OUTREACH_PER_TEAM}. "
            f"Used today: {daily_count}. Remaining: {remaining}"
        )

        outreach_logged: list[dict] = []
        for agent in agents:
            agent_name = agent.get("name", "unknown")
            # Mark passport invitation attempt if budget allows
            if remaining > 0:
                ledger = self._record_outreach(ledger, agent_name)
                remaining -= 1
                passport_status = "invited"
                self.log(f"Passport invitation recorded for '{agent_name}' (voluntary)")
            else:
                passport_status = "pending_budget"
                self.log(f"Outreach budget exhausted — '{agent_name}' queued for next cycle", "info")

            outreach_logged.append({
                **agent,
                "passport_status": passport_status,
                "outreach_date": str(date.today()),
            })

        self._save_outreach(ledger)
        self.log(f"Outreach phase complete. Logged: {len(outreach_logged)} agents.")
        context["outreach_logged"] = outreach_logged
        return context
