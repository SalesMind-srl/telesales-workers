#!/usr/bin/env python3
"""
Costruisce il dataset da APPENDERE al foglio Sebastiano.
Solo le 193 aziende NUOVE (non presenti nel suo foglio).
Colonne identiche al foglio Sebastiano:
NOME AZIENDE | NOME TITOLARE | NOTE | INDIRIZZO | TELEFONO | PRESENTE SI O NO | DATA DELLA CHIAMATA | DATA DELL'APPUNTAMENTO
"""

import csv
import re

def normalize_name(name):
    n = name.lower().strip()
    for prefix in ['ristorante ', 'hotel ', 'bar ', 'pizzeria ', 'osteria ',
                   'trattoria ', 'caffè ', 'caffe ', 'cafe ', 'gelateria ',
                   'pasticceria ', 'parkhotel ', 'design hotel ', 'restaurant ',
                   'wirtshaus ', 'gasthof ', 'albergo ']:
        if n.startswith(prefix):
            n = n[len(prefix):]
    n = re.sub(r'[^a-z0-9 ]', '', n)
    n = re.sub(r'\s+', ' ', n).strip()
    return n

def normalize_phone(phone):
    if not phone:
        return ""
    return re.sub(r'[^0-9]', '', phone)[-9:]

# Carica Sebastiano (per filtrare duplicati)
sebastiano_names = set()
sebastiano_phones = set()
with open('/Users/simocors/Desktop/telesales/culligan_sebastiano.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if not row['NOME AZIENDE'].strip():
            continue
        sebastiano_names.add(normalize_name(row['NOME AZIENDE']))
        phone = normalize_phone(row.get('TELEFONO', ''))
        if phone:
            sebastiano_phones.add(phone)

# Carica mio CSV
mio = []
with open('/Users/simocors/Desktop/telesales/aziende_bolzano_VERIFICATE.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        mio.append(row)

# Filtra: solo nuove (non in Sebastiano)
nuove = []
for m in mio:
    key_name = normalize_name(m['nome_azienda'])
    key_phone = normalize_phone(m['tel_aziendale'])

    # Skip se già in Sebastiano
    if key_name in sebastiano_names:
        continue
    if key_phone and key_phone in sebastiano_phones:
        continue

    # Match parziale (substring)
    skip = False
    for sn in sebastiano_names:
        if key_name and len(key_name) > 3 and len(sn) > 3:
            if key_name in sn or sn in key_name:
                skip = True
                break
    if skip:
        continue

    nuove.append(m)

print(f"📊 Aziende da aggiungere al foglio Sebastiano: {len(nuove)}")

# Costruisci righe nel formato Sebastiano
output_rows = []
for m in nuove:
    # NOME AZIENDE
    nome = m['nome_azienda']

    # NOME TITOLARE (proprietario verificato)
    titolare = m['proprietario']

    # NOTE: tipo + email + sito + tel diretto
    note_parts = [f"[{m['tipo']}]"]
    if m.get('email_aziendale'):
        note_parts.append(f"email: {m['email_aziendale']}")
    if m.get('sito_web'):
        note_parts.append(f"sito: {m['sito_web']}")
    if m.get('tel_diretto_proprietario'):
        note_parts.append(f"cell: {m['tel_diretto_proprietario']}")
    note = " | ".join(note_parts)

    # INDIRIZZO (rimuovo ", 39100 Bolzano" finale per allineare a Sebastiano)
    indirizzo = m['indirizzo'].replace(', 39100 Bolzano', '').replace(', Bolzano', '').strip()

    # TELEFONO (formato Sebastiano: senza +39, con spazio)
    tel = m['tel_aziendale'].replace('+39 ', '').strip()

    output_rows.append([
        nome,           # NOME AZIENDE
        titolare,       # NOME TITOLARE
        note,           # NOTE
        indirizzo,      # INDIRIZZO
        tel,            # TELEFONO
        '',             # PRESENTE SI O NO (vuoto)
        '',             # DATA DELLA CHIAMATA (vuoto)
        ''              # DATA DELL'APPUNTAMENTO (vuoto)
    ])

# Ordina per tipo per facilitare il lavoro
def tipo_priority(row):
    note = row[2].lower()
    if '[hotel]' in note: return 0
    if '[ristorante]' in note: return 1
    if '[bar]' in note: return 2
    return 3

output_rows.sort(key=lambda r: (tipo_priority(r), r[0].lower()))

# Salva come TSV per copy-paste in Google Sheets (TAB-separated = preserva colonne)
output_tsv = '/Users/simocors/Desktop/telesales/da_appendere_sebastiano.tsv'
with open(output_tsv, 'w', encoding='utf-8') as f:
    for row in output_rows:
        # Escape tab/newline e join con TAB
        cleaned = [str(c).replace('\t', ' ').replace('\n', ' ') for c in row]
        f.write('\t'.join(cleaned) + '\n')

# Salva anche CSV per debug
output_csv = '/Users/simocors/Desktop/telesales/da_appendere_sebastiano.csv'
with open(output_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['NOME AZIENDE', 'NOME TITOLARE', 'NOTE', 'INDIRIZZO', 'TELEFONO',
                     'PRESENTE SI O NO', 'DATA DELLA CHIAMATA', 'DATA DELL\'APPUNTAMENTO'])
    writer.writerows(output_rows)

print(f"✅ TSV salvato: {output_tsv}")
print(f"✅ CSV salvato: {output_csv}")
print(f"📋 Righe da incollare: {len(output_rows)}")

# Mostra prime 5 righe per verifica
print("\n📝 Prime 5 righe:")
for row in output_rows[:5]:
    print(f"  {row[0]:40s} | {row[1][:30]:30s} | {row[3][:30]:30s} | {row[4]}")
