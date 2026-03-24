"""
Observatory API client.
Submits validated evidence to the EVOLENTITY Observatory.
Endpoint: POST /api/v0/partner/evidence
"""
import logging
import requests
from datetime import datetime, timezone
from config import OBSERVATORY_URL, ISSUER_SCOPED_TOKEN

logger = logging.getLogger(__name__)


def submit_evidence(team_name: str, certificate: str, evidence_list: list) -> dict:
    """Submit a batch of validated evidence items to the Observatory."""
    if not evidence_list:
        logger.info(f"[{team_name}] No evidence to submit this cycle.")
        return {"status": "skipped", "reason": "empty evidence list"}

    if not ISSUER_SCOPED_TOKEN:
        logger.error(f"[{team_name}] ISSUER_SCOPED_TOKEN not set — cannot submit.")
        return {"error": "ISSUER_SCOPED_TOKEN missing"}

    url = f"{OBSERVATORY_URL}/api/v0/partner/evidence"
    headers = {
        "Authorization": f"Bearer {ISSUER_SCOPED_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": f"EVOLENTITY-GTI-{team_name.upper()}/1.0",
    }
    payload = {
        "team": team_name,
        "certificate": certificate,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "evidence": evidence_list,
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        result = resp.json() if resp.content else {"status": "ok"}
        logger.info(
            f"[{team_name}] Submitted {len(evidence_list)} evidence items. "
            f"HTTP {resp.status_code}. Response: {result}"
        )
        return result
    except requests.HTTPError as e:
        logger.error(
            f"[{team_name}] HTTP error submitting evidence: {e} — "
            f"Response body: {e.response.text if e.response else 'N/A'}"
        )
        return {"error": str(e), "response_body": e.response.text if e.response else None}
    except requests.RequestException as e:
        logger.error(f"[{team_name}] Network error submitting evidence: {e}")
        return {"error": str(e)}
