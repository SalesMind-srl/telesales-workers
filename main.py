"""FastAPI app with APScheduler for auto-processing ElevenLabs batches."""

import json
import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, HTTPException, Request

import pipeline
from config import CHECK_INTERVAL_MINUTES, PROCESSED_FILE

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("auto_callback")

scheduler = BackgroundScheduler()


def scheduled_check():
    log.info("--- Scheduled check started ---")
    try:
        summaries = pipeline.run_check()
        for s in summaries:
            name = s.get("batch_name") or s.get("type", "?")
            log.info("Processed: %s | %s", name, json.dumps(s, ensure_ascii=False, default=str))
    except Exception as e:
        log.error("Scheduled check failed: %s", e, exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        scheduled_check,
        "interval",
        minutes=CHECK_INTERVAL_MINUTES,
        id="batch_check",
        next_run_time=datetime.now(),
    )
    scheduler.start()
    log.info("Scheduler started (interval: %d min)", CHECK_INTERVAL_MINUTES)
    yield
    scheduler.shutdown()
    log.info("Scheduler stopped")


app = FastAPI(
    title="Telesales Auto-Callback",
    description="Processa batch ElevenLabs completati, classifica chiamate, crea callback schedulati e aggiorna GHL.",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "scheduler_running": scheduler.running,
        "next_check": str(scheduler.get_job("batch_check").next_run_time) if scheduler.get_job("batch_check") else None,
    }


@app.get("/batches")
def list_batches():
    """List recent batches with processing status."""
    processed = {}
    if PROCESSED_FILE.exists():
        processed = json.loads(PROCESSED_FILE.read_text())

    from elevenlabs_client import list_batches as el_list
    batches = el_list(limit=20)

    result = []
    for b in batches:
        entry = {
            "id": b["id"],
            "name": b["name"],
            "status": b["status"],
            "total_scheduled": b.get("total_calls_scheduled", 0),
            "total_finished": b.get("total_calls_finished", 0),
            "processed": b["id"] in processed,
        }
        if b["id"] in processed:
            entry["processed_at"] = processed[b["id"]].get("processed_at")
            entry["callback_batches"] = processed[b["id"]].get("callback_batches", 0)
        result.append(entry)

    return result


@app.post("/process/{batch_id}")
def process_batch(batch_id: str):
    """Manually process a specific batch."""
    try:
        summary = pipeline.process_batch(batch_id)
        return summary
    except Exception as e:
        log.error("Manual processing failed for %s: %s", batch_id, e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
def stats():
    """Overall statistics."""
    if not PROCESSED_FILE.exists():
        return {"total_processed": 0}

    processed = json.loads(PROCESSED_FILE.read_text())
    total_callbacks = sum(p.get("callback_batches", 0) for p in processed.values())

    return {
        "total_processed": len(processed),
        "total_callback_batches": total_callbacks,
        "batches": {k: v.get("name", k) for k, v in processed.items()},
    }


@app.post("/reset/{batch_id}")
def reset_batch(batch_id: str):
    """Remove a batch from processed list so it can be reprocessed."""
    if not PROCESSED_FILE.exists():
        raise HTTPException(status_code=404, detail="No processed batches")

    processed = json.loads(PROCESSED_FILE.read_text())
    if batch_id not in processed:
        raise HTTPException(status_code=404, detail="Batch not in processed list")

    del processed[batch_id]
    PROCESSED_FILE.write_text(json.dumps(processed, indent=2))
    return {"status": "ok", "message": f"Batch {batch_id} removed from processed list"}


@app.post("/reprocess/{batch_id}")
def reprocess_batch(batch_id: str):
    """Force reprocess a batch even if already processed (removes from cache first)."""
    if PROCESSED_FILE.exists():
        processed = json.loads(PROCESSED_FILE.read_text())
        if batch_id in processed:
            del processed[batch_id]
            PROCESSED_FILE.write_text(json.dumps(processed, indent=2))
    try:
        summary = pipeline.process_batch(batch_id)
        return summary
    except Exception as e:
        log.error("Reprocess failed for %s: %s", batch_id, e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rollback-prompt/{agent_id}")
def rollback_prompt(agent_id: str):
    """Restore the most recent prompt backup for an agent."""
    import prompt_optimizer
    success = prompt_optimizer.rollback_prompt(agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="No backup found for this agent")
    return {"status": "ok", "message": f"Prompt rolled back for agent {agent_id}"}


@app.get("/prompt-changes")
def prompt_changes():
    """View prompt optimization history."""
    from config import DATA_DIR
    changes_file = DATA_DIR / "prompt_changes.json"
    if not changes_file.exists():
        return {"changes": []}
    return json.loads(changes_file.read_text())


# ─── Instantly webhook ────────────────────────────────────────────────────────

@app.post("/instantly-webhook")
async def instantly_webhook(request: Request):
    """
    Riceve eventi da Instantly (lead replied / interested).
    Crea contatto in GHL nel sub-account del setter corretto basandosi
    sul nome della campagna (es. "filippo-marzo" → sub-account filippo).
    """
    import re
    import requests as req_lib
    import time

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON non valido")

    event_type = body.get("event_type", "")
    log.info("Instantly webhook: %s", event_type)

    # Processa solo reply e interest events
    relevant = {"reply_received", "lead_replied", "lead_interested", "lead_meeting_booked"}
    if event_type not in relevant and not any(k in event_type for k in ("reply", "interest", "meeting")):
        return {"status": "ignored", "event": event_type}

    # Estrai dati lead
    lead_data = body.get("lead", body)  # Instantly può wrappare in "lead" o flat
    email      = lead_data.get("email", "")
    first_name = lead_data.get("firstName") or lead_data.get("first_name", "")
    last_name  = lead_data.get("lastName") or lead_data.get("last_name", "")
    company    = lead_data.get("companyName") or lead_data.get("company_name") or lead_data.get("organization", "")
    campaign_name = body.get("campaign_name") or body.get("campaignName", "")

    if not email:
        return {"status": "skipped", "reason": "no email"}

    # Determina setter dal nome campagna
    from config_new_ghl import SUBACCOUNTS, GHL_TOKEN_DEFAULT, GHL_LOCATION_DEFAULT
    setter = None
    for s in SUBACCOUNTS:
        if s in campaign_name.lower():
            setter = s
            break

    if setter:
        token   = SUBACCOUNTS[setter]["token"]
        loc     = SUBACCOUNTS[setter]["loc"]
        tags    = [f"cliente-{setter}", "instantly-interessato", "fonte-email-outbound"]
    else:
        # Campagna generica → sub-account default Telesales
        token   = GHL_TOKEN_DEFAULT
        loc     = GHL_LOCATION_DEFAULT
        tags    = ["instantly-interessato", "fonte-email-outbound"]
        if campaign_name:
            safe_tag = re.sub(r"[^a-z0-9\-]", "-", campaign_name.lower().strip())[:50]
            tags.append(f"campagna-{safe_tag}")

    ghl_headers = {
        "Authorization": f"Bearer {token}",
        "Version": "2021-07-28",
        "Content-Type": "application/json",
    }
    payload = {
        "locationId": loc,
        "email":      email,
        "tags":       tags,
    }
    if first_name: payload["firstName"] = first_name
    if last_name:  payload["lastName"]  = last_name
    if company:    payload["companyName"] = company

    r = req_lib.post("https://services.leadconnectorhq.com/contacts/",
                     headers=ghl_headers, json=payload, timeout=15)
    time.sleep(0.3)

    contact_id = None
    if r.status_code in (200, 201):
        contact_id = r.json().get("contact", {}).get("id")
    elif r.status_code == 400:
        contact_id = r.json().get("meta", {}).get("contactId")

    log.info("Instantly lead → GHL [%s]: %s → contact %s",
             setter or "default", email, contact_id)

    # Aggiungi nota con il messaggio di reply
    reply_text = body.get("reply_text") or body.get("message", "")
    if contact_id and reply_text:
        note_body = f"[Instantly Reply]\nCampagna: {campaign_name}\n\n{reply_text[:1000]}"
        req_lib.post(f"https://services.leadconnectorhq.com/contacts/{contact_id}/notes/",
                     headers=ghl_headers, json={"body": note_body}, timeout=15)

    return {"status": "ok", "contact_id": contact_id, "setter": setter or "default"}
