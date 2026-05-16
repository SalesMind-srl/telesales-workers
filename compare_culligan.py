#!/usr/bin/env python3
"""
Comparazione tra:
- Foglio Sebastiano Culligan (58 aziende)
- CSV verificato da Claude (224 aziende)

Trova: duplicati, nuovi nel mio CSV, nuovi nel foglio Sebastiano
"""

import csv
import re
from collections import defaultdict

def normalize_name(name):
    """Normalizza nome per matching"""
    n = name.lower().strip()
    # Rimuovi prefissi comuni
    for prefix in ['ristorante ', 'hotel ', 'bar ', 'pizzeria ', 'osteria ',
                   'trattoria ', 'caffè ', 'caffe ', 'cafe ', 'gelateria ',
                   'pasticceria ', 'parkhotel ', 'design hotel ', 'restaurant ',
                   'wirtshaus ', 'gasthof ', 'albergo ']:
        if n.startswith(prefix):
            n = n[len(prefix):]
    # Rimuovi caratteri speciali
    n = re.sub(r'[^a-z0-9 ]', '', n)
    n = re.sub(r'\s+', ' ', n).strip()
    return n

def normalize_phone(phone):
    """Normalizza telefono"""
    if not phone:
        return ""
    return re.sub(r'[^0-9]', '', phone)[-9:]  # ultime 9 cifre

# Carica foglio Sebastiano
sebastiano = []
with open('/Users/simocors/Desktop/telesales/culligan_sebastiano.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if not row['NOME AZIENDE'].strip():
            continue
        sebastiano.append({
            'nome': row['NOME AZIENDE'].strip(),
            'titolare': row.get('NOME TITOLARE', '').strip(),
            'note': row.get('NOTE', '').strip(),
            'indirizzo': row.get('INDIRIZZO', '').strip(),
            'telefono': row.get('TELEFONO', '').strip(),
            'presente': row.get('PRESENTE SI O NO', '').strip(),
            'data_chiamata': row.get('DATA DELLA CHIAMATA', '').strip(),
            'data_appuntamento': row.get('DATA DELL\'APPUNTAMENTO', '').strip(),
            '_key_name': normalize_name(row['NOME AZIENDE']),
            '_key_phone': normalize_phone(row.get('TELEFONO', ''))
        })

# Carica mio CSV
mio = []
with open('/Users/simocors/Desktop/telesales/aziende_bolzano_VERIFICATE.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        mio.append({
            'nome': row['nome_azienda'],
            'tipo': row['tipo'],
            'indirizzo': row['indirizzo'],
            'telefono': row['tel_aziendale'],
            'email': row.get('email_aziendale', ''),
            'sito': row.get('sito_web', ''),
            'proprietario': row.get('proprietario', ''),
            'tel_diretto': row.get('tel_diretto_proprietario', ''),
            '_key_name': normalize_name(row['nome_azienda']),
            '_key_phone': normalize_phone(row['tel_aziendale'])
        })

print(f"📊 STATS:")
print(f"  Foglio Sebastiano: {len(sebastiano)} aziende")
print(f"  Mio CSV verificato: {len(mio)} aziende")

# Trova DUPLICATI (nome simile o telefono uguale)
duplicati = []
sebastiano_keys_name = {s['_key_name']: s for s in sebastiano}
sebastiano_keys_phone = {s['_key_phone']: s for s in sebastiano if s['_key_phone']}
mio_keys_name = {m['_key_name']: m for m in mio}
mio_keys_phone = {m['_key_phone']: m for m in mio if m['_key_phone']}

# Aziende nel foglio Sebastiano che SONO nel mio CSV
in_entrambi = []
solo_sebastiano = []
for s in sebastiano:
    matched = None
    # Match per nome
    if s['_key_name'] in mio_keys_name:
        matched = mio_keys_name[s['_key_name']]
    # Match per telefono
    elif s['_key_phone'] and s['_key_phone'] in mio_keys_phone:
        matched = mio_keys_phone[s['_key_phone']]
    # Match parziale (substring)
    else:
        for mk, mv in mio_keys_name.items():
            if s['_key_name'] and (s['_key_name'] in mk or mk in s['_key_name']):
                if len(s['_key_name']) > 3 and len(mk) > 3:
                    matched = mv
                    break

    if matched:
        in_entrambi.append((s, matched))
    else:
        solo_sebastiano.append(s)

# Aziende nel mio CSV NON nel foglio Sebastiano
in_entrambi_keys = set()
for s, m in in_entrambi:
    in_entrambi_keys.add(m['_key_name'])

solo_mio = [m for m in mio if m['_key_name'] not in in_entrambi_keys]

print(f"\n📊 RISULTATI COMPARAZIONE:")
print(f"  ✅ In ENTRAMBI: {len(in_entrambi)}")
print(f"  🆕 Solo nel mio CSV (NUOVI per Sebastiano): {len(solo_mio)}")
print(f"  ⚠️  Solo nel foglio Sebastiano (MANCANTI nel mio): {len(solo_sebastiano)}")

# Mostra duplicati
print(f"\n✅ AZIENDE IN ENTRAMBI ({len(in_entrambi)}):")
for s, m in in_entrambi:
    extra = ""
    if m['proprietario'] and not s['titolare']:
        extra += f" [+ PROP: {m['proprietario']}]"
    if m['email'] and 'email' not in s['note'].lower():
        extra += f" [+ EMAIL: {m['email']}]"
    if m['sito']:
        extra += f" [+ SITO]"
    print(f"  • {s['nome']:40s} ↔ {m['nome']:40s}{extra}")

# Mostra aziende solo nel foglio Sebastiano (sono da aggiungere/verificare)
print(f"\n⚠️  AZIENDE SOLO NEL FOGLIO SEBASTIANO ({len(solo_sebastiano)}):")
for s in solo_sebastiano:
    titolare = f" [Titolare: {s['titolare']}]" if s['titolare'] else ""
    print(f"  • {s['nome']:40s} | {s['telefono']:18s}{titolare}")

# Mostra TOP nuove aziende del mio CSV (Hotel + Ristorante prima)
print(f"\n🆕 NUOVE AZIENDE NEL MIO CSV (non ancora chiamate) - TOP 30:")
solo_mio_sorted = sorted(solo_mio, key=lambda x: (x['tipo'], -len(x.get('proprietario', ''))))
for i, m in enumerate(solo_mio_sorted[:30]):
    prop = f" [P: {m['proprietario'][:40]}]" if m['proprietario'] else ""
    print(f"  {i+1:3d}. [{m['tipo']:11s}] {m['nome']:40s} | {m['telefono']:18s}{prop}")

# Salva output CSV
output = '/Users/simocors/Desktop/telesales/COMPARAZIONE_RISULTATI.csv'
with open(output, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['STATO', 'NOME', 'TIPO', 'TELEFONO', 'INDIRIZZO', 'PROPRIETARIO', 'EMAIL', 'SITO', 'NOTE_SEBASTIANO'])

    # In entrambi
    for s, m in in_entrambi:
        writer.writerow(['IN_ENTRAMBI', m['nome'], m['tipo'], m['telefono'], m['indirizzo'], m['proprietario'], m['email'], m['sito'], s['note']])

    # Solo nel foglio Sebastiano
    for s in solo_sebastiano:
        writer.writerow(['SOLO_SEBASTIANO', s['nome'], '', s['telefono'], s['indirizzo'], s['titolare'], '', '', s['note']])

    # Solo nel mio CSV (NUOVE)
    for m in solo_mio_sorted:
        writer.writerow(['NUOVA_DA_CHIAMARE', m['nome'], m['tipo'], m['telefono'], m['indirizzo'], m['proprietario'], m['email'], m['sito'], ''])

print(f"\n💾 CSV salvato: {output}")
print(f"📊 Totale righe: {len(in_entrambi) + len(solo_sebastiano) + len(solo_mio)}")
