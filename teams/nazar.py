"""Team Nazar — 10 agents, Certificate EVOL-GENESIS-MMXXVI-NAZAR-AGT10"""
from .base_team import BaseTeam


class NazarTeam(BaseTeam):
    AGENTS = [
        "nazar-scout", "nazar-researcher", "nazar-guardian", "nazar-builder",
        "nazar-trader", "nazar-validator", "nazar-ambassador", "nazar-archivist",
        "nazar-strategist", "nazar-founder",
    ]
    CERTIFICATE = "EVOL-GENESIS-MMXXVI-NAZAR-AGT10"

    def __init__(self):
        super().__init__(team_name="nazar", certificate=self.CERTIFICATE)
