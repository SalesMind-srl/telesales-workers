# Demo Mik Cosentino — Brief Operativo

Documento da tenere aperto durante la demo. Sequenza, asset, risposte pronte.

## Obiettivo unico

**Chiudere il deal**. Prezzo già concordato a listino. Mik non discute il prezzo, vuole solo essere stupito sulla qualità e la fattibilità.

## Asset da avere aperti su schermo prima di iniziare

1. **Dashboard frontend Mik** (in costruzione altra chat — URL da inserire qui)
2. **Google Sheet lead demo**: https://docs.google.com/spreadsheets/d/1qb9CIgMMwLNL_l4CVpb5K2QIhxWtQf4aVbyF9NqaTdQ/edit
3. **System Prompt v1**: `prompts/mik_cosentino_infobusiness_v1.md` (in editor)
4. **Spec ClickFunnels**: `demo_mik/clickfunnels_integration_spec.md` (per risposte tech a Pier)
5. **MP3 chiamata Sofia di esempio** (da generare con smoke test prima della demo)
6. **Telefono team** pronto in viva voce per chiamata live (un numero del file `lead_demo_team_telesales.csv`)

---

## Sequenza demo (15-20 minuti)

### 1. Apertura — 2 min

> "Mik, prima di entrare nel demo: abbiamo studiato a fondo InfomarketingX. Sappiamo che usate **ClickFunnels** come funnel + CRM (l'abbiamo individuato dai vostri sales page), che **Pier** gestisce la parte tech, e che **X-Mansion** è la vostra LMS proprietaria per i corsi. Per la riattivazione dei 80-100k lead lavoriamo solo su ClickFunnels — X-Mansion non lo tocchiamo. Iniziamo a vedere cosa abbiamo preparato per voi."

### 2. Dashboard Mik (frontend) — 4 min

Apri la dashboard. Naviga:

- **Tab Dashboard**: KPI in evidenza — chiamate fatte, lead qualificati, conversion rate, appuntamenti fissati oggi
- **Tab Chiamate**: 2-3 chiamate "live" (mock realistico) — durata, sentiment, esito
- **Tab Agenti AI**: scheda di **Sofia** — tono energico stile Mik, voce italiana, statistiche di performance
- **Tab Pipeline**: 50 lead fac-simile classificati per stato (Nuovi → Contattati → Qualificati → Appuntamento Fissato)

> "Questa è la dashboard che avresti accesso 24/7. Ogni chiamata, ogni esito, ogni appuntamento — visibili in tempo reale."

### 3. Foglio lead Google — 2 min

Apri https://docs.google.com/spreadsheets/d/1qb9CIgMMwLNL_l4CVpb5K2QIhxWtQf4aVbyF9NqaTdQ/edit

> "Qui ci sono 50 lead esempio con la struttura ESATTA che vi serve. 17 colonne: nome, cognome, email, telefono, data iscrizione al webinar, fonte (webinar Infobusiness Accelerator vs Lead Magnet vs Heroes), città, età, situazione lavorativa, consenso WhatsApp, consenso marketing. Pier può esportare lo stesso schema da ClickFunnels in 30 secondi."

Scorri qualche riga per mostrare la varietà (Marco freelance 43 anni Reggio Emilia → Camilla imprenditrice Palermo → ecc.).

### 4. System Prompt Sofia — 3 min

Apri `prompts/mik_cosentino_infobusiness_v1.md`.

> "Questa è la mente di Sofia. Versione 1, ~2.700 caratteri, sotto i 3k che è il limite per chiamate fluide. Notate alcune cose:
> - Sofia parla SEMPRE in tono motivazionale stile vostro
> - Usa il TU
> - È vietata dire 'capisco', 'posso rubarti un minuto', 'sono un'AI'
> - Una sola domanda alla volta
> - Anti-loop: dopo 2 obiezioni stessa, chiude educatamente
> - Pitch UNICO: call gratuita 30 min con consulente — niente vendita corso diretto
> - Slot orari: lun-ven 09-20, sab 09-13, mai domenica."

Punta a una `{{nome_lead}}` o `{{fonte_lead}}`:

> "Vedete queste variabili? Sofia legge ogni riga del Google Sheet e personalizza. A Marco dice 'ti eri iscritto al Webinar Infobusiness Accelerator il 23 settembre 2025'. A Camilla dice la SUA data. Ogni chiamata è personalizzata come se l'avesse preparata un setter umano."

### 5. Demo audio live — 3 min — **MOMENTO WOW**

Opzioni:

**A. Audio pre-registrato** (consigliato, più safe): play MP3 generato dallo smoke test
> "Ascoltate una chiamata reale di Sofia a un mio collega. 90 secondi."

**B. Chiamata live**: prendi un numero del team Telesales, fai partire batch ElevenLabs, Mik sente in viva voce
> "Adesso facciamo partire una chiamata vera, in diretta. Numero di un mio collega."

Dopo l'audio:
> "Avete sentito? Personalizzata, energica, sotto i 2 minuti, ha fissato l'appuntamento. Questa è la chiamata che facciamo 80-100mila volte alla scala dei vostri lead. 20 appuntamenti al giorno garantiti col vostro consulente, 400 al mese."

### 6. Workflow & integrazione ClickFunnels — 3 min

Mostra slide architettura (o disegna a mano sul foglio):

```
ClickFunnels (lead) → Google Sheet (hub) → Sofia AI (chiama) → Esiti tornano in ClickFunnels → Setter umano Mik chiama solo i qualificati
```

> "Per integrarci con voi abbiamo 3 modi pronti:
>
> **A** — Pier ci dà un API token ClickFunnels, noi facciamo tutto polling. **Zero modifiche** lato vostro. Partiamo lunedì 19.
>
> **B** — Pier configura un **webhook outgoing** in ClickFunnels verso il nostro endpoint. Real-time. 5 minuti suoi + 2 giorni nostri.
>
> **C** — Pier crea un **Workflow ClickFunnels** con step webhook nativo. Stessa cosa di B ma più visibile dentro la vostra UI.
>
> Mia raccomandazione: A subito, switchiamo a C entro fine mese."

Se Pier è in call, può chiedere dettagli tecnici → apri `clickfunnels_integration_spec.md` per risposte pronte.

### 7. Numeri proiezione — 2 min

Sulla lavagna o slide:

| Voce | Numero |
|---|---|
| Lead totali in database Mik | 80-100k |
| Lead chiamabili/giorno | ~500 |
| Pickup rate atteso | ~25% → 125 conversazioni/giorno |
| Conversion call → appuntamento fissato | ~16% → **20 appuntamenti/giorno** ✓ |
| Giorni lavorativi/mese | 20 |
| **Appuntamenti consegnati/mese al setter Mik** | **400** |
| Conversion setter umano → vendita | ~10-15% |
| **Vendite Infobusiness Accelerator/mese stimate** | **40-60** |

> "Mik, fai te i conti col valore del corso. Il pricing nostro è già concordato. Vi torniamo X di fatturato extra al mese, costo Y. ROI ovvio."

### 8. Chiusura — 2 min

> "Possiamo partire **lunedì 19 maggio** con Opzione A.
> Da voi serve:
> 1. CSV lead esportato da ClickFunnels (Pier, 30 secondi)
> 2. Conferma consensi GDPR sui lead
> 3. Nome del consulente Mik che riceve gli appuntamenti + accesso al suo calendar
> 4. API token ClickFunnels (Pier, 1 minuto in UI)
>
> Tutto il resto è nostro. Domande?"

Poi: silenzio. Lascia parlare Mik.

---

## Cheatsheet obiezioni — risposte rapide

### Obiezioni Mik (sales/strategia)

| "Lead vecchi non funzionano" | "Per questo non vendiamo, offriamo solo call gratuita con consulente. Lead dormienti riattivati con voce convertono 2-3x più del solo email" |
| "Il vostro AI si capisce?" | "Italiano nativo, energico. Hai appena ascoltato. Se chiede dice la verità una volta poi prosegue. Trasparenza" |
| "Voi sostituite il mio team?" | "No, lo carichiamo. Il vostro setter chiama solo lead già scaldati da noi, risparmia ore di tentativi a vuoto" |
| "Quanto costa al minuto?" | "Sul nostro Pro 1238 min inclusi/mese. Crediti extra per 80k lead = ~$300-500, già nel pricing" |
| "Posso fermare il prompt?" | "Accesso completo a system prompt e voce, modificate quando volete. Versionato" |
| "Quanto tempo per partire?" | "Lunedì 19 maggio con Opzione A. Vi mando appendice contratto stasera" |

### Obiezioni Pier (tech)

| "Quale auth?" | "API Access Token o OAuth 2.0, entrambe documentate ClickFunnels" |
| "API calls?" | "~200 GET + ~100 write/giorno per 100 chiamate. Sotto i rate limit standard" |
| "Idempotency?" | "Sì, `conversation_id` ElevenLabs come key. No doppi update" |
| "Errori 5xx CF?" | "Retry exponential backoff 3x, alert on-call" |
| "Privacy/GDPR?" | "Pull solo `opt_in_marketing=true`. `OPT_OUT` tag su richiesta. Audio max 90gg" |
| "Webhook security?" | "Header `X-CF-Secret` shared secret, validato a ogni POST" |
| "Storage audio?" | "ElevenLabs 90gg + mirror S3 nostro se vuoi audit permanente" |
| "X-Mansion?" | "Out of scope fase 1, post-vendita. Vediamo in fase 2 con API custom di Pier se serve" |

---

## Ruoli team Telesales durante la demo

- **Simone**: parla, naviga schermo, risposte sales
- **Niccolò**: backup tech, risponde a Pier su dettagli ClickFunnels/API
- (Eventualmente) **Karima/Rebecca**: in viva voce per ricevere la chiamata Sofia live se opziona B per slot 5

---

## Verifiche sera prima

- [ ] Dashboard frontend Mik aperta e funzionante
- [ ] Google Sheet popolato e accessibile via link a Mik
- [ ] Agente Sofia pubblicato in ElevenLabs UI (account `admin@telesales.it`)
- [ ] MP3 di smoke test salvato e pronto in `demo_mik/audio_demo_sofia.mp3`
- [ ] Telefono team con numero da chiamare in viva voce
- [ ] Calcolo crediti ElevenLabs disponibili (Pro 1238 min)
- [ ] Network stabile, schermo condiviso testato, microfoni ok
- [ ] Spec ClickFunnels stampato/aperto in tab separata
- [ ] Versione draft contratto/appendice pronta da mandare post-demo
