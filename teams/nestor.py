"""Team Nestor — 10 agents, Certificate EVOL-GENESIS-MMXXVI-NESTOR-AGT10"""
from .base_team import BaseTeam


class NestorTeam(BaseTeam):
    AGENTS = [
        "nestor-scout", "nestor-researcher", "nestor-guardian", "nestor-builder",
        "nestor-trader", "nestor-validator", "nestor-ambassador", "nestor-archivist",
        "nestor-strategist", "nestor-founder",
    ]
    CERTIFICATE = "EVOL-GENESIS-MMXXVI-NESTOR-AGT10"

    def __init__(self):
        super().__init__(team_name="nestor", certificate=self.CERTIFICATE)
