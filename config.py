import os
from pathlib import Path

# ─── API Keys ────────────────────────────────────────────────────────────────
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_BASE_URL = "https://api.elevenlabs.io"

GHL_TOKEN = os.getenv("GHL_API_KEY", "pit-4a3168a0-2931-4b63-9314-b484bc245849")
GHL_LOCATION_ID = os.getenv("GHL_LOCATION_ID", "axueu1S0Ny1W9aeGbARf")
GHL_BASE_URL = "https://services.leadconnectorhq.com"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# ─── GHL Pipeline principale (fallback) ──────────────────────────────────────
# Pipeline globale "Telesales" — usata se non è configurata quella del setter
GHL_PIPELINE_ID = "MwQdkvIh5UNltNAVRpFn"

# Stage IDs (pipeline "Telesales" — stessi stage in tutte le pipeline)
GHL_STAGE_LEAD_NUOVO        = "b472183c-d649-4ed0-b332-a31fc066809f"  # 1. Lead Nuovo
GHL_STAGE_AI_QUALIFICA      = "637db8a4-d39e-4cc3-8688-55baa17e3450"  # 2. AI Qualifica
GHL_STAGE_SETTER_CHIAMA     = "e9226e3d-1079-4159-8cba-f9c552223588"  # 3. Setter Chiama
GHL_STAGE_APPUNTAMENTO      = "a537d54c-d097-495c-ad0c-c5f95d27a306"  # 4. Appuntamento
GHL_STAGE_CLOSER_DEMO       = "e7c3aae3-02ce-4521-a8fd-319110cbb748"  # 5. Closer / Demo
GHL_STAGE_CHIUSO_VINTO      = "3f041bac-ab96-4509-84a3-f7eaf49e075d"  # 6. Chiuso Vinto
GHL_STAGE_NURTURE           = "17ec3afb-221c-4d39-9f5e-9171ec08a5cb"  # 7. Nurture

# ─── Pipeline per setter (una per cliente) ───────────────────────────────────
# Imposta le env vars su Railway dopo aver creato le pipeline da GHL UI.
# Finché non sono configurate, usa la pipeline principale "Telesales".
# Stage names sono identici — il backend usa gli stage della pipeline giusta.
# HOW TO: GHL → Opportunities → Pipelines → + New Pipeline → copia ID → Railway env var
SETTER_PIPELINE_MAP = {
    "Setter - Filippo": os.getenv("PIPELINE_FILIPPO", GHL_PIPELINE_ID),
    "Setter - Adriana": os.getenv("PIPELINE_ADRIANA", GHL_PIPELINE_ID),
    "Setter - Edoardo": os.getenv("PIPELINE_EDOARDO", GHL_PIPELINE_ID),
    "Setter - Claudia": os.getenv("PIPELINE_CLAUDIA", GHL_PIPELINE_ID),
    "Setter - Laura":   os.getenv("PIPELINE_LAURA",   GHL_PIPELINE_ID),
}

# Stage IDs per pipeline setter — popolare dopo creazione pipeline
# Struttura: { pipeline_id: { stage_name: stage_id } }
# Finché vuoto, usa gli stage della pipeline principale sopra.
SETTER_STAGE_MAP: dict = {}

# ─── GHL Custom Field IDs ────────────────────────────────────────────────────
# Campi chiamata AI
GHL_FIELD_ESITO_AI              = "nSa9sSpAlYMrZPAsIYnq"  # Esito AI Call (SINGLE_OPTIONS)
GHL_FIELD_DATA_ULTIMO_CONTATTO  = "s7oF6RbqYCBw2aeoc1e7"  # Data Ultimo Contatto (DATE)
GHL_FIELD_NOTE_CHIAMATA         = "Y7Dsdc03d6IsEyjiiAWM"  # Note Chiamata (LARGE_TEXT)
GHL_FIELD_RECORDING_URL         = "W5NUtkHjnfrVFuKc83me"  # Recording URL (TEXT)
GHL_FIELD_DURATA_CHIAMATA       = "toUCEDScSJoXgqhaElBT"  # Durata Chiamata (NUMERICAL)
GHL_FIELD_RIASSUNTO_AI          = "1WkXDP4u90zAiIzYUK48"  # Riassunto AI (LARGE_TEXT)
GHL_FIELD_EMAIL_REFERENTE       = "Imrkz2TbIoOfFqEEUAsP"  # Email Referente (TEXT)
GHL_FIELD_NOME_REFERENTE        = "iLNeaUt2HuS2TENLSx69"  # Nome Referente (TEXT)
GHL_FIELD_BATCH_ELEVENLABS      = "piUGKVCzB2oguN7w5wBm"  # Batch ElevenLabs (TEXT)

# Campi classificazione / assegnazione
GHL_FIELD_OPERATORE             = "jLztWOcrNXljEZDPtvzh"  # Operatore Assegnato (SINGLE_OPTIONS)
GHL_FIELD_FONTE_LEAD            = "YJoWi6M2dlexnVAfgLet"  # Fonte Lead (SINGLE_OPTIONS)
GHL_FIELD_CANALE                = "7sjzbQoatt6urEPSaCFU"  # Canale (SINGLE_OPTIONS)
GHL_FIELD_CLIENTE_ASSEGNATO     = "z8r56KP0jTtQ7rTvCqUm"  # Cliente Assegnato (SINGLE_OPTIONS)
GHL_FIELD_SCORE_LEAD            = "pPtn9Tnb00Y0z4wIswGC"  # Score Lead (NUMERICAL)

# Campi azienda (già esistenti da import Cribis)
GHL_FIELD_SETTORE               = "7VjfIt0AercSRc3RcbyH"  # Settore Azienda
GHL_FIELD_SETTORE_CRIBIS        = "oTNbark8p5DaI9gGbQPt"  # Settore Cribis
GHL_FIELD_PROVINCIA             = "aD1cayeJVjDWC36EwLv5"  # Provincia
GHL_FIELD_DATA_PROSSIMA_CHIAMATA= "GeomTH74lnioAF3V9V5Z"  # Data Prossima Chiamata

# ─── Mapping ElevenLabs interest_level → GHL picklist ────────────────────────
# ElevenLabs data_collection: interest_level = high / medium / low / none
INTEREST_TO_GHL_ESITO = {
    "high":   "Interessato",
    "medium": "Email Fornita",
    "low":    "Non Interessato",
    "none":   "Non Risposto / IVR",
}

ESITO_TO_GHL = {
    "appointment": "Appuntamento Fissato",
    "high":        "Interessato",
    "medium":      "Email Fornita",
    "low":         "Non Interessato",
    "none":        "Non Risposto / IVR",
    # fallback da vecchio classifier
    "APPUNTAMENTO":       "Appuntamento Fissato",
    "INTERESSATO_EMAIL":  "Email Fornita",
    "INTERESSATO":        "Interessato",
    "RICHIAMO":           "Richiamata",
    "NON_INTERESSATO":    "Non Interessato",
    "IVR_NON_RISPOSTO":   "Non Risposto / IVR",
    "NUMERO_ERRATO":      "Numero Errato",
}

# ElevenLabs interest_level → Score Lead (0-100)
INTEREST_TO_SCORE = {
    "appointment": 100,
    "high":        75,
    "medium":      40,
    "low":         10,
    "none":        0,
}

# ElevenLabs interest_level → GHL Pipeline Stage (pipeline principale)
# Le pipeline setter usano gli stessi nomi stage ma ID diversi — risolti a runtime.
INTEREST_TO_STAGE = {
    "high":        GHL_STAGE_SETTER_CHIAMA,   # 3. Setter Chiama
    "medium":      GHL_STAGE_AI_QUALIFICA,    # 2. AI Qualifica
    "low":         GHL_STAGE_NURTURE,         # 7. Nurture
    "none":        None,                       # Non risposto → non spostare
    "appointment": GHL_STAGE_APPUNTAMENTO,    # 4. Appuntamento
}

# ─── Operatori (per tag/campo) ────────────────────────────────────────────────
TAG_TO_OPERATORE = {
    "cliente-filippo": "Setter - Filippo",
    "cliente-adriana": "Setter - Adriana",
    "cliente-edoardo": "Setter - Edoardo",
    "cliente-claudia": "Setter - Claudia",
    "cliente-laura":   "Setter - Laura",
}

# Mappa tag → valore campo "Cliente Assegnato"
TAG_TO_CLIENTE = {
    "cliente-filippo": "Filippo",
    "cliente-adriana": "Adriana",
    "cliente-edoardo": "Edoardo",
    "cliente-claudia": "Claudia",
    "cliente-laura":   "Laura",
}

# Mappa tag → quale pipeline usare per il contatto
TAG_TO_PIPELINE = {tag: SETTER_PIPELINE_MAP[op] for tag, op in TAG_TO_OPERATORE.items()}

# ─── Paths & Scheduler ───────────────────────────────────────────────────────
DATA_DIR = Path(os.getenv("DATA_DIR", Path(__file__).parent / "data"))
DATA_DIR.mkdir(exist_ok=True)
PROCESSED_FILE     = DATA_DIR / "processed_batches.json"
GHL_CONTACTS_CACHE = DATA_DIR / "contacts_cache.json"

CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "5"))
TIMEZONE = "Europe/Rome"

FUZZY_THRESHOLD = 0.82
GHL_SLEEP = 0.3   # ridotto da 0.5 — retry gestisce i 429

# ─── Prompt optimization ────────────────────────────────────────────────────
ENABLE_PROMPT_OPTIMIZATION = os.getenv("ENABLE_PROMPT_OPTIMIZATION", "true").lower() == "true"

# ─── Monitored agents (single outbound — non batch) ──────────────────────────
# Usato SOLO per chiamate singole outbound (non batch).
# I batch vengono rilevati automaticamente dal workspace, indipendentemente dall'agente.
# Aggiungere qui tutti gli agenti attivi che fanno chiamate singole (non batch).
# Trovare agent ID: ElevenLabs UI → Agents → seleziona agente → copia ID dall'URL.
MONITORED_AGENT_IDS = os.getenv(
    "MONITORED_AGENT_IDS",
    # Marco - Prequalifica Telesales + Outbound Cribis (account marco_ai)
    "agent_1901kme2h64pfmcb53ggjban6j8x,agent_3201km1eh8yne4r9c1dakbrbdgm5"
)
