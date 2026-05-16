# ClickFunnels Integration Spec — Mik Cosentino

Stack CRM identificato per Mik Cosentino:

- **ClickFunnels 2.0** (account `mgta.clickfunnels.com`) — funnel + CRM + email automation (qui vivono i 80-100k lead pre-vendita)
- **X-Mansion** (LMS proprietario) — solo post-vendita (membri corso). NON integrato direttamente dalla nostra campagna AI Voice.

Tutto quello sotto è basato sulla **API REST ufficiale ClickFunnels 2.0** documentata su `developers.myclickfunnels.com`.

---

## 1. API ClickFunnels 2.0 — fondamentali

### Base URL pattern

```
https://{workspace_subdomain}.myclickfunnels.com/api/v2/workspaces/{workspace_id}/...
```

Per Mik: `workspace_subdomain` = `mgta` (probabile, da confermare con Pier).

### Auth

Due metodi supportati:

1. **API Access Token** (più semplice — consigliato per il setup iniziale)
   - Pier lo genera in CF UI → Settings → API → "Create Access Token"
   - Header HTTP: `Authorization: Bearer {token}`
2. **OAuth 2.0** (per app commerciali multi-tenant — non necessario qui)

### Endpoint chiave usati nel nostro flusso

| Operazione | Metodo + Endpoint | Quando lo usiamo |
|---|---|---|
| Lista contatti | `GET /api/v2/workspaces/{id}/contacts` (filtrabile per tag) | Pull lead da chiamare |
| Dettaglio contatto | `GET /api/v2/contacts/{contact_id}` | Verifica info aggiornate |
| Update contatto | `PATCH /api/v2/contacts/{contact_id}` | Scrivere esito chiamata + custom attributes |
| Add tag a contatto | `POST /api/v2/contacts/{contact_id}/tags` | Marcare `AI_CHIAMATO`, `APP_FISSATO`, `OPT_OUT` |
| Custom attributes (campi custom) | `POST /api/v2/contacts/{id}/contact_custom_attributes` | Salvare `esito_ai_call`, `data_appuntamento`, `audio_url`, `note_ai` |
| Webhooks outgoing | `POST /api/v2/workspaces/{id}/webhooks/outgoing/endpoints` | Subscribe a eventi `contact.identified`, `contact.updated` |

### Eventi webhook outgoing rilevanti per noi

```
contact.identified        # quando un nuovo lead si iscrive a un funnel
contact.updated           # quando un lead viene aggiornato (es. tag aggiunta)
contact.tagged            # quando viene assegnato un tag specifico
order.created             # se vogliamo skippare lead che hanno già comprato
```

---

## 2. Tre opzioni di integrazione (in ordine di preferenza)

### ✅ Opzione A — "Plug-and-Play in 1 ora" (consigliata per partenza)

**Cosa serve a noi**: API Access Token + workspace_id da Pier.

**Flusso**:
1. Pier genera un API Access Token in CF UI (1 minuto, solo lui può)
2. Pier ci comunica: token, workspace_id, nome del tag "lead da chiamare" (es. `webinar_infobusiness_iscritto`)
3. Il nostro backend Python (estensione di `pipeline.py` esistente) gira un cron job ogni mattina:
   - `GET /contacts?filter[tag]=webinar_infobusiness_iscritto&filter[tag_not]=AI_CHIAMATO&filter[opt_in_marketing]=true`
   - Estrae N lead (es. 100/giorno)
   - Lancia batch ElevenLabs Sofia
4. Post-call (webhook in ingresso da ElevenLabs):
   - `POST /contacts/{id}/tags` con `AI_CHIAMATO` (sempre) + `APP_FISSATO` (se `appuntamento_fissato=true`) o `OPT_OUT` (se richiesto)
   - `POST /contacts/{id}/contact_custom_attributes` con:
     - `esito_ai_call` = high/medium/low/none
     - `data_appuntamento` = ISO 8601
     - `audio_url` = link MP3 ElevenLabs
     - `note_ai` = sintesi

**Pro**:
- 0 modifiche lato Pier oltre alla generazione del token (1 min)
- Cron job 100% controllato da noi (orari, batch size, retry)
- Audit log nostro

**Contro**:
- Polling vs real-time (latenza fino a 24h dal momento dell'iscrizione lead — irrilevante per lead già storici di 80-100k vecchi)

**Tempo go-live**: 1 giorno (8h dev sul nostro backend).

**Costo**: 0 software, solo nostro dev time.

---

### Opzione B — "Real-time via webhook outgoing CF" (consigliata a regime)

**Cosa serve a noi**: tutto della A + Pier configura webhook outgoing.

**Flusso**:
1. Setup iniziale A completato (token + script)
2. Pier crea webhook in CF UI:
   - Settings → API → Webhooks → New
   - Event: `contact.tagged` (su tag specifico tipo `da_richiamare_ai`)
   - URL: `https://telesales-backend.simocors.it/clickfunnels/webhook/mik` (lo esponiamo noi)
   - Headers: `X-CF-Secret: {shared secret}` per validazione
3. Quando Mik tagga un contatto come `da_richiamare_ai`, CF chiama immediatamente il nostro endpoint
4. Il nostro endpoint:
   - Valida la firma
   - Mette il lead in coda per chiamata (Redis/SQS o semplice tabella DB)
   - Risponde 200 immediatamente
5. Worker async preleva dalla coda, chiama via ElevenLabs
6. Esiti tornano come in opzione A

**Pro**:
- Real-time: appena Mik aggiunge un lead, parte chiamata entro minuti
- Zero polling, zero spreco di API calls
- Scalabile a 100k+ lead/mese

**Contro**:
- Serve nostro backend live 24/7 con endpoint HTTPS pubblico
- Serve Pier configuri webhook in CF UI (5 min — banale ma fuori dal nostro controllo)

**Tempo go-live**: +2 giorni dopo opzione A (esposizione endpoint + queue).

**Costo**: hosting endpoint (Railway/Render ~$10/mese, già attivo).

---

### Opzione C — "Workflow CF + webhook step" (più chirurgico)

Differenza con B: invece di webhook globale, usiamo un **Workflow di ClickFunnels** che ha lo step nativo "Webhook" interno.

**Flusso**:
1. Pier crea in CF UI un Workflow:
   - Trigger: contatto aggiunto a una specifica lista o con tag X
   - Step 1: Webhook → POST a `https://telesales-backend.simocors.it/cf/webhook/mik`
2. Tutto il resto identico a B

**Vantaggi sopra B**:
- Pier può gestire visualmente i criteri di "quando chiamare" in CF (es. solo lead iscritti da almeno 30 gg, escludere chi ha già comprato, ecc.) senza scrivere codice
- Più trasparenza per il team Mik: "vedo nel workflow quando partono le chiamate"

**Tempo go-live**: come B.

**Costo**: come B.

---

### Opzione D — "Zapier/Make middleware" (no-code, ma limitato)

**Cosa**: trigger Zapier/Make su evento CF → action: webhook → noi.

**Limiti Zapier ClickFunnels 2.0** (verificati): solo trigger `New Contact Activity`, `New Failed Purchase`, `New Successful Purchase` disponibili come trigger nativi. Per "contatto creato" o "tag aggiunta" servono webhook custom.

**Quando ha senso**: solo se Pier rifiuta di toccare CF API/Workflows (improbabile, è il tech lead).

**Costo**: Zapier Pro ~$30-50/mese o Make.com ~$10-20/mese.

**Recommendation**: SCONSIGLIATA. Aggiunge un intermediario inutile.

---

## 3. Pseudo-codice del backend nostro (Python — opzione A+B combinata)

```python
# pipeline_mik.py — estensione di pipeline.py esistente
import requests
from config import MIK_AGENT_ID
from elevenlabs_client import launch_batch_call

CF_BASE = "https://mgta.myclickfunnels.com/api/v2"
CF_WORKSPACE_ID = "TBD"  # da Pier
CF_TOKEN = os.getenv("CLICKFUNNELS_API_TOKEN")
HEADERS = {"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"}

def fetch_leads_to_call(tag="webinar_infobusiness_iscritto", limit=100):
    """Pull lead da chiamare — escludendo già chiamati e opt-out."""
    r = requests.get(
        f"{CF_BASE}/workspaces/{CF_WORKSPACE_ID}/contacts",
        headers=HEADERS,
        params={
            "filter[tag]": tag,
            "filter[tag_not]": "AI_CHIAMATO,OPT_OUT",
            "filter[opt_in_marketing]": True,
            "per_page": limit,
        },
    )
    r.raise_for_status()
    return r.json()["data"]

def update_contact_after_call(contact_id, data_collection, audio_url):
    """Scrivi esito AI call + tag su contatto CF."""
    # 1. Custom attributes
    requests.post(
        f"{CF_BASE}/contacts/{contact_id}/contact_custom_attributes",
        headers=HEADERS,
        json={
            "esito_ai_call": data_collection["interest_level"],
            "data_appuntamento": data_collection.get("data_appuntamento"),
            "obiezione_principale": data_collection.get("obiezione_principale"),
            "audio_url": audio_url,
            "note_ai": data_collection.get("note_ai"),
        },
    )
    # 2. Tags
    tags = ["AI_CHIAMATO"]
    if data_collection.get("appuntamento_fissato"):
        tags.append("APP_FISSATO")
    if data_collection.get("opt_out_richiesto"):
        tags.append("OPT_OUT")
    for tag in tags:
        requests.post(
            f"{CF_BASE}/contacts/{contact_id}/tags",
            headers=HEADERS,
            json={"name": tag},
        )

# Webhook endpoint Flask/FastAPI (Opzione B)
@app.post("/clickfunnels/webhook/mik")
def cf_webhook():
    payload = request.json
    if request.headers.get("X-CF-Secret") != CF_WEBHOOK_SECRET:
        return abort(401)
    event = payload["event_type"]
    if event == "contact.tagged" and payload["data"]["tag"] == "da_richiamare_ai":
        contact = payload["data"]["contact"]
        launch_batch_call(
            agent_id=MIK_AGENT_ID,
            phone=contact["phone"],
            dynamic_vars={
                "nome_lead": contact["first_name"],
                "email_lead": contact["email"],
                "data_iscrizione": contact["custom_attributes"]["data_iscrizione"],
                "fonte_lead": contact["custom_attributes"]["fonte_lead"],
            },
        )
    return "", 200

# Webhook in arrivo da ElevenLabs (post-call)
@app.post("/elevenlabs/webhook/mik")
def el_webhook():
    payload = request.json
    cf_contact_id = payload["dynamic_vars"]["cf_contact_id"]
    update_contact_after_call(
        contact_id=cf_contact_id,
        data_collection=payload["data_collection"],
        audio_url=payload["recording_url"],
    )
    return "", 200
```

---

## 4. Custom attributes da chiedere a Pier di creare in CF

Per scrivere gli esiti via API ci servono questi custom attributes sul Contact (li crea Pier in CF UI → Contacts → Custom Attributes → New, oppure li creiamo noi via API):

| Nome attributo | Tipo | Esempio | Note |
|---|---|---|---|
| `esito_ai_call` | Text/Select | `high` / `medium` / `low` / `none` / `appointment` | Select consigliato |
| `data_appuntamento` | Text (ISO 8601) | `2026-05-20T17:00:00+02:00` | Text (CF non ha tipo datetime nativo) |
| `obiezione_principale` | Select | `tempo` / `soldi` / `scetticismo` / `gia_provato` / `nessuna` | |
| `audio_url` | Text | `https://api.elevenlabs.io/v1/convai/conversations/{id}/audio` | Link MP3 |
| `note_ai` | Text long | sintesi 1-2 frasi | |
| `data_ultimo_ai_call` | Text | `2026-05-15` | Per evitare ri-chiamate troppo frequenti |
| `setter_assegnato` | Text | nome consulente Mik che farà la call di approfondimento | |

E i tag necessari (CF gestisce tag automaticamente al primo uso):

```
da_richiamare_ai      # trigger per noi (lead pronto per chiamata)
AI_CHIAMATO           # noi dopo aver chiamato
APP_FISSATO           # appuntamento fissato (= sucesso primario)
OPT_OUT               # da escludere per sempre
```

---

## 5. X-Mansion — perché NON ci integriamo (per ora)

X-Mansion è LMS proprietario per i corsi acquistati. Nessuna API pubblica documentata.

**Quando potrebbe servirci**: post-vendita per tracciare se il lead chiamato → fissato appuntamento → comprato corso → attivato in X-Mansion. Questo loop completo è interessante per il ROI dimostrato a Mik, ma fuori scope per la **campagna di riattivazione** che gira al 100% sui lead PRE-vendita (ClickFunnels).

**Se Mik lo chiede**: "X-Mansion possiamo integrarlo in una fase 2 — ci servirà un'API custom esposta da Pier, oppure un export periodico di chi ha comprato per fare attribution. Non necessario per la prima campagna."

---

## 6. Sequenza setup completa (cosa diciamo a Pier in demo o appena dopo)

**Setup minimo per partire (Opzione A — 1 ora di lavoro distribuito)**:

1. **Pier**: in CF Settings → API → "Create Access Token" → manda token via canale sicuro
2. **Pier**: conferma `workspace_subdomain` (probabilmente `mgta`) e `workspace_id` numerico
3. **Pier**: conferma il nome del tag che identifica i lead "iscritto webinar Infobusiness Accelerator" (oppure ci dà il segment_id)
4. **Pier**: crea i 7 custom attributes elencati sopra (5 min in CF UI)
5. **Noi**: configuriamo `CLICKFUNNELS_API_TOKEN` env var in `config.py`
6. **Noi**: scriviamo `pipeline_mik.py` con le 3 funzioni `fetch_leads_to_call`, `update_contact_after_call`, webhook handler
7. **Noi**: smoke test su 5 contatti reali (anche del team Pier) prima di scalare

**Upgrade a real-time (Opzione B/C — extra 2 giorni)**:

8. **Noi**: esponiamo endpoint `https://telesales-backend.simocors.it/clickfunnels/webhook/mik`
9. **Pier**: configura webhook outgoing in CF UI puntando a quell'URL (oppure crea Workflow con step Webhook)
10. **Noi**: aggiungiamo coda async (Redis) per gestire spike di lead simultanei

---

## 7. Backup — se Pier dice "non vi do API token / non tocco CF"

Scenario poco probabile (Pier è il tech lead, capisce il valore), ma backup:

**Plan B**: Export CSV manuale settimanale da CF UI da parte di chiunque del team → upload manuale su nostro Google Sheet condiviso → noi processiamo. È esattamente l'**Opzione A** del piano demo "Zero tech, partiamo lunedì". Funziona, ma scala male oltre 5k lead/settimana.

**Plan C**: Zapier middleware se rifiutano sia API token che CSV manuale (ipotesi improbabile, ma copre il caso).

---

## 8. Risposte tecniche pronte a domande di Pier in demo

| Domanda di Pier | Risposta |
|---|---|
| "Quale auth supportate?" | API Access Token (consigliato) o OAuth 2.0 — entrambe documentate da ClickFunnels |
| "Quanti API calls fate al giorno?" | ~200 GET (pull) + ~100 PATCH/POST (write esiti) per 100 chiamate giornaliere. Sotto i limit standard CF |
| "Avete idempotency?" | Sì, tracciamo `conversation_id` ElevenLabs come idempotency key, evitando double-update |
| "Come gestite errori 5xx CF?" | Retry exponential backoff fino a 3 tentativi, poi alert al nostro on-call |
| "Storage audio chiamate?" | ElevenLabs ospita le registrazioni 90 gg. Possiamo mirror su S3 nostro se vuoi audit log permanente |
| "Privacy / GDPR?" | Pull solo contatti con `opt_in_marketing=true` in CF. Salviamo `OPT_OUT` tag se richiesto. Audio cancellati a 90gg |
| "Possiamo vedere il prompt prima?" | Sì, è in `prompts/mik_cosentino_infobusiness_v1.md` — ve lo passiamo, accesso completo, versionato |
| "Webhook secret per evitare spoofing?" | Sì, header `X-CF-Secret` con shared secret. Validato a ogni request |
| "Esiti scritti dove esattamente?" | 7 custom attributes su Contact + 4 tag (`AI_CHIAMATO`, `APP_FISSATO`, `OPT_OUT`, opzionale `INTERESSATO`) |

---

## Recap — cosa diciamo a Mik in demo sull'integrazione

> "Mik, abbiamo già mappato che usate ClickFunnels 2.0. La loro API è solida e documentata. Vi propongo 3 modi di integrarci, scegliete voi:
>
> **A** — Pier ci dà un API token, noi facciamo tutto polling: zero modifiche da parte vostra. Partiamo lunedì.
>
> **B** — Pier configura un webhook outgoing in CF UI verso il nostro endpoint: real-time. 5 minuti di lavoro suo + 2 giorni nostri. Live entro la settimana.
>
> **C** — Pier crea un Workflow CF nativo con step webhook: stessa cosa di B ma più visibile per voi nella UI ClickFunnels.
>
> Mia raccomandazione: partiamo con A lunedì, switchiamo a C entro fine mese quando il flusso è rodato.
>
> **X-Mansion** non lo tocchiamo in questa campagna — lì stanno i clienti dopo che hanno comprato, a noi servono i lead prima del corso, che sono tutti in ClickFunnels."

---

**Sources**:
- [ClickFunnels Developer Hub](https://developers.myclickfunnels.com/docs/intro)
- [ClickFunnels Webhooks Guide](https://developers.myclickfunnels.com/docs/webhooks)
- [ClickFunnels API & Webhooks features](https://www.clickfunnels.com/features/api-and-webhooks)
- [Workflow Webhook Step](https://support.myclickfunnels.com/support/solutions/articles/150000156983-using-the-webhook-step-in-a-workflow)
- [ClickFunnels Getting Started](https://developers.myclickfunnels.com/docs/getting-started)
- [Custom Attributes](https://support.myclickfunnels.com/docs/how-to-add-and-manage-contact-attributes-1)
