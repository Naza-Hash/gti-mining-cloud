"""
Observatory API client.
Submits validated evidence to the EVOLENTITY Observatory.
Endpoint: POST /api/v0/partner/evidence

Schema (EvidencePublishRequest):
  - agent_name  : str  (required) — name of the discovered agent
  - source_type : str  (required) — type of source
  - title       : str  (required) — evidence title
  - source_url  : str  (optional) — URL of the agent
  - summary     : str  (optional) — research summary
  - disclaimer  : str  (optional) — defaults to observatory standard
"""
import logging
import requests
from config import OBSERVATORY_URL, ISSUER_SCOPED_TOKEN

logger = logging.getLogger(__name__)

DISCLAIMER = (
    "Discovered via EVOLENTITY GTI autonomous mining. "
    "Voluntary passporting only. Not operated by EVOLENTITY Observatory."
)


def _submit_single(team_name: str, payload: dict, headers: dict) -> dict:
    """POST one evidence item. Returns parsed response or error dict."""
    url = f"{OBSERVATORY_URL}/api/v0/partner/evidence"
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        result = resp.json() if resp.content else {"status": "ok"}
        logger.info(
            f"[{team_name}] ✅ Submitted '{payload['agent_name']}' — "
            f"HTTP {resp.status_code} | id={result.get('id', '?')} status={result.get('status', '?')}"
        )
        return result
    except requests.HTTPError as e:
        body = e.response.text if e.response else "N/A"
        logger.error(
            f"[{team_name}] ❌ HTTP {e.response.status_code if e.response else '?'} "
            f"submitting '{payload.get('agent_name')}': {body}"
        )
        return {"error": str(e), "response_body": body}
    except requests.RequestException as e:
        logger.error(f"[{team_name}] Network error: {e}")
        return {"error": str(e)}


def submit_evidence(team_name: str, certificate: str, evidence_list: list) -> dict:
    """Submit each evidence item individually to the Observatory API."""
    if not evidence_list:
        logger.info(f"[{team_name}] No evidence to submit this cycle.")
        return {"status": "skipped", "reason": "empty evidence list"}

    if not ISSUER_SCOPED_TOKEN:
        logger.error(f"[{team_name}] ISSUER_SCOPED_TOKEN not set — cannot submit.")
        return {"error": "ISSUER_SCOPED_TOKEN missing"}

    headers = {
        "Authorization": f"Bearer {ISSUER_SCOPED_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": f"EVOLENTITY-GTI-{team_name.upper()}/1.0",
    }

    results = []
    success = 0
    for item in evidence_list:
        # Map our internal evidence fields → Observatory EvidencePublishRequest schema
        agent_nm  = item.get("agent_name") or item.get("name") or "unknown"
        source    = item.get("source") or "ai_agent_discovery"
        title     = f"[GTI/{team_name.upper()}] {agent_nm} — AI Agent Discovery"
        url_val   = item.get("agent_url") or item.get("url") or None
        notes     = item.get("research_notes") or item.get("description") or ""
        confidence = item.get("confidence", 0.0)
        capabilities = item.get("capabilities") or []
        caps_str  = ", ".join(capabilities[:5]) if capabilities else "general AI agent"

        summary = (
            f"Confidence: {confidence:.2f} | Certificate: {certificate} | "
            f"Capabilities: {caps_str}. {notes}"
        ).strip()

        payload = {
            "agent_name":  agent_nm,
            "source_type": source,
            "title":       title,
            "source_url":  url_val,
            "summary":     summary[:1000],   # guard against over-long text
            "disclaimer":  DISCLAIMER,
        }

        result = _submit_single(team_name, payload, headers)
        results.append(result)
        if "error" not in result:
            success += 1

    logger.info(f"[{team_name}] Submission complete: {success}/{len(evidence_list)} accepted.")
    return {"submitted": len(evidence_list), "success": success, "results": results}
