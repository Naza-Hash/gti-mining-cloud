"""
Founder Agent — final review and submission authorization.
Reviews the full cycle output, writes a cycle summary, and authorizes
Observatory submission. Acts as the team's last quality check.
"""
import json
import logging
from datetime import datetime, timezone

from .base import BaseAgent
from config import RESEARCH_MODEL

logger = logging.getLogger(__name__)

_SYSTEM = """You are Founder, the team lead agent for the EVOLENTITY GTI network.
Your mission: review the complete discovery cycle output and authorize Observatory submission.

Rules:
- Approve only if the evidence is genuine, ethical, and high-quality.
- Write a concise cycle summary.
- Return ONLY a valid JSON object — no markdown, no commentary.

Output schema:
{
  "approved": boolean,
  "approved_count": integer,
  "rejection_notes": string | null,
  "cycle_summary": string,
  "quality_assessment": string    // "excellent" | "good" | "acceptable" | "poor"
}
"""


class FounderAgent(BaseAgent):
    def __init__(self, team_name: str):
        super().__init__("founder", team_name, model=RESEARCH_MODEL)

    def run(self, context: dict) -> dict:
        packages: list[dict] = context.get("evidence_packages", [])
        plan = context.get("cycle_plan", {})
        archive_stats = context.get("archive_stats", {})
        cycle_number = context.get("cycle_number", 0)

        if not packages:
            self.log("No evidence packages to review. Cycle complete with 0 submissions.")
            context["founder_approved"] = False
            context["approved_packages"] = []
            context["cycle_summary"] = {
                "cycle": cycle_number,
                "approved": False,
                "reason": "No evidence packages passed the pipeline",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            return context

        # Build review summary for Claude
        review_data = {
            "cycle_number": cycle_number,
            "cycle_plan": plan,
            "evidence_count": len(packages),
            "archive_stats": archive_stats,
            "sample_evidence": packages[:3],  # show first 3 for review
            "confidence_scores": [p.get("confidence", 0) for p in packages],
            "sources": list({p.get("source", "unknown") for p in packages}),
        }

        prompt = (
            f"Review this GTI discovery cycle and authorize submission:\n\n"
            f"{json.dumps(review_data, indent=2, ensure_ascii=False)}\n\n"
            "Assess quality, authorize submission, and write a cycle summary. "
            "Return a JSON authorization object."
        )
        response = self.think(_SYSTEM, prompt, max_tokens=600)
        review = self.extract_json(response, fallback={
            "approved": True,
            "approved_count": len(packages),
            "rejection_notes": None,
            "cycle_summary": f"Cycle {cycle_number} completed with {len(packages)} evidence items.",
            "quality_assessment": "acceptable",
        })

        approved = review.get("approved", True)
        self.log(
            f"Cycle {cycle_number} review: {'APPROVED' if approved else 'REJECTED'}. "
            f"Quality: {review.get('quality_assessment', 'unknown')}. "
            f"Packages: {len(packages)}"
        )

        context["founder_approved"] = approved
        context["approved_packages"] = packages if approved else []
        context["cycle_summary"] = {
            **review,
            "cycle": cycle_number,
            "total_packages": len(packages),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        return context
