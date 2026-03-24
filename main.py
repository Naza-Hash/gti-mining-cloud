"""
EVOLENTITY GTI Mining Cloud
============================
Main entry point — starts all 3 agent teams and the 4-hour scheduler.
Designed to run 24/7 as a Render.com background worker.

Teams deployed:
  - Oleh   (10 agents) — EVOL-GENESIS-MMXXVI-OLEH-AGT10
  - Nestor (10 agents) — EVOL-GENESIS-MMXXVI-NESTOR-AGT10
  - Nazar  (10 agents) — EVOL-GENESIS-MMXXVI-NAZAR-AGT10

Each team runs one full discovery cycle every 4 hours.
Results are submitted automatically to the EVOLENTITY Observatory.
"""
import logging
import os
import sys
from datetime import datetime, timezone

from config import ANTHROPIC_API_KEY, ISSUER_SCOPED_TOKEN, OBSERVATORY_URL, DATA_DIR
from teams import OlehTeam, NestorTeam, NazarTeam
from scheduler import build_scheduler

# ── Logging setup ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("gti.main")


def check_env() -> bool:
    """Verify required environment variables are set."""
    missing = []
    if not ANTHROPIC_API_KEY:
        missing.append("ANTHROPIC_API_KEY")
    if not ISSUER_SCOPED_TOKEN:
        missing.append("ISSUER_SCOPED_TOKEN")
    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        logger.error("Set them in the Render.com dashboard under Environment Variables.")
        return False
    return True


def print_banner() -> None:
    banner = f"""
╔══════════════════════════════════════════════════════════════╗
║         EVOLENTITY GTI MINING CLOUD — STARTING UP           ║
╠══════════════════════════════════════════════════════════════╣
║  Team Oleh   │ EVOL-GENESIS-MMXXVI-OLEH-AGT10   │ 10 agents ║
║  Team Nestor │ EVOL-GENESIS-MMXXVI-NESTOR-AGT10 │ 10 agents ║
║  Team Nazar  │ EVOL-GENESIS-MMXXVI-NAZAR-AGT10  │ 10 agents ║
╠══════════════════════════════════════════════════════════════╣
║  Total agents: 30 │ Cycle interval: 4 hours │ 24/7 cloud   ║
║  Observatory: {OBSERVATORY_URL[:40]:<40} ║
║  Started:     {datetime.now(timezone.utc).isoformat()[:19]:<40} ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def main() -> None:
    print_banner()

    # Validate environment
    if not check_env():
        sys.exit(1)

    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)
    logger.info(f"Data directory: {os.path.abspath(DATA_DIR)}")

    # Instantiate all 3 teams
    logger.info("Initializing GTI teams...")
    teams = {
        "oleh": OlehTeam(),
        "nestor": NestorTeam(),
        "nazar": NazarTeam(),
    }
    logger.info(f"Teams ready: {list(teams.keys())}")

    # Run Team Oleh immediately on startup (smoke test + first data)
    logger.info("Running initial discovery cycle for Team Oleh (startup test)...")
    try:
        teams["oleh"].run_cycle()
    except Exception as exc:
        logger.error(f"Startup cycle failed: {exc}", exc_info=True)

    # Build and start the scheduler (blocking — keeps the process alive)
    logger.info("Starting APScheduler (4-hour cycles, all teams)...")
    scheduler = build_scheduler(teams)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped. GTI Mining Cloud shutting down.")


if __name__ == "__main__":
    main()
