"""Analyze batch call transcripts and report issues — MONITOR ONLY, no auto-editing.

Detects problematic patterns in transcripts and LOGS them as alerts.
Does NOT modify the agent prompt or TTS settings.
Prompt and TTS are managed manually for quality control.

What it does:
- Analyzes transcripts for known problems (IVR loops, audio issues, talking over, etc.)
- Logs alerts with frequencies and examples
- Saves reports to data/optimization_reports/
- Provides data for manual optimization decisions

What it does NOT do:
- Modify the agent prompt
- Modify TTS settings (stability, speed, etc.)
- Modify turn settings (timeout, eagerness, etc.)
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from config import DATA_DIR

log = logging.getLogger(__name__)

REPORTS_DIR = DATA_DIR / "optimization_reports"
REPORTS_DIR.mkdir(exist_ok=True)
CHANGES_FILE = DATA_DIR / "prompt_changes.json"

ACTIVATION_THRESHOLD = 0.10  # Pattern must appear in >= 10% of calls


# ---------------------------------------------------------------------------
# Pattern detectors — each returns True if the problem is present
# ---------------------------------------------------------------------------

def detect_ivr_loop(transcript: str, durata: int, human_lines: int) -> bool:
    """Agent stuck on IVR for > 30s without reaching a human."""
    ivr_kw = ["premere", "digitare", "digitate", "premete", "attendere in linea",
              "operatore disponibile", "we apologize", "rimanete in attesa"]
    ivr_count = sum(1 for kw in ivr_kw if kw in transcript.lower())
    return ivr_count >= 2 and durata > 30 and human_lines <= 1


def detect_audio_issues(transcript: str) -> bool:
    """Agent keeps saying 'pronto? mi senti?' more than 3 times."""
    t = transcript.lower()
    pronto_count = len(re.findall(r"pronto\??\s", t))
    mi_senti_count = len(re.findall(r"mi sent[ie]", t))
    return (pronto_count + mi_senti_count) >= 4


def detect_talking_over(lines: List[str]) -> bool:
    """Agent sends 3+ consecutive messages without a client response."""
    consecutive_agent = 0
    max_consecutive = 0
    for line in lines:
        if line.startswith("AGENTE:"):
            consecutive_agent += 1
            max_consecutive = max(max_consecutive, consecutive_agent)
        elif line.startswith("CLIENTE:") and len(line) > 15:
            consecutive_agent = 0
    return max_consecutive >= 4


def detect_long_gatekeeper_pitch(lines: List[str]) -> bool:
    """Agent gives a > 100 char pitch to a gatekeeper asking 'per che cosa?'."""
    gatekeeper_triggers = ["per che cosa", "a che proposito", "chi la desidera",
                           "per quale motivo", "di che si tratta"]
    for i, line in enumerate(lines):
        if line.startswith("CLIENTE:"):
            text = line[8:].strip().lower()
            if any(t in text for t in gatekeeper_triggers):
                for j in range(i + 1, min(i + 3, len(lines))):
                    if lines[j].startswith("AGENTE:"):
                        agent_text = lines[j][7:].strip()
                        if len(agent_text) > 120:
                            return True
    return False


def detect_office_closed_stay(transcript: str, durata: int) -> bool:
    """Agent stays on the line after hearing 'uffici chiusi/orari' for > 20s."""
    t = transcript.lower()
    closed_kw = ["uffici sono chiusi", "orari sono", "uffici chiusi",
                 "i nostri uffici sono aperti", "uffici attualmente sono chiusi"]
    has_closed = any(kw in t for kw in closed_kw)
    return has_closed and durata > 20


def detect_wait_loop(transcript: str, durata: int) -> bool:
    """Agent stuck in a hold/wait loop saying 'rimango in attesa' repeatedly."""
    t = transcript.lower()
    wait_phrases = len(re.findall(r"(rimango in attesa|sono ancora in attesa|aspetto|continuo ad aspettare)", t))
    return wait_phrases >= 4 and durata > 60


def detect_capisco_usage(transcript: str) -> bool:
    """Agent says 'capisco' which is a banned word."""
    agent_lines = re.findall(r"AGENTE: (.+)", transcript)
    return any("capisco" in line.lower() for line in agent_lines)


def detect_audio_tags(transcript: str) -> bool:
    """Agent says audio tags out loud like [slow], [happy], [sad]."""
    return bool(re.search(r"\[(slow|fast|happy|sad|calm|clear|friendly|laugh|understanding|attentive|waiting)\]", transcript.lower()))


def detect_long_monologue(lines: List[str]) -> bool:
    """Agent sends a message longer than 200 characters."""
    for line in lines:
        if line.startswith("AGENTE:"):
            text = line[7:].strip()
            if len(text) > 200:
                return True
    return False


# ---------------------------------------------------------------------------
# Batch analyzer
# ---------------------------------------------------------------------------

def analyze_batch(transcripts: List[Dict]) -> Dict[str, float]:
    """Analyze a list of transcripts and return pattern frequencies.

    Each item in transcripts should have:
      - transcript: str
      - durata: int
      - lines: List[str]  (transcript split by newline)
      - human_lines: int
    """
    if not transcripts:
        return {}

    total = len(transcripts)
    counts = {
        "ivr_loop": 0,
        "audio_issues": 0,
        "talking_over": 0,
        "long_gatekeeper_pitch": 0,
        "office_closed_stay": 0,
        "wait_loop": 0,
        "capisco_usage": 0,
        "audio_tags": 0,
        "long_monologue": 0,
    }

    for t in transcripts:
        text = t.get("transcript", "")
        durata = t.get("durata", 0)
        lines = t.get("lines", text.split("\n"))
        human_lines = t.get("human_lines", sum(1 for l in lines if l.startswith("CLIENTE:") and len(l) > 15))

        if detect_ivr_loop(text, durata, human_lines):
            counts["ivr_loop"] += 1
        if detect_audio_issues(text):
            counts["audio_issues"] += 1
        if detect_talking_over(lines):
            counts["talking_over"] += 1
        if detect_long_gatekeeper_pitch(lines):
            counts["long_gatekeeper_pitch"] += 1
        if detect_office_closed_stay(text, durata):
            counts["office_closed_stay"] += 1
        if detect_wait_loop(text, durata):
            counts["wait_loop"] += 1
        if detect_capisco_usage(text):
            counts["capisco_usage"] += 1
        if detect_audio_tags(text):
            counts["audio_tags"] += 1
        if detect_long_monologue(lines):
            counts["long_monologue"] += 1

    frequencies = {k: v / total for k, v in counts.items()}
    log.info("Batch analysis (%d calls): %s", total, {k: f"{v:.0%}" for k, v in frequencies.items() if v > 0})
    return frequencies


# ---------------------------------------------------------------------------
# Report generator — MONITOR ONLY
# ---------------------------------------------------------------------------

def optimize_prompt(agent_id: str, batch_analysis: Dict[str, float], dry_run: bool = False) -> List[str]:
    """Analyze patterns and generate alert report. Does NOT modify the prompt.

    Returns list of detected issues for logging purposes.
    """
    alerts = []

    for pattern, freq in sorted(batch_analysis.items(), key=lambda x: -x[1]):
        if freq < ACTIVATION_THRESHOLD:
            continue
        alerts.append(f"{pattern}: {freq:.0%}")

    if not alerts:
        log.info("No issues detected above threshold")
        return []

    # Save report
    report = {
        "agent_id": agent_id,
        "analyzed_at": datetime.now().isoformat(),
        "issues": {p: f for p, f in batch_analysis.items() if f >= ACTIVATION_THRESHOLD},
        "all_frequencies": {p: round(f, 3) for p, f in batch_analysis.items() if f > 0},
        "action": "REPORT ONLY — no auto-modification",
    }

    report_file = REPORTS_DIR / f"report_{agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_file.write_text(json.dumps(report, indent=2))
    log.info("Optimization report saved: %s", report_file)

    # Log alerts prominently
    for alert in alerts:
        log.warning("ALERT: %s", alert)

    # Track in changes file for visibility
    data = _load_changes()
    data["changes"].append({
        "type": "report",
        "agent_id": agent_id,
        "analyzed_at": datetime.now().isoformat(),
        "issues_detected": alerts,
        "action": "none — monitor only",
    })
    _save_changes(data)

    return alerts


def optimize_tts(agent_id: str, results: list) -> dict:
    """TTS analysis — MONITOR ONLY. Does NOT modify TTS settings.

    Returns empty dict (no changes made).
    Logs engagement/conversion/dropout signals for manual review.
    """
    completed = [r for r in results if r.get("esito") not in ("SKIPPED", None)]
    if len(completed) < 5:
        return {}

    total = len(completed)
    engaged = sum(1 for r in completed if r.get("durata", 0) >= 20)
    converted = sum(1 for r in completed if r.get("esito") in ("APPUNTAMENTO", "INTERESSATO_EMAIL"))
    dropouts = sum(1 for r in completed if 5 <= r.get("durata", 0) < 20)

    engagement_rate = engaged / total
    conversion_rate = converted / total
    dropout_rate = dropouts / total

    log.info("TTS signals (monitor only) — engaged: %.0f%%, converted: %.0f%%, dropout: %.0f%%",
             engagement_rate * 100, conversion_rate * 100, dropout_rate * 100)

    return {}  # No modifications


# ---------------------------------------------------------------------------
# Rollback (kept for backward compatibility with API endpoint)
# ---------------------------------------------------------------------------

def rollback_prompt(agent_id: str) -> bool:
    """Restore the most recent prompt backup."""
    import requests as req
    from config import ELEVENLABS_API_KEY, ELEVENLABS_BASE_URL

    BACKUPS_DIR_LOCAL = DATA_DIR / "prompt_backups"
    backups = sorted(BACKUPS_DIR_LOCAL.glob(f"prompt_{agent_id}_*.md"), reverse=True)
    if not backups:
        log.error("No backup found for agent %s", agent_id)
        return False

    prompt = backups[0].read_text()
    resp = req.patch(
        f"{ELEVENLABS_BASE_URL}/v1/convai/agents/{agent_id}",
        headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"},
        json={"conversation_config": {"agent": {"prompt": {"prompt": prompt}}}},
        timeout=30,
    )
    resp.raise_for_status()
    log.info("Prompt rolled back from %s", backups[0].name)
    return True


# ---------------------------------------------------------------------------
# Internal
# ---------------------------------------------------------------------------

def _load_changes() -> Dict:
    if CHANGES_FILE.exists():
        return json.loads(CHANGES_FILE.read_text())
    return {"changes": []}


def _save_changes(data: Dict):
    CHANGES_FILE.write_text(json.dumps(data, indent=2))
