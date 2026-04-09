"""Orchestrator: processes completed ElevenLabs batches → GHL + callbacks."""

import json
import logging
import os
from collections import defaultdict, Counter
from datetime import datetime
from typing import Optional, List, Dict

import requests

import elevenlabs_client as el
import ghl_client_v2 as ghl          # nuovo GHL multi sub-account ($297 Unlimited)
from config import (
    PROCESSED_FILE, TIMEZONE, ENABLE_PROMPT_OPTIMIZATION,
    ELEVENLABS_API_KEY, ELEVENLABS_BASE_URL,
    TAG_TO_OPERATORE, MONITORED_AGENT_IDS,
)

log = logging.getLogger(__name__)


def _load_processed() -> dict:
    if PROCESSED_FILE.exists():
        return json.loads(PROCESSED_FILE.read_text())
    return {}


def _save_processed(data: dict):
    PROCESSED_FILE.write_text(json.dumps(data, indent=2))


# Batch filters
ALLOWED_BATCH_IDS = [x for x in os.environ.get("ALLOWED_BATCH_IDS", "").split(",") if x]
ALLOWED_BATCH_PREFIX = os.environ.get("ALLOWED_BATCH_PREFIX", "")


def _is_allowed(batch: dict) -> bool:
    if not ALLOWED_BATCH_IDS and not ALLOWED_BATCH_PREFIX:
        return True
    if batch.get("id", "") in ALLOWED_BATCH_IDS:
        return True
    if ALLOWED_BATCH_PREFIX and batch.get("name", "").lower().startswith(ALLOWED_BATCH_PREFIX.lower()):
        return True
    return False


def find_new_completed_batches() -> List[dict]:
    processed = _load_processed()
    batches = el.list_batches(limit=50)
    return [b for b in batches if b["status"] == "completed" and b["id"] not in processed and _is_allowed(b)]


# ─── ElevenLabs native analysis ───────────────────────────────────────────────

def _get_conversation_analysis(conv_id: str) -> dict:
    """Fetch the full conversation data including ElevenLabs native analysis."""
    headers = {"xi-api-key": ELEVENLABS_API_KEY}
    r = requests.get(f"{ELEVENLABS_BASE_URL}/v1/convai/conversations/{conv_id}", headers=headers, timeout=30)
    if r.status_code != 200:
        return {}
    return r.json()


def _extract_analysis(conv_data: dict) -> dict:
    """
    Extract structured analysis from ElevenLabs conversation data.
    Returns a unified dict used to update GHL.
    ElevenLabs already classifies calls natively — no Claude classifier needed.
    """
    analysis = conv_data.get("analysis", {})
    meta = conv_data.get("metadata", {})

    # Data collection fields (structured extraction during call)
    dc = analysis.get("data_collection_results", {})
    def dc_val(key):
        return (dc.get(key) or {}).get("value")

    # Evaluation criteria (pass/fail per objective)
    ec = analysis.get("evaluation_criteria_results", {})
    def ec_ok(key):
        return (ec.get(key) or {}).get("result") == "success"

    # Interest level: high / medium / low / none
    interest_level = dc_val("interest_level") or "none"

    # Appointment: explicit success check
    appointment_scheduled = ec_ok("appointment_scheduled")
    if appointment_scheduled:
        interest_level = "high"  # appointment implies high interest

    return {
        "interest_level": interest_level,
        "appointment_scheduled": appointment_scheduled,
        "email_ottenuta": dc_val("contact_person_email"),
        "nome_referente": dc_val("contact_person_name"),
        "telefono_diretto": dc_val("contact_person_phone"),
        "appointment_date_time": dc_val("appointment_date_time"),
        "transcript_summary": analysis.get("transcript_summary", ""),
        "call_successful": analysis.get("call_successful", "failure"),
        "durata": meta.get("call_duration_secs", 0),
    }


def _infer_operatore_from_contact(contact: Optional[dict]) -> Optional[str]:
    """Infer the setter/operatore from the GHL contact's tags."""
    if not contact:
        return None
    tags = contact.get("tags", [])
    for tag in tags:
        if tag in TAG_TO_OPERATORE:
            return TAG_TO_OPERATORE[tag]
    return None


# ─── Main batch processor ─────────────────────────────────────────────────────

def process_batch(batch_id: str) -> dict:
    log.info("Processing batch %s", batch_id)
    batch = el.get_batch(batch_id)
    batch_name = batch.get("name") or batch_id or "unknown-batch"
    agent_id = batch["agent_id"]
    phone_number_id = batch["phone_number_id"]

    results = []
    transcript_data = []
    callbacks_scheduled: List[dict] = []

    for recipient in batch.get("recipients", []):
        phone = recipient.get("phone_number", "")
        info = el.extract_recipient_info(recipient)
        status = recipient.get("status", "")
        conv_id = recipient.get("conversation_id")

        # ── Tag ai-chiamato per TUTTI (anche failed/no answer) ──────────────
        # Solo se la chiamata è completed — evita 429 su tutti i numeri
        if status == "completed":
            try:
                ghl.tag_called(phone, batch_name)
            except Exception as e:
                log.warning("tag_called failed %s: %s", phone, e)

        if status != "completed" or not conv_id:
            results.append({
                "azienda": info["azienda"], "phone": phone,
                "status": status, "esito": "SKIPPED",
            })
            continue

        # ── Fetch transcript ────────────────────────────────────────────────
        try:
            transcript, durata_txt = el.get_transcript_text(conv_id)
        except Exception as e:
            log.error("Transcript error %s: %s", conv_id, e)
            results.append({"azienda": info["azienda"], "phone": phone, "esito": "ERROR"})
            continue

        # ── Fetch native ElevenLabs analysis ────────────────────────────────
        try:
            conv_data = _get_conversation_analysis(conv_id)
            analysis = _extract_analysis(conv_data)
        except Exception as e:
            log.error("Analysis error %s: %s", conv_id, e)
            analysis = {"interest_level": "none", "appointment_scheduled": False,
                        "transcript_summary": "", "durata": durata_txt}

        durata = analysis.get("durata") or durata_txt
        oggi = datetime.now().strftime("%Y-%m-%d")

        # Collect for prompt optimizer
        lines = transcript.strip().split("\n")
        human_lines = sum(1 for l in lines if l.startswith("CLIENTE:") and len(l) > 15)
        transcript_data.append({
            "transcript": transcript, "durata": durata,
            "lines": lines, "human_lines": human_lines,
            "interest_level": analysis["interest_level"],
        })

        # ── Determina operatore assegnato ───────────────────────────────────
        contact_by_phone = ghl.find_by_phone(phone)
        operatore = _infer_operatore_from_contact(contact_by_phone)

        # ── Push a GHL — TUTTI i contatti con chiamata completed ─────────────
        # none → aggiorna solo campi (esito, score, data) — visibile nelle Smart List
        # low/medium/high/appointment → push completo con nota, stage, task
        ghl_result = {}
        try:
            ghl_result = ghl.push_call_result(
                company_name=info["azienda"],
                esito=analysis["interest_level"],
                riassunto=analysis.get("transcript_summary", ""),
                durata=durata,
                data_chiamata=oggi,
                batch_name=batch_name,
                conv_id=conv_id,
                email_ottenuta=analysis.get("email_ottenuta"),
                nome_referente=analysis.get("nome_referente"),
                interest_level=analysis["interest_level"],
                appointment_scheduled=analysis["appointment_scheduled"],
                transcript_summary=analysis.get("transcript_summary"),
                operatore=operatore,
                quando_richiamare=analysis.get("appointment_date_time"),
            )
        except Exception as e:
            log.error("GHL push failed %s: %s", info["azienda"], e)
            ghl_result = {"status": "error", "error": str(e)}

        result = {
            "azienda": info["azienda"],
            "phone": phone,
            "conv_id": conv_id,
            "durata": durata,
            "interest_level": analysis["interest_level"],
            "appointment_scheduled": analysis["appointment_scheduled"],
            "email_ottenuta": analysis.get("email_ottenuta"),
            "transcript_summary": analysis.get("transcript_summary", ""),
            "ghl": ghl_result,
        }
        results.append(result)

        # ── Richiami automatici (ElevenLabs outbound) ────────────────────────
        # Solo per RICHIAMO esplicito con data precisa — non per generici "richiamare"
        appt_dt = analysis.get("appointment_date_time")
        if appt_dt and analysis["appointment_scheduled"]:
            date_key = appt_dt[:10] if len(appt_dt) >= 10 else oggi
            callbacks_scheduled.append({
                "phone_number": phone,
                "client_data": recipient.get("conversation_initiation_client_data", {}),
                "note_per_agente": analysis.get("transcript_summary", ""),
                "quando": appt_dt,
                "azienda": info["azienda"],
                "agent_id": agent_id,
                "phone_number_id": phone_number_id,
                "date_key": date_key,
            })

    # ── Avvia conversazioni di richiamo ──────────────────────────────────────
    callback_batches = []
    for cb in callbacks_scheduled:
        try:
            res = el.start_outbound_conversation(
                agent_id=cb["agent_id"],
                phone_number_id=cb["phone_number_id"],
                to_number=cb["phone_number"],
                original_client_data=cb["client_data"],
                note_per_agente=cb["note_per_agente"],
            )
            log.info("Outbound richiamo avviato: %s | conv=%s", cb["azienda"], res.get("conversation_id"))
            callback_batches.append({"azienda": cb["azienda"], "conv_id": res.get("conversation_id")})
        except Exception as e:
            log.error("Outbound richiamo fallito %s: %s", cb["azienda"], e)

    # ── Prompt + TTS optimization ────────────────────────────────────────────
    prompt_fixes = []
    tts_changes = {}
    if ENABLE_PROMPT_OPTIMIZATION and transcript_data:
        try:
            import prompt_optimizer
            analysis_batch = prompt_optimizer.analyze_batch(transcript_data)
            # Passa esempi di transcript (testo grezzo) per fix chirurgici via Claude
            transcript_examples = [t.get("transcript", "") for t in transcript_data if t.get("transcript")]
            prompt_fixes = prompt_optimizer.optimize_prompt(agent_id, analysis_batch, transcript_examples)
            if prompt_fixes:
                log.info("Prompt optimized: %s", prompt_fixes)
        except Exception as e:
            log.error("Prompt optimization failed: %s", e)
        try:
            tts_changes = prompt_optimizer.optimize_tts(agent_id, results)
            if tts_changes:
                log.info("TTS tuned: %s", tts_changes)
        except Exception as e:
            log.error("TTS optimization failed: %s", e)

    # ── Salva come processato ────────────────────────────────────────────────
    processed = _load_processed()
    processed[batch_id] = {
        "name": batch_name,
        "processed_at": datetime.now().isoformat(),
        "total_recipients": len(batch.get("recipients", [])),
        "results_count": len(results),
        "callback_batches": len(callback_batches),
        "prompt_fixes": prompt_fixes,
        "tts_changes": tts_changes,
    }
    _save_processed(processed)

    summary = _build_summary(results, callback_batches, batch_name)
    summary["prompt_fixes"] = prompt_fixes
    summary["tts_changes"] = tts_changes
    log.info("Batch %s done: %s", batch_id, json.dumps(summary, ensure_ascii=False))
    return summary


def _build_summary(results: List[dict], callback_batches: list, batch_name: str) -> dict:
    interest_counts = Counter(r.get("interest_level", "none") for r in results)
    appointments = sum(1 for r in results if r.get("appointment_scheduled"))
    ghl_ok = sum(1 for r in results if r.get("ghl", {}).get("status") == "ok")
    ghl_no_match = sum(1 for r in results if r.get("ghl", {}).get("status") == "no_match")

    return {
        "batch_name": batch_name,
        "total": len(results),
        "appointments": appointments,
        "interest_levels": dict(interest_counts),
        "ghl_matched": ghl_ok,
        "ghl_no_match": ghl_no_match,
        "callbacks_scheduled": len(callback_batches),
    }


PROCESSED_CONVS_FILE = PROCESSED_FILE.parent / "processed_conversations.json"

MONITORED_AGENTS = [x.strip() for x in MONITORED_AGENT_IDS.split(",") if x.strip()]


def _load_processed_convs() -> set:
    if PROCESSED_CONVS_FILE.exists():
        return set(json.loads(PROCESSED_CONVS_FILE.read_text()))
    return set()


def _save_processed_convs(conv_ids: set):
    # Keep last 5000 to prevent file bloat
    trimmed = sorted(conv_ids)[-5000:]
    PROCESSED_CONVS_FILE.write_text(json.dumps(trimmed))


def process_single_conversations():
    """Process individual outbound conversations (not batch) for monitored agents.

    These are calls launched by smart_batch_caller.py or manual outbound calls.
    Runs the same flow as batch processing: analyze, classify, push to GHL, run optimizer.
    """
    if not MONITORED_AGENTS:
        log.info("No MONITORED_AGENT_IDS configured — skipping single conversation check")
        return []

    processed_convs = _load_processed_convs()
    all_results = []
    all_transcript_data = []

    for agent_id in MONITORED_AGENTS:
        log.info("Checking single conversations for agent %s", agent_id)

        try:
            conversations = el.list_conversations(agent_id, page_size=100, max_pages=3)
        except Exception as e:
            log.error("Failed to list conversations for %s: %s", agent_id, e)
            continue

        new_convs = [
            c for c in conversations
            if c.get("conversation_id") not in processed_convs
            and c.get("status") == "done"
        ]

        if not new_convs:
            log.info("No new single conversations for agent %s", agent_id)
            continue

        log.info("Found %d new single conversations for agent %s", len(new_convs), agent_id)

        for conv in new_convs:
            conv_id = conv.get("conversation_id", "")
            durata_meta = conv.get("call_duration_secs", 0) or 0

            # Skip very short calls (IVR hangups)
            if durata_meta < 5:
                processed_convs.add(conv_id)
                continue

            try:
                transcript, durata = el.get_transcript_text(conv_id)
            except Exception as e:
                log.error("Transcript error %s: %s", conv_id, e)
                processed_convs.add(conv_id)
                continue

            # Fetch native analysis
            try:
                conv_data = _get_conversation_analysis(conv_id)
                analysis = _extract_analysis(conv_data)
            except Exception as e:
                log.error("Analysis error %s: %s", conv_id, e)
                analysis = {"interest_level": "none", "appointment_scheduled": False,
                            "transcript_summary": "", "durata": durata}

            durata = analysis.get("durata") or durata
            oggi = datetime.now().strftime("%Y-%m-%d")

            # Get phone number from metadata
            phone_call = conv_data.get("metadata", {}).get("phone_call", {})
            phone = phone_call.get("external_number", "")

            # Get company from dynamic variables
            cd = conv_data.get("metadata", {}).get("conversation_initiation_client_data", {})
            dv = cd.get("dynamic_variables", {}) if cd else {}
            azienda = dv.get("nome_azienda", dv.get("azienda", ""))

            # Collect for optimizer
            lines = transcript.strip().split("\n")
            human_lines = sum(1 for l in lines if l.startswith("CLIENTE:") and len(l) > 15)
            all_transcript_data.append({
                "transcript": transcript, "durata": durata,
                "lines": lines, "human_lines": human_lines,
                "interest_level": analysis["interest_level"],
            })

            # Push to GHL
            if phone:
                try:
                    ghl.tag_called(phone, f"single-{agent_id[:8]}")
                except Exception as e:
                    log.warning("tag_called failed %s: %s", phone, e)

                # Inferisci operatore dal contatto
                contact_by_phone = ghl.find_by_phone(phone)
                single_operatore = _infer_operatore_from_contact(contact_by_phone)

                try:
                    ghl.push_call_result(
                        company_name=azienda,
                        esito=analysis["interest_level"],
                        riassunto=analysis.get("transcript_summary", ""),
                        durata=durata,
                        data_chiamata=oggi,
                        batch_name="single-outbound",
                        conv_id=conv_id,
                        email_ottenuta=analysis.get("email_ottenuta"),
                        nome_referente=analysis.get("nome_referente"),
                        interest_level=analysis["interest_level"],
                        appointment_scheduled=analysis["appointment_scheduled"],
                        transcript_summary=analysis.get("transcript_summary"),
                        quando_richiamare=analysis.get("appointment_date_time"),
                        operatore=single_operatore,
                    )
                except Exception as e:
                    log.error("GHL push failed for single conv %s: %s", conv_id, e)

            all_results.append({
                "conv_id": conv_id,
                "azienda": azienda,
                "phone": phone,
                "durata": durata,
                "interest_level": analysis["interest_level"],
                "appointment_scheduled": analysis["appointment_scheduled"],
            })

            processed_convs.add(conv_id)

    _save_processed_convs(processed_convs)

    # Run optimizer on all collected transcripts
    if ENABLE_PROMPT_OPTIMIZATION and all_transcript_data and MONITORED_AGENTS:
        try:
            import prompt_optimizer
            batch_analysis = prompt_optimizer.analyze_batch(all_transcript_data)
            transcript_examples = [t.get("transcript", "") for t in all_transcript_data if t.get("transcript")]
            for agent_id in MONITORED_AGENTS:
                prompt_optimizer.optimize_prompt(agent_id, batch_analysis, transcript_examples)
        except Exception as e:
            log.error("Prompt optimization failed: %s", e)

    if all_results:
        log.info("Processed %d single conversations", len(all_results))
    return all_results


def run_check():
    # 1. Process batch calls (original flow)
    new_batches = find_new_completed_batches()
    summaries = []
    if new_batches:
        log.info("Found %d new batches", len(new_batches))
        for batch in new_batches:
            try:
                summaries.append(process_batch(batch["id"]))
            except Exception as e:
                log.error("Failed to process batch %s: %s", batch["id"], e)

    # 2. Process single outbound conversations
    try:
        single_results = process_single_conversations()
        if single_results:
            summaries.append({
                "type": "single_conversations",
                "total": len(single_results),
                "appointments": sum(1 for r in single_results if r.get("appointment_scheduled")),
            })
    except Exception as e:
        log.error("Failed to process single conversations: %s", e)

    if not summaries:
        log.info("No new batches or conversations.")
    return summaries
