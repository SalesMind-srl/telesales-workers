# Demo Mik Cosentino — Asset

Materiale per la demo che facciamo a Mik Cosentino (14-15 maggio 2026) dell'AI Voice per riattivazione lead Infobusiness Accelerator.

## File in questa cartella

| File | Cosa contiene | Quando usarlo |
|---|---|---|
| `lead_demo_mik.csv` / `.xlsx` | **50 lead fac-simile** (B2C italiano realistico, telefoni fittizi) | Mostrato a Mik come "database tipo" per fargli vedere come il prompt si personalizza |
| `lead_demo_team_telesales.csv` | **5 contatti team Telesales** (numeri veri da sostituire) | Per chiamate demo dal vivo durante la presentazione |
| `genera_lead_demo.py` | Script Python che rigenera i 50 lead | Rieseguire se servono altri dati o varianti |

## Schema colonne (per entrambi i CSV)

| Colonna | Esempio | Note |
|---|---|---|
| `id` | `MIK-DEMO-001` | ID univoco interno |
| `nome_lead` | `Marco` | → dynamic variable ElevenLabs |
| `cognome_lead` | `Rossi` | |
| `email_lead` | `marco.rossi@gmail.com` | → dynamic variable |
| `telefono_lead` | `+393331234567` | E.164, → SIP outbound |
| `data_iscrizione` | `15/03/2026` | → dynamic variable per personalizzare aggancio |
| `fonte_lead` | `Webinar Infobusiness Accelerator` | → dynamic variable, mostra che ricordiamo da dove vengono |
| `citta` / `provincia` | `Milano` / `MI` | Per eventuale personalizzazione geo |
| `eta` | `34` | |
| `sesso` | `M` / `F` | |
| `situazione_lavorativa` | `dipendente` | dipendente/freelance/imprenditore/disoccupato/studente/altro |
| `obiettivo_dichiarato_form` | `Aumentare il reddito mensile` | Risposta data al form di iscrizione |
| `consenso_whatsapp` | `si` / `no` | Per GDPR — chiamare solo se `si` |
| `consenso_marketing` | `si` | Tutti opt-in (sono in lista) |
| `ultimo_contatto` | `` (vuoto) | Mai ricontattati = riattivazione fredda |
| `note_storiche` | `` | Eventuale storico |

## Come usarlo nella demo

**Scenario A — Mostrare il database a Mik:**
1. Apri `lead_demo_mik.xlsx` su schermo
2. Spiega: "Questi sono 50 lead esemplificativi con la stessa struttura dei tuoi — nome, email, telefono, data iscrizione, fonte da cui è arrivato (webinar, lead magnet, ad)."
3. Mostra come il system prompt usa le variabili: aprire `prompts/mik_cosentino_infobusiness_v1.md` e indicare i `{{nome_lead}}`, `{{email_lead}}`, ecc.
4. Spiega: "Quando partiamo, l'AI legge ogni riga e personalizza: a Marco dice 'ti eri iscritto al webinar Infobusiness Accelerator il 23 settembre', a Camilla dice la sua data ecc. Ogni chiamata è diversa."

**Scenario B — Chiamata demo live:**
1. Apri `lead_demo_team_telesales.csv`
2. Sostituisci i `+39XXXXXXXXXX` con i numeri veri del team Telesales (Simone, Karima, Rebecca, Barbara)
3. Carica nella UI ElevenLabs come batch, lancia chiamate
4. Mik sente la voce in viva voce → vede personalizzazione in azione

## Note importanti

- **Telefoni dei 50 lead sono FITTIZI** — pattern E.164 plausibile ma non collegabile a persone reali. Non lanciare batch sul file `lead_demo_mik.csv` (chiamerebbero numeri inesistenti / random).
- **GDPR**: questi lead non esistono → nessun problema legale. Per i lead reali di Mik servirà verifica consensi.
- **Distribuzione realistica**: 60% webinar Infobusiness Accelerator, 15% lead magnet PDF, mix di età 22-60, mix M/F, mix città italiane, situazioni lavorative ponderate (35% dipendenti, 22% freelance, ecc.).

## Rigenerare i lead

```bash
cd /Users/simocors/Desktop/telesales/demo_mik
python3 genera_lead_demo.py
```

Output: rigenera CSV + XLSX con seed fisso 42 (cambia il seed nello script per dati diversi).
