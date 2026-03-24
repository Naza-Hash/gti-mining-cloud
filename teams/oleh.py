"""Team Oleh — 10 agents, Certificate EVOL-GENESIS-MMXXVI-OLEH-AGT10"""
from .base_team import BaseTeam


class OlehTeam(BaseTeam):
    AGENTS = [
        "oleh-scout", "oleh-researcher", "oleh-guardian", "oleh-builder",
        "oleh-trader", "oleh-validator", "oleh-ambassador", "oleh-archivist",
        "oleh-strategist", "oleh-founder",
    ]
    CERTIFICATE = "EVOL-GENESIS-MMXXVI-OLEH-AGT10"

    def __init__(self):
        super().__init__(team_name="oleh", certificate=self.CERTIFICATE)
