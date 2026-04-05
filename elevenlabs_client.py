"""ElevenLabs Conversational AI - batch calling API wrapper."""

import time
import logging
from datetime import datetime, timezone
from typing import Optional, Tuple, List, Dict

import requests

from config import ELEVENLABS_API_KEY, ELEVENLABS_BASE_URL

log = logging.getLogger(__name__)

HEADERS = {
    "xi-api-key": ELEVENLABS_API_KEY,
    "Content-Type": "application/json",
}


def _request(method: str, path: str, **kwargs) -> dict:
    url = f"{ELEVENLABS_BASE_URL}{path}"
    for attempt in range(5):
        resp = requests.request(method, url, headers=HEADERS, timeout=30, **kwargs)
        if resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", 10 * (2 ** attempt)))
            log.warning("ElevenLabs 429 - waiting %ds", wait)
            time.sleep(wait)
            continue
        resp.raise_for_status()
        return resp.json()
    resp.raise_for_status()
    return {}


def list_batches(limit: int = 100) -> List[dict]:
    data = _request("GET", "/v1/convai/batch-calling/workspace", params={"limit": limit})
    return data.get("batch_calls", [])


def get_batch(batch_id: str) -> dict:
    return _request("GET", f"/v1/convai/batch-calling/{batch_id}")


def get_conversation(conv_id: str) -> dict:
    return _request("GET", f"/v1/convai/conversations/{conv_id}")


def get_transcript_text(conv_id: str) -> Tuple[str, int]:
    """Fetch conversation and return (transcript_text, duration_secs)."""
    conv = get_conversation(conv_id)
    transcript = conv.get("transcript", [])
    duration = conv.get("metadata", {}).get("call_duration_secs", 0)

    lines = []
    for t in transcript:
        role = "AGENTE" if t.get("role") == "agent" else "CLIENTE"
        msg = t.get("message", "")
        if msg and msg != "None":
            lines.append(f"{role}: {msg}")

    return "\n".join(lines), duration


def list_conversations(agent_id: str, page_size: int = 100, max_pages: int = 5) -> List[dict]:
    """List recent conversations for an agent (includes single outbound calls)."""
    all_convs = []
    cursor = None
    for _ in range(max_pages):
        params = {"agent_id": agent_id, "page_size": page_size}
        if cursor:
            params["cursor"] = cursor
        data = _request("GET", "/v1/convai/conversations", params=params)
        convs = data.get("conversations", [])
        all_convs.extend(convs)
        cursor = data.get("next_cursor")
        if not cursor or not convs:
            break
    return all_convs


def submit_batch(
    call_name: str,
    agent_id: str,
    phone_number_id: str,
    recipients: List[dict],
    scheduled_time_unix: Optional[int] = None,
    timezone_str: str = "Europe/Rome",
    concurrency: int = 1,
) -> dict:
    """Submit a new batch call. Returns the batch response."""
    payload = {
        "call_name": call_name,
        "agent_id": agent_id,
        "agent_phone_number_id": phone_number_id,
        "recipients": recipients,
        "target_concurrency_limit": concurrency,
        "telephony_call_config": {"ringing_timeout_secs": 60},
    }
    if scheduled_time_unix:
        payload["scheduled_time_unix"] = scheduled_time_unix
        payload["timezone"] = timezone_str

    return _request("POST", "/v1/convai/batch-calling/submit", json=payload)


def extract_recipient_info(recipient: dict) -> dict:
    """Extract company info from a batch recipient's dynamic_variables."""
    cd = recipient.get("conversation_initiation_client_data", {})
    dv = cd.get("dynamic_variables", {})
    return {
        "phone_number": recipient.get("phone_number", ""),
        "azienda": dv.get("nome_azienda", dv.get("azienda", "")),
        "categoria": dv.get("categoria", ""),
        "citta": dv.get("citta", ""),
        "nome_contatto": dv.get("nome_contatto", ""),
        "note": dv.get("note", ""),
    }


def build_callback_recipient(
    phone_number: str,
    original_client_data: dict,
    note_per_agente: str,
) -> dict:
    """Build a recipient dict for the callback batch, injecting agent notes."""
    cd = dict(original_client_data)
    dv = dict(cd.get("dynamic_variables", {}))
    dv["note"] = note_per_agente
    cd["dynamic_variables"] = dv
    return {
        "phone_number": phone_number,
        "conversation_initiation_client_data": cd,
    }


def start_outbound_conversation(
    agent_id: str,
    phone_number_id: str,
    to_number: str,
    original_client_data: dict,
    note_per_agente: str,
) -> dict:
    """Avvia una singola conversazione outbound (non batch) per un richiamo."""
    cd = dict(original_client_data)
    dv = dict(cd.get("dynamic_variables", {}))
    dv["note"] = note_per_agente
    cd["dynamic_variables"] = dv

    payload = {
        "agent_id": agent_id,
        "agent_phone_number_id": phone_number_id,
        "to_number": to_number,
        "conversation_initiation_client_data": cd,
    }
    return _request("POST", "/v1/convai/conversations/outbound", json=payload)
