"""
Scheduler — APScheduler setup for all 3 GTI teams.
Each team runs one discovery cycle every 4 hours.
Start times are staggered by 80 minutes to avoid simultaneous API load:
  - Oleh:   runs immediately, then every 4h
  - Nestor: starts 80min after boot, then every 4h
  - Nazar:  starts 160min after boot, then every 4h
"""
import logging
from datetime import datetime, timezone, timedelta

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config import CYCLE_INTERVAL_HOURS, TEAM_CONFIGS

logger = logging.getLogger(__name__)


def build_scheduler(teams: dict) -> BlockingScheduler:
    """
    Build and return a configured BlockingScheduler.
    `teams` is a dict: { "oleh": OlehTeam(), "nestor": ..., "nazar": ... }
    """
    scheduler = BlockingScheduler(timezone="UTC")
    now = datetime.now(timezone.utc)

    for team_name, team in teams.items():
        cfg = TEAM_CONFIGS[team_name]
        offset_minutes = cfg.get("schedule_offset_minutes", 0)
        start_time = now + timedelta(minutes=offset_minutes)

        scheduler.add_job(
            func=team.run_cycle,
            trigger=IntervalTrigger(
                hours=CYCLE_INTERVAL_HOURS,
                start_date=start_time,
                timezone="UTC",
            ),
            id=f"team_{team_name}",
            name=f"GTI Team {team_name.capitalize()} — 4h discovery cycle",
            replace_existing=True,
            misfire_grace_time=600,       # 10-minute grace window
            coalesce=True,                # skip missed runs, run once
            max_instances=1,              # no overlapping cycles
        )
        logger.info(
            f"Scheduled team '{team_name}' every {CYCLE_INTERVAL_HOURS}h. "
            f"First run at {start_time.isoformat()}"
        )

    return scheduler
