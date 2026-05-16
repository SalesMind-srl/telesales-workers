#!/usr/bin/env python3
"""
Culligan Batch Caller — Legge il foglio Google e lancia chiamate outbound
tramite ElevenLabs Conversational AI (batch calling API).

Stesso metodo usato per Cribis test coworking.

FOGLIO: 1PiezlYSd5TZNBCRTvzBhx_yVCGfN6aMI3PXdOYU4xu8
TAB:    aziende_bolzano_VERIFICATE

AGENTE: Marco - Culligan Bolzano HoReCa
        agent_5101kreejrz1e98rfzjrf3brhd50

TELEFONO OUTBOUND: phnum_1501kr3sx76sfxeap503jqy1m7j9
        (+390554652406 — SIP Telnyx Italia)

USO:
    # Dry run (mostra cosa farebbe senza chiamare)
    python3 culligan_batch_caller.py --dry-run

    # Lancia batch (max 10 alla volta di default)
    python3 culligan_batch_caller.py

    # Lancia batch con limite custom
    python3 culligan_batch_caller.py --limit 5

    # Lancia TUTTE le righe non ancora chiamate
    python3 culligan_batch_caller.py --limit 0
"""

import os
import re
import sys
import json
import time
import argparse
from datetime import datetime

# Google Sheets
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# ElevenLabs
import requests

# ============================================================================
# CONFIGURAZIONE
# ============================================================================

ELEVENLABS_API_KEY = os.getenv(
    "ELEVENLABS_API_KEY",
    "sk_9148f936dc1c67e88b13f7b400333cb87813613682f70726"
)
ELEVENLABS_BASE_URL = "https://api.elevenlabs.io"

CULLIGAN_AGENT_ID = "agent_5101kreejrz1e98rfzjrf3brhd50"
PHONE_NUMBER_ID = "phnum_1501kr3sx76sfxeap503jqy1m7j9"

SHEET_ID = "1PiezlYSd5TZNBCRTvzBhx_yVCGfN6aMI3PXdOYU4xu8"
TAB_NAME = "aziende_bolzano_VERIFICATE"

SA_PATH = os.path.join(os.path.dirname(__file__), "service-account.json")

# Colonne (0-based)
COL_NOME_AZIENDA = 0    # A - NOME AZIENDE
COL_NOME_TITOLARE = 1   # B - NOME TITOLARE
COL_NOTE = 2             # C - NOTE
COL_INDIRIZZO = 3        # D - INDIRIZZO
COL_TELEFONO = 4         # E - TELEFONO
COL_PRESENTE = 5         # F - PRESENTE SI O NO
COL_DATA_CHIAMATA = 6    # G - DATA DELLA CHIAMATA
COL_DATA_APPUNTAMENTO = 7  # H - DATA DELL'APPUNTAMENTO

DEFAULT_BATCH_LIMIT = 10
CONCURRENCY = 1  # Chiamate simultanee (1 = una alla volta)

# ============================================================================
# GOOGLE SHEETS
# ============================================================================

def get_sheets_service():
    creds = Credentials.from_service_account_file(
        SA_PATH,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return build("sheets", "v4", credentials=creds)


def read_all_rows(service):
    """Legge tutte le righe dal foglio."""
    result = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=f"'{TAB_NAME}'!A:H"
    ).execute()
    return result.get("values", [])


def mark_called(service, row_index, date_str):
    """Segna la data di chiamata nella colonna G (DATA DELLA CHIAMATA)."""
    col_letter = "G"  # COL_DATA_CHIAMATA
    service.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range=f"'{TAB_NAME}'!{col_letter}{row_index + 1}",
        valueInputOption="USER_ENTERED",
        body={"values": [[date_str]]}
    ).execute()


# ============================================================================
# PARSING DATI
# ============================================================================

def extract_categoria(note: str) -> str:
    """Estrae la categoria dalle NOTE: [Hotel], [Ristorante], [Bar], etc."""
    if not note:
        return "Attivita"
    m = re.search(r"\[(\w+(?:\s+\w+)*)\]", note)
    if m:
        cat = m.group(1)
        # Normalizza
        cat_lower = cat.lower()
        if "hotel" in cat_lower or "albergo" in cat_lower:
            return "Hotel"
        elif "ristorante" in cat_lower or "trattoria" in cat_lower or "pizzeria" in cat_lower:
            return "Ristorante"
        elif "bar" in cat_lower or "cafe" in cat_lower or "caffe" in cat_lower:
            return "Bar"
        return cat
    return "Attivita"


def normalize_phone(phone: str) -> str:
    """Normalizza il numero di telefono in formato E.164 (+39...)."""
    if not phone:
        return ""
    # Rimuovi spazi, trattini, punti
    clean = re.sub(r"[\s\-\.\/\(\)]", "", phone.strip())
    # Se inizia con 00, sostituisci con +
    if clean.startswith("00"):
        clean = "+" + clean[2:]
    # Se non inizia con +, aggiungi +39
    if not clean.startswith("+"):
        clean = "+39" + clean
    return clean


def is_valid_phone(phone: str) -> bool:
    """Verifica che il numero sia valido (almeno 10 cifre dopo +39)."""
    if not phone or not phone.startswith("+39"):
        return False
    digits = re.sub(r"\D", "", phone)
    return len(digits) >= 11  # 39 + almeno 9 cifre


def is_already_called(row) -> bool:
    """Verifica se la riga ha gia una data di chiamata o un appuntamento."""
    if len(row) > COL_DATA_CHIAMATA and row[COL_DATA_CHIAMATA].strip():
        return True
    if len(row) > COL_DATA_APPUNTAMENTO and row[COL_DATA_APPUNTAMENTO].strip():
        return True
    return False


def safe_get(row, col, default=""):
    """Accesso sicuro a una colonna della riga."""
    if col < len(row):
        return row[col].strip()
    return default


# ============================================================================
# ELEVENLABS BATCH CALLING
# ============================================================================

def submit_batch(call_name: str, recipients: list) -> dict:
    """Invia un batch di chiamate a ElevenLabs."""
    url = f"{ELEVENLABS_BASE_URL}/v1/convai/batch-calling/submit"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "call_name": call_name,
        "agent_id": CULLIGAN_AGENT_ID,
        "agent_phone_number_id": PHONE_NUMBER_ID,
        "recipients": recipients,
        "target_concurrency_limit": CONCURRENCY,
        "telephony_call_config": {
            "ringing_timeout_secs": 60
        },
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def build_recipient(phone: str, nome_azienda: str, categoria: str,
                     nome_titolare: str, indirizzo: str, note: str) -> dict:
    """Costruisce un recipient per il batch con le dynamic_variables del prompt."""
    return {
        "phone_number": phone,
        "conversation_initiation_client_data": {
            "dynamic_variables": {
                "nome_azienda": nome_azienda,
                "categoria": categoria.lower(),
                "citta": "Bolzano",
                "nome_titolare": nome_titolare,
                "indirizzo": indirizzo,
                "note_extra": note,
            }
        }
    }


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Culligan Batch Caller")
    parser.add_argument("--dry-run", action="store_true", help="Mostra cosa farebbe senza chiamare")
    parser.add_argument("--limit", type=int, default=DEFAULT_BATCH_LIMIT,
                        help=f"Max chiamate per batch (0 = tutte, default {DEFAULT_BATCH_LIMIT})")
    parser.add_argument("--skip-confirm", action="store_true", help="Non chiedere conferma")
    args = parser.parse_args()

    mode = "DRY RUN" if args.dry_run else "LIVE"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"\n{'='*60}")
    print(f"CULLIGAN BATCH CALLER [{mode}] - {now}")
    print(f"{'='*60}")

    # 1. Leggi il foglio
    print("\nLettura foglio Google...")
    service = get_sheets_service()
    rows = read_all_rows(service)

    if not rows or len(rows) < 2:
        print("Foglio vuoto o solo header!")
        return

    header = rows[0]
    data_rows = rows[1:]
    print(f"  Righe totali: {len(data_rows)}")

    # 2. Filtra righe da chiamare
    to_call = []
    skipped_called = 0
    skipped_phone = 0

    for i, row in enumerate(data_rows):
        row_num = i + 2  # 1-based, +1 per header

        # Gia chiamata?
        if is_already_called(row):
            skipped_called += 1
            continue

        # Telefono valido?
        raw_phone = safe_get(row, COL_TELEFONO)
        phone = normalize_phone(raw_phone)
        if not is_valid_phone(phone):
            skipped_phone += 1
            continue

        nome_azienda = safe_get(row, COL_NOME_AZIENDA)
        nome_titolare = safe_get(row, COL_NOME_TITOLARE)
        note = safe_get(row, COL_NOTE)
        indirizzo = safe_get(row, COL_INDIRIZZO)
        categoria = extract_categoria(note)

        to_call.append({
            "row_num": row_num,
            "row_index": i + 1,  # 0-based (incl header)
            "phone": phone,
            "nome_azienda": nome_azienda,
            "nome_titolare": nome_titolare,
            "categoria": categoria,
            "indirizzo": indirizzo,
            "note": note,
        })

    print(f"  Gia chiamate: {skipped_called}")
    print(f"  Telefono mancante/invalido: {skipped_phone}")
    print(f"  Da chiamare: {len(to_call)}")

    if not to_call:
        print("\nNessuna azienda da chiamare!")
        return

    # 3. Applica limite
    if args.limit > 0:
        batch = to_call[:args.limit]
    else:
        batch = to_call

    print(f"\n  Batch da lanciare: {len(batch)} chiamate")
    print(f"  Agente: Marco - Culligan Bolzano HoReCa")
    print(f"  Telefono: +390554652406 (SIP Telnyx)")
    print()

    # 4. Mostra anteprima
    for item in batch:
        cat_tag = f"[{item['categoria']}]"
        print(f"  {item['row_num']:3d}. {item['nome_azienda']:<35} {cat_tag:<15} {item['phone']}")

    if args.dry_run:
        print(f"\n[DRY RUN] Nessuna chiamata lanciata.")
        return

    # 5. Conferma
    if not args.skip_confirm:
        print()
        confirm = input(f"Lanciare {len(batch)} chiamate? [s/N] ").strip().lower()
        if confirm not in ("s", "si", "y", "yes"):
            print("Annullato.")
            return

    # 6. Costruisci recipients
    recipients = []
    for item in batch:
        recipients.append(build_recipient(
            phone=item["phone"],
            nome_azienda=item["nome_azienda"],
            categoria=item["categoria"],
            nome_titolare=item["nome_titolare"],
            indirizzo=item["indirizzo"],
            note=item["note"],
        ))

    # 7. Invia batch
    batch_name = f"Culligan-Bolzano-{datetime.now().strftime('%Y%m%d-%H%M')}"
    print(f"\nInvio batch '{batch_name}' con {len(recipients)} destinatari...")

    try:
        result = submit_batch(batch_name, recipients)
        batch_id = result.get("batch_call_id", result.get("id", "?"))
        print(f"  Batch inviato! ID: {batch_id}")
        print(f"  Status: {result.get('status', '?')}")
    except requests.exceptions.HTTPError as e:
        print(f"  ERRORE API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  Response: {e.response.text[:500]}")
        return
    except Exception as e:
        print(f"  ERRORE: {e}")
        return

    # 8. Segna le righe come chiamate
    oggi = datetime.now().strftime("%d/%m/%Y")
    print(f"\nAggiornamento foglio (data: {oggi})...")
    for item in batch:
        try:
            mark_called(service, item["row_index"], oggi)
            time.sleep(0.3)  # Rate limit Google API
        except Exception as e:
            print(f"  WARN: Non riesco a segnare riga {item['row_num']}: {e}")

    print(f"\nDone! {len(batch)} chiamate lanciate, foglio aggiornato.")
    print(f"Batch ID: {batch_id}")
    print(f"Monitora su: https://elevenlabs.io/app/conversational-ai/batch-calling")


if __name__ == "__main__":
    main()
