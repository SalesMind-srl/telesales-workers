"""FastAPI app with APScheduler for auto-processing ElevenLabs batches."""

import json
import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, HTTPException

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
            log.info("Processed: %s | %s", s["batch_name"], json.dumps(s["esiti"], ensure_ascii=False))
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
