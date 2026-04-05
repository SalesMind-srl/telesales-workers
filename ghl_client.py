"""GoHighLevel CRM API wrapper."""

import difflib
import json
import logging
import re
import time
from datetime import datetime, timezone
from typing import Optional, Tuple, List, Dict

import requests

from config import (
    GHL_BASE_URL,
    GHL_CONTACTS_CACHE,
    GHL_FIELD_DATA_ULTIMO_CONTATTO,
    GHL_FIELD_DURATA_CHIAMATA,
    GHL_FIELD_ESITO_AI,
    GHL_FIELD_NOTE_CHIAMATA,
    GHL_FIELD_RECORDING_URL,
    GHL_FIELD_RIASSUNTO_AI,
    GHL_FIELD_EMAIL_REFERENTE,
    GHL_FIELD_NOME_REFERENTE,
    GHL_FIELD_BATCH_ELEVENLABS,
    GHL_FIELD_OPERATORE,
    GHL_FIELD_FONTE_LEAD,
    GHL_FIELD_CANALE,
    GHL_FIELD_SCORE_LEAD,
    GHL_LOCATION_ID,
    GHL_PIPELINE_ID,
    GHL_SLEEP,
    GHL_TOKEN,
    ESITO_TO_GHL,
    INTEREST_TO_STAGE,
    TAG_TO_OPERATORE,
    FUZZY_THRESHOLD,
)

log = logging.getLogger(__name__)

HEADERS = {
    "Authorization": f"Bearer {GHL_TOKEN}",
    "Version": "2021-07-28",
    "Content-Type": "application/json",
}


def _request(method: str, path: str, max_retries: int = 5, **kwargs) -> requests.Response:
    url = f"{GHL_BASE_URL}{path}"
    for attempt in range(max_retries):
        resp = requests.request(method, url, headers=HEADERS, timeout=30, **kwargs)
        if resp.status_code == 429:
            wait = min(5 * (2 ** attempt), 30)   # 5, 10, 20, 30 max
            log.warning("GHL 429 - waiting %ds", wait)
            time.sleep(wait)
            continue
        return resp
    return resp


def _normalize(name: str) -> str:
    if not name:
        return ""
    name = name.lower()
    name = re.sub(r"[^\w\s]", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def _sanitize_tag(name: str) -> str:
    return re.sub(r"[^a-z0-9\-]", "-", name.lower().strip()).strip("-")[:50]


def _today_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


# ─── Contact Index ────────────────────────────────────────────────────────────

class ContactIndex:
    """Lazy-loaded index of GHL contacts by company name."""

    def __init__(self):
        self._index: Dict[str, dict] = {}
        self._loaded = False

    def _load(self):
        if self._loaded:
            return
        if GHL_CONTACTS_CACHE.exists():
            age = time.time() - GHL_CONTACTS_CACHE.stat().st_mtime
            if age < 7200:
                contacts = json.loads(GHL_CONTACTS_CACHE.read_text())
                log.info("GHL cache: %d contacts (age: %ds)", len(contacts), int(age))
                self._build_index(contacts)
                return
        contacts = self._fetch_all()
        GHL_CONTACTS_CACHE.write_text(json.dumps(contacts))
        self._build_index(contacts)

    def _fetch_all(self) -> list:
        contacts = []
        params = {"locationId": GHL_LOCATION_ID, "limit": 100}
        log.info("Fetching GHL contacts...")
        while True:
            resp = _request("GET", "/contacts/", params=params)
            resp.raise_for_status()
            data = resp.json()
            batch = data.get("contacts", [])
            contacts.extend(batch)
            meta = data.get("meta", {})
            if not meta.get("nextPageUrl") or len(batch) == 0:
                break
            params = {
                "locationId": GHL_LOCATION_ID,
                "limit": 100,
                "startAfter": meta.get("startAfter"),
                "startAfterId": meta.get("startAfterId"),
            }
            time.sleep(0.5)
        log.info("Fetched %d GHL contacts", len(contacts))
        return contacts

    def _build_index(self, contacts: list):
        for c in contacts:
            company = c.get("companyName") or ""
            key = _normalize(company)
            if key:
                self._index[key] = c
        self._loaded = True
        log.info("Contact index: %d unique companies", len(self._index))

    def invalidate(self):
        self._index.clear()
        self._loaded = False
        if GHL_CONTACTS_CACHE.exists():
            GHL_CONTACTS_CACHE.unlink()

    def find(self, company_name: str) -> Tuple[Optional[dict], float]:
        self._load()
        key = _normalize(company_name)
        if not key or len(key) < 4:
            return None, 0.0
        if key in self._index:
            return self._index[key], 1.0
        matches = difflib.get_close_matches(key, list(self._index.keys()), n=1, cutoff=FUZZY_THRESHOLD)
        if matches:
            ratio = difflib.SequenceMatcher(None, key, matches[0]).ratio()
            return self._index[matches[0]], ratio
        return None, 0.0


contact_index = ContactIndex()


# ─── Core actions ─────────────────────────────────────────────────────────────

def find_by_phone(phone: str) -> Optional[dict]:
    """Find a GHL contact by phone number (uses query param — GHL doesn't support phone filter directly)."""
    phone = re.sub(r"\s+", "", phone)
    resp = _request("GET", "/contacts/", params={"locationId": GHL_LOCATION_ID, "query": phone, "limit": 3})
    if resp.status_code != 200:
        return None
    contacts = resp.json().get("contacts", [])
    # Find exact phone match among results
    for c in contacts:
        if re.sub(r"\s+", "", c.get("phone", "")) == phone:
            return c
    return contacts[0] if contacts else None


def add_note(contact_id: str, body: str) -> str:
    resp = _request("POST", f"/contacts/{contact_id}/notes", json={"body": body})
    resp.raise_for_status()
    time.sleep(GHL_SLEEP)
    return resp.json().get("note", {}).get("id", "")


def add_tag(contact_id: str, tag: str):
    _request("POST", f"/contacts/{contact_id}/tags", json={"tags": [tag]})
    time.sleep(GHL_SLEEP)


def update_contact_fields(contact_id: str, custom_fields: list):
    _request("PUT", f"/contacts/{contact_id}", json={"customFields": custom_fields})
    time.sleep(GHL_SLEEP)


def move_to_stage(contact_id: str, stage_id: str) -> bool:
    """Move a contact to a pipeline stage (creates opportunity if missing)."""
    # Check for existing opportunity first
    resp = _request("GET", "/opportunities/search", params={
        "location_id": GHL_LOCATION_ID,
        "contact_id": contact_id,
        "pipeline_id": GHL_PIPELINE_ID,
        "limit": 1,
    })
    opps = resp.json().get("opportunities", []) if resp.status_code == 200 else []

    if opps:
        opp_id = opps[0]["id"]
        r = _request("PUT", f"/opportunities/{opp_id}", json={"stageId": stage_id})
        ok = r.status_code in (200, 201)
        log.info("move_to_stage (update) %s → %s: %s", contact_id[:12], stage_id[:12], ok)
    else:
        # Create new opportunity
        r = _request("POST", "/opportunities/", json={
            "pipelineId": GHL_PIPELINE_ID,
            "locationId": GHL_LOCATION_ID,
            "name": "Cribis AI",
            "pipelineStageId": stage_id,
            "contactId": contact_id,
            "status": "open",
        })
        ok = r.status_code in (200, 201)
        log.info("move_to_stage (create) %s → %s: %s", contact_id[:12], stage_id[:12], ok)

    time.sleep(GHL_SLEEP)
    return ok


def create_task(contact_id: str, title: str, due_date: str, body: str = "") -> str:
    if len(due_date) <= 16:
        due_date = due_date + ":00+02:00" if "T" in due_date else due_date + "T09:00:00+02:00"
    payload = {"title": title[:255], "dueDate": due_date, "completed": False}
    if body:
        payload["body"] = body[:2000]
    resp = _request("POST", f"/contacts/{contact_id}/tasks", json=payload)
    resp.raise_for_status()
    time.sleep(GHL_SLEEP)
    return (resp.json().get("task") or resp.json()).get("id", "")


def tag_called(phone: str, batch_name: str):
    """Tag a contact as ai-chiamato after any call outcome."""
    contact = find_by_phone(phone)
    if not contact:
        return
    contact_id = contact["id"]
    # Single API call with both tags at once
    _request("POST", f"/contacts/{contact_id}/tags", json={
        "tags": ["ai-chiamato", f"campagna:{_sanitize_tag(batch_name)}"]
    })
    time.sleep(GHL_SLEEP)
    log.info("Tagged ai-chiamato: %s", contact.get("companyName", phone))


# ─── Main push (uses ElevenLabs native analysis) ──────────────────────────────

def push_call_result(
    company_name: str,
    esito: str,
    riassunto: str,
    durata: int,
    data_chiamata: str,
    batch_name: str,
    conv_id: Optional[str] = None,
    quando_richiamare: Optional[str] = None,
    note_per_agente: Optional[str] = None,
    email_ottenuta: Optional[str] = None,
    # nuovi parametri ElevenLabs nativi
    interest_level: Optional[str] = None,   # high/medium/low/none
    nome_referente: Optional[str] = None,
    appointment_scheduled: bool = False,
    transcript_summary: Optional[str] = None,
    operatore: Optional[str] = None,
) -> dict:
    """Push a call result to GHL — pipeline stage + custom fields + note + tag."""

    contact, ratio = contact_index.find(company_name)
    if contact is None:
        log.warning("GHL no match for: %s", company_name)
        return {"status": "no_match", "company": company_name}

    contact_id = contact["id"]
    actions = {
        "status": "ok",
        "company": company_name,
        "ghl_company": contact.get("companyName", ""),
        "match_ratio": ratio,
    }

    # ── 1. Determina esito GHL ───────────────────────────────────────────────
    if appointment_scheduled:
        ghl_esito = "Appuntamento Fissato"
        stage_id = INTEREST_TO_STAGE["appointment"]
    elif interest_level:
        ghl_esito = ESITO_TO_GHL.get(interest_level, "Non Risposto / IVR")
        stage_id = INTEREST_TO_STAGE.get(interest_level, INTEREST_TO_STAGE["none"])
    else:
        ghl_esito = ESITO_TO_GHL.get(esito, "Non Risposto / IVR")
        stage_id = INTEREST_TO_STAGE.get("none")

    # Email: usa quella raccolta o skip
    email_field_value = email_ottenuta or ""

    # Riassunto: preferisci transcript_summary di ElevenLabs, fallback su riassunto
    summary = transcript_summary or riassunto or ""

    # ── 2. Aggiorna custom fields ────────────────────────────────────────────
    fields = [
        {"id": GHL_FIELD_ESITO_AI,              "field_value": ghl_esito},
        {"id": GHL_FIELD_DATA_ULTIMO_CONTATTO,  "field_value": data_chiamata},
        {"id": GHL_FIELD_DURATA_CHIAMATA,       "field_value": durata},
        {"id": GHL_FIELD_RIASSUNTO_AI,          "field_value": summary[:2000]},
        {"id": GHL_FIELD_BATCH_ELEVENLABS,      "field_value": batch_name},
        {"id": GHL_FIELD_FONTE_LEAD,            "field_value": "AI Outbound - Cribis"},
        {"id": GHL_FIELD_CANALE,                "field_value": "AI Outbound"},
    ]
    if email_field_value:
        fields.append({"id": GHL_FIELD_EMAIL_REFERENTE, "field_value": email_field_value})
    if nome_referente:
        fields.append({"id": GHL_FIELD_NOME_REFERENTE, "field_value": nome_referente})
    if conv_id:
        fields.append({"id": GHL_FIELD_RECORDING_URL,
                       "field_value": f"https://elevenlabs.io/app/conversational-ai/conversations/{conv_id}"})
    if operatore:
        fields.append({"id": GHL_FIELD_OPERATORE, "field_value": operatore})

    # Score lead: appointment=100, high=75, medium=40, low=10, none=0
    score_map = {"appointment": 100, "high": 75, "medium": 40, "low": 10, "none": 0}
    score_key = "appointment" if appointment_scheduled else (interest_level or "none")
    fields.append({"id": GHL_FIELD_SCORE_LEAD, "field_value": score_map.get(score_key, 0)})

    update_contact_fields(contact_id, fields)
    actions["fields_updated"] = True

    # ── 3. Nota leggibile ───────────────────────────────────────────────────
    note_lines = [
        f"[AI Call] {data_chiamata} | {batch_name}",
        f"Esito: {ghl_esito} | Durata: {durata}s",
    ]
    if summary:
        note_lines.append(f"Riassunto: {summary[:500]}")
    if email_field_value:
        note_lines.append(f"Email: {email_field_value}")
    if nome_referente:
        note_lines.append(f"Referente: {nome_referente}")
    if note_per_agente:
        note_lines.append(f"Note: {note_per_agente}")
    note_id = add_note(contact_id, "\n".join(note_lines))
    actions["note_id"] = note_id

    # ── 4. Tag ──────────────────────────────────────────────────────────────
    add_tag(contact_id, "ai-chiamato")
    add_tag(contact_id, f"campagna:{_sanitize_tag(batch_name)}")
    if appointment_scheduled:
        add_tag(contact_id, "appuntamento-fissato")
    elif interest_level in ("high", "medium"):
        add_tag(contact_id, "ai-qualificato")
    actions["tags_added"] = True

    # ── 5. Sposta pipeline stage ─────────────────────────────────────────────
    if stage_id:
        moved = move_to_stage(contact_id, stage_id)
        actions["stage_moved"] = moved
        actions["stage_id"] = stage_id

    # ── 6. Task per setter se caldo/appuntamento ──────────────────────────────
    if appointment_scheduled or interest_level == "high":
        due = quando_richiamare or _today_iso()
        task_title = (
            f"APPUNTAMENTO — {company_name}" if appointment_scheduled
            else f"Richiama CALDO — {company_name}"
        )
        task_body = summary[:500] if summary else ""
        if email_field_value:
            task_body += f"\nEmail: {email_field_value}"
        task_id = create_task(contact_id, task_title, due, task_body)
        actions["task_id"] = task_id

    return actions
