"""
GoHighLevel CRM API wrapper — versione multi sub-account (nuovo GHL $297 Unlimited).

Instrada le chiamate al sub-account corretto basandosi sul setter (operatore).
Usa config_new_ghl.py per token, location, pipeline, stage e field ID per setter.

Compatibile con pipeline.py: espone le stesse funzioni di ghl_client.py
"""

import difflib
import json
import logging
import re
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List, Tuple

import requests

from config_new_ghl import (
    SUBACCOUNTS,
    INTEREST_TO_STAGE_KEY,
    ESITO_TO_GHL,
    INTEREST_TO_SCORE,
    TAG_TO_SETTER,
)

log = logging.getLogger(__name__)

GHL_BASE    = "https://services.leadconnectorhq.com"
GHL_VERSION = "2021-07-28"
GHL_SLEEP   = 0.3   # secondi tra chiamate API


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _normalize(name: str) -> str:
    if not name:
        return ""
    name = name.lower()
    name = re.sub(r"[^\w\s]", " ", name)
    return re.sub(r"\s+", " ", name).strip()


def _sanitize_tag(name: str) -> str:
    if not name:
        return "unknown"
    return re.sub(r"[^a-z0-9\-]", "-", name.lower().strip()).strip("-")[:50]


def _today_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _days_from_now(days: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=days)).strftime("%Y-%m-%d")


def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Version": GHL_VERSION,
        "Content-Type": "application/json",
    }


def _request(method: str, path: str, token: str, max_retries: int = 5, **kwargs) -> requests.Response:
    url = f"{GHL_BASE}{path}"
    for attempt in range(max_retries):
        resp = requests.request(method, url, headers=_headers(token), timeout=30, **kwargs)
        if resp.status_code == 429:
            wait = min(5 * (2 ** attempt), 60)
            log.warning("GHL 429 — waiting %ds (attempt %d)", wait, attempt + 1)
            time.sleep(wait)
            continue
        return resp
    return resp


# ─── Setter inference ─────────────────────────────────────────────────────────

def _setter_from_tags(tags: list) -> Optional[str]:
    """Infer setter name from contact tags (cliente-filippo etc.)."""
    for tag in tags:
        setter = TAG_TO_SETTER.get(tag)
        if setter:
            return setter
    return None


def _setter_from_batch_name(batch_name: str) -> Optional[str]:
    """
    Infer setter from batch name conventions.
    Examples: 'filippo-cribis-50' → 'filippo', 'adriana collection' → 'adriana'
    """
    if not batch_name:
        return None
    batch_lower = batch_name.lower()
    for setter in SUBACCOUNTS:
        if setter in batch_lower:
            return setter
    return None


# ─── Per-setter contact indexes ────────────────────────────────────────────────

class SetterContactIndex:
    """Lazy-loaded contact index for a single setter's sub-account."""

    def __init__(self, setter: str):
        self.setter = setter
        self.sub = SUBACCOUNTS[setter]
        self._by_company: Dict[str, dict] = {}
        self._by_phone: Dict[str, dict] = {}
        self._loaded = False

    def _load(self):
        if self._loaded:
            return
        contacts = self._fetch_all()
        for c in contacts:
            company = c.get("companyName") or ""
            key = _normalize(company)
            if key:
                self._by_company[key] = c
            phone = re.sub(r"\s+", "", c.get("phone") or "")
            if phone:
                self._by_phone[phone] = c
        self._loaded = True
        log.info("[%s] Index: %d companies, %d phones",
                 self.setter, len(self._by_company), len(self._by_phone))

    def _fetch_all(self) -> list:
        contacts = []
        token = self.sub["token"]
        loc   = self.sub["loc"]
        params = {"locationId": loc, "limit": 100}
        log.info("[%s] Fetching contacts...", self.setter)
        while True:
            resp = _request("GET", "/contacts/", token, params=params)
            if resp.status_code != 200:
                log.error("[%s] Contacts fetch failed: %s", self.setter, resp.status_code)
                break
            data = resp.json()
            batch = data.get("contacts", [])
            contacts.extend(batch)
            meta = data.get("meta", {})
            if not meta.get("nextPageUrl") or not batch:
                break
            params = {
                "locationId": loc,
                "limit": 100,
                "startAfter": meta.get("startAfter"),
                "startAfterId": meta.get("startAfterId"),
            }
            time.sleep(0.5)
        log.info("[%s] Fetched %d contacts", self.setter, len(contacts))
        return contacts

    def invalidate(self):
        self._by_company.clear()
        self._by_phone.clear()
        self._loaded = False

    def find_by_company(self, company_name: str, fuzzy_threshold: float = 0.85) -> Tuple[Optional[dict], float]:
        self._load()
        key = _normalize(company_name)
        if not key or len(key) < 3:
            return None, 0.0
        if key in self._by_company:
            return self._by_company[key], 1.0
        matches = difflib.get_close_matches(key, list(self._by_company.keys()), n=1, cutoff=fuzzy_threshold)
        if matches:
            ratio = difflib.SequenceMatcher(None, key, matches[0]).ratio()
            return self._by_company[matches[0]], ratio
        return None, 0.0

    def find_by_phone(self, phone: str) -> Optional[dict]:
        self._load()
        phone = re.sub(r"\s+", "", phone)
        return self._by_phone.get(phone)


# Lazy init: indexes are created on first use
_setter_indexes: Dict[str, SetterContactIndex] = {}

def _get_index(setter: str) -> SetterContactIndex:
    if setter not in _setter_indexes:
        _setter_indexes[setter] = SetterContactIndex(setter)
    return _setter_indexes[setter]


# ─── Public: find contact ──────────────────────────────────────────────────────

def find_by_phone(phone: str, setter: Optional[str] = None) -> Optional[dict]:
    """
    Find contact by phone.
    If setter is provided, searches only that sub-account.
    Otherwise searches all sub-accounts (slower).
    """
    phone = re.sub(r"\s+", "", phone)
    if setter and setter in SUBACCOUNTS:
        return _get_index(setter).find_by_phone(phone)
    # Search all
    for s in SUBACCOUNTS:
        c = _get_index(s).find_by_phone(phone)
        if c:
            return c
    return None


def find_by_company(company_name: str, setter: Optional[str] = None) -> Tuple[Optional[dict], float, Optional[str]]:
    """
    Find contact by company name.
    Returns (contact, match_ratio, setter_name).
    """
    if setter and setter in SUBACCOUNTS:
        c, ratio = _get_index(setter).find_by_company(company_name)
        return c, ratio, setter if c else None
    # Search all
    best_contact, best_ratio, best_setter = None, 0.0, None
    for s in SUBACCOUNTS:
        c, ratio = _get_index(s).find_by_company(company_name)
        if ratio > best_ratio:
            best_contact, best_ratio, best_setter = c, ratio, s
    return best_contact, best_ratio, best_setter


# ─── Core actions ─────────────────────────────────────────────────────────────

def add_note(contact_id: str, body: str, token: str) -> str:
    resp = _request("POST", f"/contacts/{contact_id}/notes/", token, json={"body": body})
    if resp.status_code not in (200, 201):
        log.warning("add_note failed %s: %s", contact_id[:12], resp.status_code)
        return ""
    time.sleep(GHL_SLEEP)
    return resp.json().get("note", {}).get("id", "")


def add_tags(contact_id: str, tags: list, token: str):
    if not tags:
        return
    _request("POST", f"/contacts/{contact_id}/tags", token, json={"tags": tags})
    time.sleep(GHL_SLEEP)


def update_contact_fields(contact_id: str, custom_fields: list, token: str):
    resp = _request("PUT", f"/contacts/{contact_id}", token, json={"customFields": custom_fields})
    if resp.status_code not in (200, 201):
        log.warning("update_fields failed %s: %s", contact_id[:12], resp.status_code)
    time.sleep(GHL_SLEEP)


def move_to_stage(contact_id: str, stage_key: str, sub: dict, token: str) -> bool:
    """
    Crea o aggiorna opportunity nello stage corretto.
    stage_key: 'lead_nuovo' | 'ai_qualifica' | 'setter_chiama' | 'appuntamento' | 'closer_demo' | 'chiuso_vinto'
    """
    stage_id    = sub["stages"].get(stage_key)
    pipeline_id = sub["pipeline_id"]
    loc_id      = sub["loc"]

    if not stage_id or not pipeline_id:
        log.warning("Stage/pipeline not configured: %s", stage_key)
        return False

    # Cerca opportunity esistente
    resp = _request("GET", "/opportunities/search", token, params={
        "location_id": loc_id,
        "contact_id":  contact_id,
        "pipeline_id": pipeline_id,
        "limit": 1,
    })
    opps = resp.json().get("opportunities", []) if resp.status_code == 200 else []

    if opps:
        r = _request("PUT", f"/opportunities/{opps[0]['id']}", token,
                     json={"pipelineStageId": stage_id})
    else:
        r = _request("POST", "/opportunities/", token, json={
            "pipelineId":      pipeline_id,
            "locationId":      loc_id,
            "name":            "Telesales AI",
            "pipelineStageId": stage_id,
            "contactId":       contact_id,
            "status":          "open",
        })
    ok = r.status_code in (200, 201)
    log.info("move_to_stage %s → %s: %s", contact_id[:12], stage_key, ok)
    time.sleep(GHL_SLEEP)
    return ok


def create_task(contact_id: str, title: str, due_date: str, token: str, body: str = "") -> str:
    if len(due_date) <= 10:
        due_date = due_date + "T09:00:00+02:00"
    elif len(due_date) <= 16:
        due_date = due_date + ":00+02:00"
    payload = {"title": title[:255], "dueDate": due_date, "completed": False}
    if body:
        payload["body"] = body[:2000]
    resp = _request("POST", f"/contacts/{contact_id}/tasks", token, json=payload)
    if resp.status_code not in (200, 201):
        log.warning("create_task failed %s: %s", contact_id[:12], resp.status_code)
        return ""
    time.sleep(GHL_SLEEP)
    return (resp.json().get("task") or resp.json()).get("id", "")


def tag_called(phone: str, batch_name: str, setter: Optional[str] = None):
    """Tag contact as ai-chiamato. Called for ALL completed calls."""
    if not setter:
        setter = _setter_from_batch_name(batch_name)

    contact = find_by_phone(phone, setter)
    if not contact:
        return

    # Find which setter this contact belongs to (from tags if not passed)
    if not setter:
        setter = _setter_from_tags(contact.get("tags", []))
    if not setter or setter not in SUBACCOUNTS:
        log.warning("tag_called: no setter found for %s", phone)
        return

    token = SUBACCOUNTS[setter]["token"]
    add_tags(contact["id"], ["ai-chiamato", f"campagna:{_sanitize_tag(batch_name)}"], token)
    log.info("Tagged ai-chiamato: %s [%s]", contact.get("companyName", phone), setter)


# ─── Main push ────────────────────────────────────────────────────────────────

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
    interest_level: Optional[str] = None,
    nome_referente: Optional[str] = None,
    appointment_scheduled: bool = False,
    transcript_summary: Optional[str] = None,
    operatore: Optional[str] = None,
) -> dict:
    """
    Push call result to GHL (nuovo multi-account).
    Stessa firma di ghl_client.push_call_result — drop-in replacement.
    """
    # ── Determina setter ──────────────────────────────────────────────────────
    setter = operatore  # di solito viene già passato da pipeline.py
    if not setter:
        setter = _setter_from_batch_name(batch_name)

    # ── Trova contatto ────────────────────────────────────────────────────────
    contact, ratio, matched_setter = find_by_company(company_name, setter)
    if contact is None:
        log.warning("GHL v2 no match: %s", company_name)
        return {"status": "no_match", "company": company_name}

    # Usa il setter determinato dalla ricerca se non era noto
    if not setter and matched_setter:
        setter = matched_setter

    if not setter or setter not in SUBACCOUNTS:
        log.warning("GHL v2: setter non trovato per %s", company_name)
        return {"status": "no_setter", "company": company_name}

    sub     = SUBACCOUNTS[setter]
    token   = sub["token"]
    fields  = sub["fields"]
    contact_id = contact["id"]

    actions = {
        "status":      "ok",
        "company":     company_name,
        "ghl_company": contact.get("companyName", ""),
        "match_ratio": ratio,
        "setter":      setter,
    }

    # ── Determina esito, score, level_key ─────────────────────────────────────
    if appointment_scheduled:
        ghl_esito = "Appuntamento Fissato"
        level_key = "appointment"
    elif interest_level:
        ghl_esito = ESITO_TO_GHL.get(interest_level, "Non Risposto / IVR")
        level_key = interest_level
    else:
        ghl_esito = ESITO_TO_GHL.get(esito, "Non Risposto / IVR")
        level_key = "none"

    score   = INTEREST_TO_SCORE.get(level_key, 0)
    summary = transcript_summary or riassunto or ""
    email_val = email_ottenuta or ""

    # ── 1. Custom fields (SEMPRE) ─────────────────────────────────────────────
    def fid(name): return fields.get(name, "")

    cf = [
        {"id": fid("Esito AI Call"),          "value": ghl_esito},
        {"id": fid("Data Ultimo Contatto"),    "value": data_chiamata},
        {"id": fid("Durata Chiamata"),         "value": str(durata)},
        {"id": fid("Batch ElevenLabs"),        "value": batch_name},
        {"id": fid("Fonte Lead"),              "value": "AI Outbound - Cribis"},
        {"id": fid("Canale"),                  "value": "AI Outbound"},
        {"id": fid("Score Lead"),              "value": str(score)},
    ]
    if setter:
        cf.append({"id": fid("Operatore Assegnato"), "value": setter.capitalize()})
    if email_val:
        cf.append({"id": fid("Email Referente"),     "value": email_val})
    if nome_referente:
        cf.append({"id": fid("Nome Referente"),      "value": nome_referente})
    if conv_id:
        cf.append({"id": fid("Recording URL"),
                   "value": f"https://elevenlabs.io/app/conversational-ai/conversations/{conv_id}"})
    if summary:
        cf.append({"id": fid("Riassunto AI"), "value": summary[:2000]})
    # Rimuovi campo vuoti (id="")
    cf = [x for x in cf if x.get("id")]
    # GHL usa "id" + "value"
    update_contact_fields(contact_id, cf, token)
    actions["fields_updated"] = True

    # ── 2. Tag ────────────────────────────────────────────────────────────────
    tags_to_add = []
    if appointment_scheduled:
        tags_to_add += ["appuntamento-fissato", "ai-qualificato"]
    elif level_key in ("high", "medium"):
        tags_to_add.append("ai-qualificato")
    if tags_to_add:
        add_tags(contact_id, tags_to_add, token)
    actions["tags_added"] = tags_to_add

    # ── Early exit per "none" ─────────────────────────────────────────────────
    if level_key == "none":
        return actions

    # ── 3. Nota ───────────────────────────────────────────────────────────────
    note_lines = [
        f"[AI Call] {data_chiamata} | {batch_name}",
        f"Esito: {ghl_esito} | Durata: {durata}s",
    ]
    if summary:
        note_lines.append(f"Riassunto: {summary[:500]}")
    if email_val:
        note_lines.append(f"Email: {email_val}")
    if nome_referente:
        note_lines.append(f"Referente: {nome_referente}")
    if note_per_agente:
        note_lines.append(f"Note: {note_per_agente}")
    note_id = add_note(contact_id, "\n".join(note_lines), token)
    actions["note_id"] = note_id

    # ── 4. Stage pipeline ─────────────────────────────────────────────────────
    stage_key_map = {
        "appointment": "appuntamento",
        "high":        "setter_chiama",
        "medium":      "ai_qualifica",
        "low":         "lead_nuovo",
    }
    stage_key_ghl = stage_key_map.get(level_key)
    if stage_key_ghl:
        moved = move_to_stage(contact_id, stage_key_ghl, sub, token)
        actions["stage_moved"] = moved
        actions["stage_key"]   = stage_key_ghl

    # ── 5. Task setter ────────────────────────────────────────────────────────
    task_body = summary[:400] if summary else ""
    if email_val:
        task_body += f"\nEmail: {email_val}"

    task_id = ""
    if level_key == "appointment":
        due = quando_richiamare or _today_iso()
        task_id = create_task(contact_id, f"APPUNTAMENTO — {company_name}", due, token, task_body)
    elif level_key == "high":
        task_id = create_task(contact_id, f"Chiama CALDO — {company_name}", _today_iso(), token, task_body)
    elif level_key == "medium":
        task_id = create_task(
            contact_id,
            f"Email follow-up — {company_name}",
            _days_from_now(1),
            token,
            f"Ha fornito email in chiamata AI.\n{task_body}"
        )

    if task_id:
        actions["task_id"] = task_id

    # Invalida cache per questo setter (così al prossimo batch è fresco)
    _get_index(setter).invalidate()

    return actions
