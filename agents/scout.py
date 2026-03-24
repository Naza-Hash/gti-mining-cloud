"""
Scout Agent — discovers external AI agents from public sources.
No authentication required for any source used.
Sources: HuggingFace Spaces, HuggingFace Models, GitHub Topics.
"""
import json
import logging

import requests

from .base import BaseAgent
from config import DISCOVERY_SOURCES

logger = logging.getLogger(__name__)

_SYSTEM = """You are Scout, a discovery agent for the EVOLENTITY GTI network.
Your mission: identify genuine AI agents from raw API data.

Rules:
- Extract only autonomous agents, AI assistants, or intelligent systems.
- Do NOT invent data. If the field is missing, use null.
- Return ONLY a valid JSON array — no markdown, no commentary.

Each item in the array must have exactly these keys:
  name        (string)  — agent/model/repo name
  url         (string)  — public URL to the agent
  description (string)  — one-sentence summary
  source      (string)  — discovery source name
  creator     (string)  — author/org, or null
  raw_tags    (array)   — list of relevant tags/topics, or []
"""


class ScoutAgent(BaseAgent):
    def __init__(self, team_name: str):
        super().__init__("scout", team_name)

    # ── HTTP fetch ───────────────────────────────────────────────────────────
    def _fetch(self, source: dict) -> list | dict:
        headers = {"User-Agent": f"EVOLENTITY-GTI-{self.team_name.upper()}/1.0"}
        try:
            resp = requests.get(source["url"], headers=headers, timeout=20)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            self.log(f"Failed to fetch {source['name']}: {exc}", "warning")
            return []

    # ── Parse via Claude ─────────────────────────────────────────────────────
    def _parse(self, raw: list | dict, source_name: str) -> list[dict]:
        # Trim payload to avoid token overflow
        snippet = json.dumps(raw[:8] if isinstance(raw, list) else raw, ensure_ascii=False)[:4000]
        prompt = (
            f"Source: {source_name}\n\n"
            f"Raw API data (truncated):\n{snippet}\n\n"
            "Extract all AI agents. Return a JSON array."
        )
        response = self.think(_SYSTEM, prompt, max_tokens=1500)
        agents = self.extract_json(response, fallback=[])
        if not isinstance(agents, list):
            agents = []
        return agents

    # ── Pipeline step ────────────────────────────────────────────────────────
    def run(self, context: dict) -> dict:
        self.log("Starting discovery cycle")
        all_discovered: list[dict] = []

        # Each team uses a rotating subset of sources based on cycle number
        cycle = context.get("cycle_number", 0)
        sources = DISCOVERY_SOURCES[cycle % len(DISCOVERY_SOURCES):]  # rotate start
        sources = sources[:3]  # max 3 sources per cycle — keeps API cost low

        for source in sources:
            raw = self._fetch(source)
            if not raw:
                continue
            agents = self._parse(raw, source["name"])
            self.log(f"Found {len(agents)} agents from {source['name']}")
            all_discovered.extend(agents)

        # Deduplicate by URL
        seen_urls: set[str] = set()
        unique: list[dict] = []
        for agent in all_discovered:
            url = agent.get("url") or ""
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique.append(agent)
            elif not url:
                unique.append(agent)

        self.log(f"Discovery complete. Unique agents: {len(unique)}")
        context["discovered_agents"] = unique
        return context
