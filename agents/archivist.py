"""
Archivist Agent — persists all evidence to local JSON storage.
Maintains a rolling archive per team and deduplicates by agent_url.
"""
import json
import logging
import os
from datetime import datetime, timezone

from .base import BaseAgent
from config import DATA_DIR

logger = logging.getLogger(__name__)


class ArchivistAgent(BaseAgent):
    def __init__(self, team_name: str):
        super().__init__("archivist", team_name)
        self._archive_file = os.path.join(DATA_DIR, f"{team_name}_archive.json")
        self._cycle_log_file = os.path.join(DATA_DIR, f"{team_name}_cycles.json")

    # ── Archive I/O ──────────────────────────────────────────────────────────
    def _load_archive(self) -> dict:
        if os.path.exists(self._archive_file):
            try:
                with open(self._archive_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                self.log(f"Could not load archive: {e}", "warning")
        return {"agents": {}, "total_submissions": 0}

    def _save_archive(self, archive: dict) -> None:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(self._archive_file, "w", encoding="utf-8") as f:
            json.dump(archive, f, indent=2, ensure_ascii=False)

    def _load_cycles(self) -> list:
        if os.path.exists(self._cycle_log_file):
            try:
                with open(self._cycle_log_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_cycles(self, cycles: list) -> None:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(self._cycle_log_file, "w", encoding="utf-8") as f:
            json.dump(cycles, f, indent=2, ensure_ascii=False)

    # ── Pipeline step ────────────────────────────────────────────────────────
    def run(self, context: dict) -> dict:
        packages: list[dict] = context.get("evidence_packages", [])
        cycle_number: int = context.get("cycle_number", 0)

        archive = self._load_archive()
        new_count = 0
        updated_count = 0

        for item in packages:
            key = item.get("agent_url") or item.get("agent_name", "unknown")
            if key not in archive["agents"]:
                archive["agents"][key] = item
                new_count += 1
            else:
                # Update with latest data
                archive["agents"][key] = {**archive["agents"][key], **item}
                updated_count += 1

        archive["last_updated"] = datetime.now(timezone.utc).isoformat()
        archive["total_unique_agents"] = len(archive["agents"])
        self._save_archive(archive)

        # Log cycle summary
        cycles = self._load_cycles()
        cycles.append({
            "cycle": cycle_number,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "new_agents": new_count,
            "updated_agents": updated_count,
            "total_packages": len(packages),
        })
        self._save_cycles(cycles[-100:])  # Keep last 100 cycles

        self.log(
            f"Archived. New: {new_count}, Updated: {updated_count}. "
            f"Total unique in archive: {len(archive['agents'])}"
        )
        context["archive_stats"] = {
            "new": new_count,
            "updated": updated_count,
            "total_unique": len(archive["agents"]),
        }
        return context
