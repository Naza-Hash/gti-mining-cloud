import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY: str = os.environ.get("ANTHROPIC_API_KEY", "")
ISSUER_SCOPED_TOKEN: str = os.environ.get("ISSUER_SCOPED_TOKEN", "")
OBSERVATORY_URL: str = os.environ.get(
    "OBSERVATORY_URL", "https://evolentity-production-c979.up.railway.app"
)

# Model selection — haiku for routine tasks, sonnet for strategic/research
DEFAULT_MODEL = "claude-haiku-4-5-20251001"
RESEARCH_MODEL = "claude-haiku-4-5-20251001"

# Evidence quality gate
MIN_CONFIDENCE: float = 0.70

# Scheduler
CYCLE_INTERVAL_HOURS: int = 4

# Ethics
MAX_DAILY_OUTREACH_PER_TEAM: int = 10

# Data persistence directory
DATA_DIR: str = "data"

# Team definitions
TEAM_CONFIGS: dict = {
    "oleh": {
        "name": "Oleh",
        "certificate": "EVOL-GENESIS-MMXXVI-OLEH-AGT10",
        "agents": [
            "oleh-scout", "oleh-researcher", "oleh-guardian", "oleh-builder",
            "oleh-trader", "oleh-validator", "oleh-ambassador", "oleh-archivist",
            "oleh-strategist", "oleh-founder",
        ],
        "schedule_offset_minutes": 0,
    },
    "nestor": {
        "name": "Nestor",
        "certificate": "EVOL-GENESIS-MMXXVI-NESTOR-AGT10",
        "agents": [
            "nestor-scout", "nestor-researcher", "nestor-guardian", "nestor-builder",
            "nestor-trader", "nestor-validator", "nestor-ambassador", "nestor-archivist",
            "nestor-strategist", "nestor-founder",
        ],
        "schedule_offset_minutes": 80,
    },
    "nazar": {
        "name": "Nazar",
        "certificate": "EVOL-GENESIS-MMXXVI-NAZAR-AGT10",
        "agents": [
            "nazar-scout", "nazar-researcher", "nazar-guardian", "nazar-builder",
            "nazar-trader", "nazar-validator", "nazar-ambassador", "nazar-archivist",
            "nazar-strategist", "nazar-founder",
        ],
        "schedule_offset_minutes": 160,
    },
}

# Public discovery sources — no API key required
DISCOVERY_SOURCES = [
    {
        "name": "HuggingFace Spaces (agents)",
        "url": "https://huggingface.co/api/spaces?search=agent&full=true&limit=15&sort=likes",
        "type": "huggingface_spaces",
    },
    {
        "name": "HuggingFace Models (agents)",
        "url": "https://huggingface.co/api/models?search=agent&sort=downloads&limit=15",
        "type": "huggingface_models",
    },
    {
        "name": "GitHub Repos (ai-agent topic)",
        "url": "https://api.github.com/search/repositories?q=topic:ai-agent+stars:>50&sort=updated&per_page=10",
        "type": "github",
    },
    {
        "name": "GitHub Repos (autonomous-agent topic)",
        "url": "https://api.github.com/search/repositories?q=topic:autonomous-agent+stars:>30&sort=updated&per_page=10",
        "type": "github",
    },
]
