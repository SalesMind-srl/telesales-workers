"""
Auto-ottimizzazione agente ElevenLabs basata sui transcript delle chiamate.

Ogni ciclo (ogni 5 min via APScheduler):
1. Analizza pattern problematici nei transcript
2. Calcola metriche di conversione (dropout, engagement, esiti)
3. Se ci sono problemi sopra soglia: chiede a Claude di generare fix mirati
4. Applica il prompt aggiornato + eventuali aggiustamenti TTS via ElevenLabs API
5. Backup del prompt precedente prima di ogni modifica

Non modifica nulla se ci sono meno di 5 chiamate da analizzare.
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests

from config import (
    ANTHROPIC_API_KEY,
    DATA_DIR,
    ELEVENLABS_API_KEY,
    ELEVENLABS_BASE_URL,
    ENABLE_PROMPT_OPTIMIZATION,
)

log = logging.getLogger(__name__)

REPORTS_DIR = DATA_DIR / "optimization_reports"
BACKUPS_DIR = DATA_DIR / "prompt_backups"
CHANGES_FILE = DATA_DIR / "prompt_changes.json"
REPORTS_DIR.mkdir(exist_ok=True)
BACKUPS_DIR.mkdir(exist_ok=True)

# Pattern deve apparire in >= 12% delle chiamate per scatenare un fix
ACTIVATION_THRESHOLD = 0.12
# Min chiamate analizzate per permettere modifiche
MIN_CALLS_FOR_EDIT = 5
# Max una modifica ogni N minuti (evita flapping)
MIN_MINUTES_BETWEEN_EDITS = 15


# ─── Pattern detectors ────────────────────────────────────────────────────────

def detect_ivr_loop(transcript: str, durata: int, human_lines: int) -> bool:
    ivr_kw = ["premere", "digitare", "digitate", "premete", "attendere in linea",
              "operatore disponibile", "we apologize", "rimanete in attesa"]
    ivr_count = sum(1 for kw in ivr_kw if kw in transcript.lower())
    return ivr_count >= 2 and durata > 30 and human_lines <= 1


def detect_audio_issues(transcript: str) -> bool:
    t = transcript.lower()
    pronto_count = len(re.findall(r"pronto\??\s", t))
    mi_senti_count = len(re.findall(r"mi sent[ie]", t))
    return (pronto_count + mi_senti_count) >= 4


def detect_talking_over(lines: List[str]) -> bool:
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
    gatekeeper_triggers = ["per che cosa", "a che proposito", "chi la desidera",
                           "per quale motivo", "di che si tratta"]
    for i, line in enumerate(lines):
        if line.startswith("CLIENTE:"):
            text = line[8:].strip().lower()
            if any(t in text for t in gatekeeper_triggers):
                for j in range(i + 1, min(i + 3, len(lines))):
                    if lines[j].startswith("AGENTE:"):
                        if len(lines[j][7:].strip()) > 120:
                            return True
    return False


def detect_office_closed_stay(transcript: str, durata: int) -> bool:
    t = transcript.lower()
    closed_kw = ["uffici sono chiusi", "orari sono", "uffici chiusi",
                 "i nostri uffici sono aperti", "uffici attualmente sono chiusi"]
    return any(kw in t for kw in closed_kw) and durata > 20


def detect_wait_loop(transcript: str, durata: int) -> bool:
    t = transcript.lower()
    wait_phrases = len(re.findall(r"(rimango in attesa|sono ancora in attesa|aspetto|continuo ad aspettare)", t))
    return wait_phrases >= 4 and durata > 60


def detect_capisco_usage(transcript: str) -> bool:
    agent_lines = re.findall(r"AGENTE: (.+)", transcript)
    return any("capisco" in line.lower() for line in agent_lines)


def detect_audio_tags(transcript: str) -> bool:
    return bool(re.search(
        r"\[(slow|fast|happy|sad|calm|clear|friendly|laugh|understanding|attentive|waiting)\]",
        transcript.lower()
    ))


def detect_long_monologue(lines: List[str]) -> bool:
    for line in lines:
        if line.startswith("AGENTE:") and len(line[7:].strip()) > 200:
            return True
    return False


def detect_banned_words(transcript: str) -> bool:
    banned = ["assolutamente", "comprendo", "posso disturbarla"]
    agent_lines = " ".join(re.findall(r"AGENTE: (.+)", transcript)).lower()
    return any(w in agent_lines for w in banned)


# ─── Batch analyzer ───────────────────────────────────────────────────────────

def analyze_batch(transcripts: List[Dict]) -> Dict[str, float]:
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
        "banned_words": 0,
    }

    for t in transcripts:
        text = t.get("transcript", "")
        durata = t.get("durata", 0)
        lines = t.get("lines", text.split("\n"))
        human_lines = t.get("human_lines",
            sum(1 for l in lines if l.startswith("CLIENTE:") and len(l) > 15))

        if detect_ivr_loop(text, durata, human_lines):    counts["ivr_loop"] += 1
        if detect_audio_issues(text):                     counts["audio_issues"] += 1
        if detect_talking_over(lines):                    counts["talking_over"] += 1
        if detect_long_gatekeeper_pitch(lines):           counts["long_gatekeeper_pitch"] += 1
        if detect_office_closed_stay(text, durata):       counts["office_closed_stay"] += 1
        if detect_wait_loop(text, durata):                counts["wait_loop"] += 1
        if detect_capisco_usage(text):                    counts["capisco_usage"] += 1
        if detect_audio_tags(text):                       counts["audio_tags"] += 1
        if detect_long_monologue(lines):                  counts["long_monologue"] += 1
        if detect_banned_words(text):                     counts["banned_words"] += 1

    frequencies = {k: v / total for k, v in counts.items()}
    log.info("Batch analysis (%d calls): %s", total,
             {k: f"{v:.0%}" for k, v in frequencies.items() if v > 0})
    return frequencies


# ─── ElevenLabs API helpers ───────────────────────────────────────────────────

def _el_headers():
    return {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}


def _fetch_current_prompt(agent_id: str) -> Optional[str]:
    try:
        r = requests.get(
            f"{ELEVENLABS_BASE_URL}/v1/convai/agents/{agent_id}",
            headers=_el_headers(), timeout=20
        )
        r.raise_for_status()
        return r.json()["conversation_config"]["agent"]["prompt"]["prompt"]
    except Exception as e:
        log.error("Cannot fetch current prompt: %s", e)
        return None


def _patch_agent(agent_id: str, payload: dict) -> bool:
    try:
        r = requests.patch(
            f"{ELEVENLABS_BASE_URL}/v1/convai/agents/{agent_id}",
            headers=_el_headers(), json=payload, timeout=30
        )
        r.raise_for_status()
        return True
    except Exception as e:
        log.error("PATCH agent failed: %s", e)
        return False


def _backup_prompt(agent_id: str, prompt: str):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUPS_DIR / f"prompt_{agent_id}_{ts}.md"
    backup.write_text(prompt)
    log.info("Prompt backup → %s", backup.name)


# ─── Claude-powered prompt fixer ─────────────────────────────────────────────

def _ask_claude_for_fixes(current_prompt: str, issues: Dict[str, float],
                           transcript_examples: List[str]) -> Optional[str]:
    """Ask Claude to generate a targeted improved prompt based on detected issues."""
    if not ANTHROPIC_API_KEY:
        log.warning("ANTHROPIC_API_KEY not set — skip Claude optimization")
        return None

    issues_desc = "\n".join(
        f"- {k.replace('_', ' ')}: {v:.0%} delle chiamate" for k, v in issues.items()
    )
    examples_text = "\n\n---\n\n".join(transcript_examples[:3]) if transcript_examples else "(nessun esempio disponibile)"

    system = (
        "Sei un esperto di ottimizzazione prompt per agenti AI outbound B2B italiani. "
        "Fai modifiche MINIME e CHIRURGICHE al prompt — non riscrivere, non aggiungere sezioni inutili. "
        "Rispondi SOLO con il prompt aggiornato, niente spiegazioni prima o dopo."
    )

    user = f"""Agente: Mario di Cribis — telesales outbound B2B italiano.
Obiettivo: fissare call di 15 minuti con consulente Cribis.

PROBLEMI RILEVATI nelle ultime chiamate:
{issues_desc}

ESEMPI DI TRANSCRIPT con problemi:
{examples_text}

PROMPT ATTUALE:
{current_prompt}

Correggi SOLO i problemi elencati. Non cambiare parti che funzionano.
Mantieni la struttura identica (stesse sezioni, stesso formato).
Rispondi SOLO con il prompt corretto, nessun'altra parola."""

    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 4096,
                "system": system,
                "messages": [{"role": "user", "content": user}],
            },
            timeout=60,
        )
        r.raise_for_status()
        new_prompt = r.json()["content"][0]["text"].strip()
        if len(new_prompt) < len(current_prompt) * 0.5:
            log.warning("Claude returned suspiciously short prompt — skip")
            return None
        return new_prompt
    except Exception as e:
        log.error("Claude API call failed: %s", e)
        return None


# ─── TTS auto-tuner ──────────────────────────────────────────────────────────

def _compute_tts_adjustments(results: list, current_speed: float, current_stability: float) -> dict:
    """
    Aggiusta speed e stability in base a segnali di engagement.

    Logica:
    - Alta % dropout (5-20s) → voce forse troppo lenta/robota → speed +0.02
    - Alta % no risposta (durata < 5s) → non correlato alla voce, niente
    - Buona conversione → non toccare niente
    - Bassa stabilità (molti rumori/interruzioni) → stability +0.03
    """
    completed = [r for r in results if r.get("esito") not in ("SKIPPED", None)]
    if len(completed) < 8:
        return {}

    total = len(completed)
    dropout   = sum(1 for r in completed if 5 <= r.get("durata", 0) < 20)
    engaged   = sum(1 for r in completed if r.get("durata", 0) >= 20)
    converted = sum(1 for r in completed if r.get("esito") in (
        "APPUNTAMENTO", "INTERESSATO_EMAIL", "INTERESSATO", "Appuntamento Fissato",
        "Interessato", "Email Fornita", "appointment", "high", "medium"
    ))

    dropout_rate   = dropout / total
    engaged_rate   = engaged / total
    conversion_rate = converted / total

    log.info("TTS signals — engaged: %.0f%%, converted: %.0f%%, dropout: %.0f%%",
             engaged_rate * 100, conversion_rate * 100, dropout_rate * 100)

    adjustments = {}

    # Se conversion è buona (>10%): non toccare niente
    if conversion_rate >= 0.10:
        log.info("Conversion rate %.0f%% — TTS stable", conversion_rate * 100)
        return {}

    # Alto dropout → prova a velocizzare leggermente
    if dropout_rate > 0.30 and current_speed < 1.0:
        new_speed = min(round(current_speed + 0.02, 2), 1.0)
        adjustments["speed"] = new_speed
        log.info("High dropout %.0f%% → speed %.2f → %.2f", dropout_rate * 100, current_speed, new_speed)

    # Basso engagement → prova a stabilizzare la voce
    if engaged_rate < 0.25 and current_stability < 0.75:
        new_stability = min(round(current_stability + 0.03, 2), 0.75)
        adjustments["stability"] = new_stability
        log.info("Low engagement %.0f%% → stability %.2f → %.2f",
                 engaged_rate * 100, current_stability, new_stability)

    return adjustments


# ─── Main entry points (chiamati da pipeline.py) ──────────────────────────────

def optimize_prompt(agent_id: str, batch_analysis: Dict[str, float],
                    transcript_examples: Optional[List[str]] = None) -> List[str]:
    """
    Analizza pattern e, se necessario, aggiorna il prompt via ElevenLabs API.
    Usa Claude per generare fix chirurgici basati su esempi reali.
    Restituisce lista di issue fixate (o vuota se nessuna modifica).
    """
    if not ENABLE_PROMPT_OPTIMIZATION:
        return []

    issues = {k: v for k, v in batch_analysis.items() if v >= ACTIVATION_THRESHOLD}
    if not issues:
        log.info("No issues above threshold — prompt unchanged")
        return []

    # Verifica min tempo tra una modifica e la prossima
    changes = _load_changes()
    last_prompt_edit = next(
        (c for c in reversed(changes.get("changes", [])) if c.get("type") == "prompt_edit"),
        None
    )
    if last_prompt_edit:
        last_ts = datetime.fromisoformat(last_prompt_edit["edited_at"])
        elapsed_minutes = (datetime.now() - last_ts).total_seconds() / 60
        if elapsed_minutes < MIN_MINUTES_BETWEEN_EDITS:
            log.info("Last prompt edit was %.0f min ago (min %d) — skip",
                     elapsed_minutes, MIN_MINUTES_BETWEEN_EDITS)
            return list(issues.keys())

    current_prompt = _fetch_current_prompt(agent_id)
    if not current_prompt:
        return []

    examples = transcript_examples or []
    new_prompt = _ask_claude_for_fixes(current_prompt, issues, examples)
    if not new_prompt or new_prompt == current_prompt:
        log.info("No prompt changes from Claude")
        return list(issues.keys())

    # Backup + apply
    _backup_prompt(agent_id, current_prompt)
    success = _patch_agent(agent_id, {
        "conversation_config": {"agent": {"prompt": {"prompt": new_prompt}}}
    })

    if success:
        log.info("Prompt updated — fixed issues: %s", list(issues.keys()))
        changes["changes"].append({
            "type": "prompt_edit",
            "agent_id": agent_id,
            "edited_at": datetime.now().isoformat(),
            "issues_fixed": list(issues.keys()),
            "issue_frequencies": {k: round(v, 3) for k, v in issues.items()},
        })
        _save_changes(changes)

    # Salva report
    report = {
        "agent_id": agent_id,
        "analyzed_at": datetime.now().isoformat(),
        "issues": {k: round(v, 3) for k, v in issues.items()},
        "prompt_updated": success,
    }
    rfile = REPORTS_DIR / f"report_{agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    rfile.write_text(json.dumps(report, indent=2))

    return list(issues.keys()) if success else []


def optimize_tts(agent_id: str, results: list) -> dict:
    """
    Aggiusta speed e stability dell'agente in base ai segnali di engagement.
    Legge i settings correnti dall'API, calcola delta, applica se necessario.
    """
    if not ENABLE_PROMPT_OPTIMIZATION:
        return {}

    completed = [r for r in results if r.get("esito") not in ("SKIPPED", None)]
    if len(completed) < MIN_CALLS_FOR_EDIT:
        return {}

    # Leggi settings correnti
    try:
        r = requests.get(
            f"{ELEVENLABS_BASE_URL}/v1/convai/agents/{agent_id}",
            headers=_el_headers(), timeout=20
        )
        r.raise_for_status()
        tts = r.json()["conversation_config"]["tts"]
        current_speed     = tts.get("speed", 0.90)
        current_stability = tts.get("stability", 0.62)
    except Exception as e:
        log.error("Cannot fetch current TTS settings: %s", e)
        return {}

    adjustments = _compute_tts_adjustments(results, current_speed, current_stability)
    if not adjustments:
        return {}

    tts_payload = {k: v for k, v in adjustments.items()}
    success = _patch_agent(agent_id, {
        "conversation_config": {"tts": tts_payload}
    })

    if success:
        log.info("TTS updated: %s", adjustments)
        changes = _load_changes()
        changes["changes"].append({
            "type": "tts_edit",
            "agent_id": agent_id,
            "edited_at": datetime.now().isoformat(),
            "adjustments": adjustments,
            "prev": {"speed": current_speed, "stability": current_stability},
        })
        _save_changes(changes)
        return adjustments

    return {}


# ─── Rollback ─────────────────────────────────────────────────────────────────

def rollback_prompt(agent_id: str) -> bool:
    backups = sorted(BACKUPS_DIR.glob(f"prompt_{agent_id}_*.md"), reverse=True)
    if not backups:
        log.error("No backup found for agent %s", agent_id)
        return False
    prompt = backups[0].read_text()
    ok = _patch_agent(agent_id, {
        "conversation_config": {"agent": {"prompt": {"prompt": prompt}}}
    })
    if ok:
        log.info("Prompt rolled back from %s", backups[0].name)
    return ok


# ─── Internal ─────────────────────────────────────────────────────────────────

def _load_changes() -> Dict:
    if CHANGES_FILE.exists():
        return json.loads(CHANGES_FILE.read_text())
    return {"changes": []}


def _save_changes(data: Dict):
    CHANGES_FILE.write_text(json.dumps(data, indent=2))
