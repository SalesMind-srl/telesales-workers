"""Classify ElevenLabs call transcripts using rule-based analysis.

No external LLM needed - uses keyword matching, duration, and pattern
detection to classify calls accurately.
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict

log = logging.getLogger(__name__)


# --- Keyword patterns ---

EMAIL_PATTERN = re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')

APPOINTMENT_KEYWORDS = [
    "appuntamento", "fissato", "confermato", "call telefonica",
    "ci vediamo", "va bene per", "fissiamo", "meeting",
    "quindici minuti", "15 minuti",
]

INTERESTED_KEYWORDS = [
    "mi mandi una mail", "mandi una email", "mandi email",
    "scriva una mail", "scriva email", "scrivere una mail",
    "le passo l'indirizzo", "le do l'email", "indirizzo email",
    "chiocciola", "@", "punto com", "punto it",
    "mandare email", "inviare email",
]

NOT_INTERESTED_KEYWORDS = [
    "non mi interessa", "non interessa", "non ci interessa",
    "non le faccio perdere tempo", "non siamo interessati",
    "non abbiamo bisogno", "non ho bisogno", "no grazie",
    "non vogliamo", "non ne abbiamo bisogno",
]

CALLBACK_KEYWORDS = [
    "richiamare", "richiami", "riprovare", "riprovi",
    "non c'e", "non c'è", "non è in sede", "non in ufficio",
    "non è disponibile", "è in riunione", "è assente",
    "è in ferie", "è fuori", "non è presente",
    "provi a richiamare", "provi nel pomeriggio",
    "provi domani", "provi lunedi", "provi la prossima",
    "problemi audio", "non la sento", "sento male",
    "linea disturbata",
]

IVR_KEYWORDS = [
    "premere", "digitare", "digitate", "premete",
    "uffici sono chiusi", "orari sono", "dal lunedi al venerdi",
    "casella vocale", "operatore disponibile",
    "rimanete in attesa", "attendere in linea",
    "we apologize for the wait",
]

WHEN_PATTERNS = {
    r"dopo le (\d{1,2})": lambda m, oggi: oggi.replace(hour=int(m.group(1)), minute=0),
    r"dalle (\d{1,2})": lambda m, oggi: oggi.replace(hour=int(m.group(1)), minute=0),
    r"pomeriggio": lambda m, oggi: oggi.replace(hour=14, minute=30),
    r"tardo pomeriggio": lambda m, oggi: oggi.replace(hour=17, minute=0),
    r"domani mattina": lambda m, oggi: (oggi + timedelta(days=1)).replace(hour=9, minute=30),
    r"domani pomeriggio": lambda m, oggi: (oggi + timedelta(days=1)).replace(hour=14, minute=30),
    r"domani": lambda m, oggi: (oggi + timedelta(days=1)).replace(hour=10, minute=0),
    r"luned[iì]": lambda m, oggi: _next_weekday(oggi, 0).replace(hour=9, minute=30),
    r"marted[iì]": lambda m, oggi: _next_weekday(oggi, 1).replace(hour=9, minute=30),
    r"mercoled[iì]": lambda m, oggi: _next_weekday(oggi, 2).replace(hour=9, minute=30),
    r"gioved[iì]": lambda m, oggi: _next_weekday(oggi, 3).replace(hour=9, minute=30),
    r"venerd[iì]": lambda m, oggi: _next_weekday(oggi, 4).replace(hour=9, minute=30),
    r"prossima settimana": lambda m, oggi: _next_weekday(oggi, 0).replace(hour=9, minute=30),
    r"fra qualche giorno": lambda m, oggi: (oggi + timedelta(days=3)).replace(hour=9, minute=30),
    r"tra qualche giorno": lambda m, oggi: (oggi + timedelta(days=3)).replace(hour=9, minute=30),
}


def _next_weekday(d, weekday):
    """Return the next date that falls on the given weekday (0=Mon, 4=Fri)."""
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return d + timedelta(days=days_ahead)


def _count_keywords(text_lower, keywords):
    return sum(1 for kw in keywords if kw in text_lower)


def _extract_email(text):
    emails = EMAIL_PATTERN.findall(text)
    # Filter out common false positives
    for e in emails:
        if not any(x in e.lower() for x in ["example", "test", "none", "null"]):
            return e
    return None


IVR_WORDS = {
    "aperti", "chiusi", "apriamo", "chiudiamo", "benvenuti", "welcome",
    "premere", "digitare", "attesa", "trasferiti", "operatore", "disponibile",
    "orari", "lunedi", "venerdi", "grazie", "arrivederci",
}


def _extract_contact_name(transcript_lower, lines):
    """Try to extract who actually answered the phone."""
    for line in lines:
        if line.startswith("CLIENTE:"):
            text = line[8:].strip().lower()
            m = re.search(r"sono (\w+)", text)
            if m and len(m.group(1)) > 2:
                name = m.group(1)
                if name.lower() not in IVR_WORDS and len(name) > 3:
                    return name.capitalize()
    return None


def _extract_when(text_lower, oggi):
    """Extract callback time from transcript."""
    for pattern, resolver in WHEN_PATTERNS.items():
        m = re.search(pattern, text_lower)
        if m:
            try:
                dt = resolver(m, oggi)
                return dt.strftime("%Y-%m-%dT%H:%M")
            except Exception:
                continue
    return None


def _build_agent_notes(info, classification, transcript_lower, contact_parlato):
    """Build specific instructions for the callback agent."""
    parts = []
    nome = info.get("nome_contatto", "")
    if nome:
        parts.append(f"Chiedere di {nome}")

    if contact_parlato:
        parts.append(f"Nella chiamata precedente ha risposto {contact_parlato}")

    # Extract specific context from transcript
    if "riunione" in transcript_lower:
        parts.append("Il referente era in riunione")
    elif "ferie" in transcript_lower or "vacanza" in transcript_lower:
        parts.append("Il referente era in ferie")
    elif "non in ufficio" in transcript_lower or "non è in sede" in transcript_lower:
        parts.append("Il referente non era in sede")
    elif "problemi audio" in transcript_lower or "sento male" in transcript_lower:
        parts.append("La chiamata precedente aveva problemi audio")

    if "interno" in transcript_lower:
        m = re.search(r"interno\s*(\d+)", transcript_lower)
        if m:
            parts.append(f"Digitare interno {m.group(1)}")

    return ". ".join(parts) if parts else None


def classify_call(
    transcript: str,
    azienda: str,
    citta: str,
    nome_contatto: str,
    durata: int,
) -> Dict:
    """Classify a call transcript. Returns classification dict."""
    oggi = datetime.now()
    text_lower = transcript.lower()
    lines = transcript.strip().split("\n")
    cliente_lines = [l for l in lines if l.startswith("CLIENTE:")]
    agente_lines = [l for l in lines if l.startswith("AGENTE:")]

    info = {"nome_contatto": nome_contatto, "azienda": azienda}

    # Count human interaction
    human_responses = len([l for l in cliente_lines if len(l) > 15])

    # Scores
    appointment_score = _count_keywords(text_lower, APPOINTMENT_KEYWORDS)
    interested_score = _count_keywords(text_lower, INTERESTED_KEYWORDS)
    not_interested_score = _count_keywords(text_lower, NOT_INTERESTED_KEYWORDS)
    callback_score = _count_keywords(text_lower, CALLBACK_KEYWORDS)
    ivr_score = _count_keywords(text_lower, IVR_KEYWORDS)

    # Extract data
    email = _extract_email(transcript)
    contact_parlato = _extract_contact_name(text_lower, lines)
    quando = _extract_when(text_lower, oggi)

    # --- Classification logic ---

    # 1. Very short / no human interaction = IVR
    if durata < 10 or (human_responses == 0 and ivr_score > 0):
        return {
            "esito": "IVR_NON_RISPOSTO",
            "riassunto": "Nessuna risposta umana" if human_responses == 0 else "Chiamata brevissima",
            "email_ottenuta": None,
            "contatto_parlato": None,
            "quando_richiamare": None,
            "note_per_agente": None,
        }

    # 2. Only IVR, no human ever answered
    if ivr_score >= 3 and human_responses <= 1 and callback_score == 0:
        return {
            "esito": "IVR_NON_RISPOSTO",
            "riassunto": "Solo sistema IVR, nessun operatore ha risposto",
            "email_ottenuta": None,
            "contatto_parlato": None,
            "quando_richiamare": None,
            "note_per_agente": None,
        }

    # 3. Appointment confirmed
    if appointment_score >= 1 and not_interested_score == 0:
        return {
            "esito": "APPUNTAMENTO",
            "riassunto": "Appuntamento confermato",
            "email_ottenuta": email,
            "contatto_parlato": contact_parlato,
            "quando_richiamare": quando,
            "note_per_agente": _build_agent_notes(info, "APPUNTAMENTO", text_lower, contact_parlato),
        }

    # 4. Gave email / interested
    if email or interested_score >= 2:
        riassunto = "Ha fornito email" if email else "Ha mostrato interesse"
        if email:
            riassunto += f" ({email})"
        return {
            "esito": "INTERESSATO_EMAIL",
            "riassunto": riassunto,
            "email_ottenuta": email,
            "contatto_parlato": contact_parlato,
            "quando_richiamare": quando,
            "note_per_agente": _build_agent_notes(info, "INTERESSATO_EMAIL", text_lower, contact_parlato),
        }

    # 5. Not interested (explicit rejection)
    if not_interested_score >= 1 and callback_score == 0:
        return {
            "esito": "NON_INTERESSATO",
            "riassunto": "Non interessato",
            "email_ottenuta": None,
            "contatto_parlato": contact_parlato,
            "quando_richiamare": None,
            "note_per_agente": None,
        }

    # 6. Callback needed (referent not there, audio issues, etc.)
    if callback_score >= 1 or (human_responses >= 1 and not_interested_score == 0 and quando):
        if not quando:
            # Default: tomorrow at 10
            quando = (oggi + timedelta(days=1)).replace(hour=10, minute=0).strftime("%Y-%m-%dT%H:%M")

        # Build riassunto
        riassunto_parts = []
        if "riunione" in text_lower:
            riassunto_parts.append("Referente in riunione")
        elif "ferie" in text_lower or "vacanza" in text_lower:
            riassunto_parts.append("Referente in ferie")
        elif "non c'" in text_lower or "non è in sede" in text_lower or "non in ufficio" in text_lower:
            riassunto_parts.append("Referente non in sede")
        elif "problemi audio" in text_lower or "sento male" in text_lower:
            riassunto_parts.append("Problemi audio")
        else:
            riassunto_parts.append("Da richiamare")

        if contact_parlato:
            riassunto_parts.append(f"parlato con {contact_parlato}")

        return {
            "esito": "RICHIAMO",
            "riassunto": ", ".join(riassunto_parts),
            "email_ottenuta": email,
            "contatto_parlato": contact_parlato,
            "quando_richiamare": quando,
            "note_per_agente": _build_agent_notes(info, "RICHIAMO", text_lower, contact_parlato),
        }

    # 7. Default: if there was human interaction but no clear outcome
    if human_responses >= 2 and durata > 30:
        return {
            "esito": "RICHIAMO",
            "riassunto": "Conversazione avvenuta, esito non chiaro",
            "email_ottenuta": email,
            "contatto_parlato": contact_parlato,
            "quando_richiamare": (oggi + timedelta(days=1)).replace(hour=10, minute=0).strftime("%Y-%m-%dT%H:%M"),
            "note_per_agente": _build_agent_notes(info, "RICHIAMO", text_lower, contact_parlato),
        }

    # 8. Fallback: IVR / non risposto
    return {
        "esito": "IVR_NON_RISPOSTO",
        "riassunto": "Nessuna conversazione significativa",
        "email_ottenuta": None,
        "contatto_parlato": None,
        "quando_richiamare": None,
        "note_per_agente": None,
    }
