"""
BaseAgent — shared foundation for all 10 agent roles.
Every agent has a Claude client and a standard think() / run() interface.
"""
import json
import logging
import re
from typing import Any

import anthropic
from config import ANTHROPIC_API_KEY, DEFAULT_MODEL

logger = logging.getLogger(__name__)


class BaseAgent:
    """
    All GTI agents inherit from this class.

    Subclasses must implement run(context: dict) -> dict.
    The context dict flows through the entire team pipeline; each agent
    enriches it with its own results.
    """

    def __init__(self, role: str, team_name: str, model: str = DEFAULT_MODEL):
        self.role = role
        self.team_name = team_name
        self.agent_id = f"{team_name}-{role}"
        self.model = model
        self._client: anthropic.Anthropic | None = None

    # ── Lazy client init (avoids import-time crash if key missing) ──────────
    @property
    def client(self) -> anthropic.Anthropic:
        if self._client is None:
            self._client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        return self._client

    # ── Core LLM call ────────────────────────────────────────────────────────
    def think(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 2048,
    ) -> str:
        """Send a prompt to Claude and return the text response."""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return message.content[0].text
        except anthropic.APIError as e:
            logger.error(f"[{self.agent_id}] Claude API error: {e}")
            return ""

    # ── JSON extraction helper ───────────────────────────────────────────────
    def extract_json(self, text: str, fallback: Any = None) -> Any:
        """
        Try to extract a JSON object or array from a Claude response.
        Falls back to `fallback` if parsing fails.
        """
        if not text:
            return fallback
        # First try: entire text as JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        # Second try: find first [...] or {...} block
        for pattern in (r'\[[\s\S]*\]', r'\{[\s\S]*\}'):
            match = re.search(pattern, text)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    continue
        logger.warning(f"[{self.agent_id}] Could not extract JSON from response.")
        return fallback

    # ── Pipeline entry point ─────────────────────────────────────────────────
    def run(self, context: dict) -> dict:
        """
        Process `context`, enrich it, and return the updated dict.
        Must be overridden by every subclass.
        """
        raise NotImplementedError(f"{self.__class__.__name__}.run() not implemented")

    def log(self, msg: str, level: str = "info") -> None:
        getattr(logger, level)(f"[{self.agent_id}] {msg}")
