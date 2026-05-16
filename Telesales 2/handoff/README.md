# Handoff: Telesales — Piattaforma AI Completa

## Overview
Telesales è una piattaforma SaaS B2B italiana con 10 moduli AI per automatizzare reparti aziendali interi: AI Voice commerciale, CRM, outreach omnicanale, HR screening, scraping globale, eventi, prodotti digitali, fundraising, finanza agevolata.

Questo pacchetto contiene:
1. **Landing page** marketing (`landing/Landing.html`) — sito pubblico con Marco AI simulato
2. **Console app** operativa (`app/App.html`) — 12 moduli funzionali con command palette, drawer, toast
3. **Sales Kit** deck 14 slide (`sales-kit/Sales-Kit.html`) — pitch commerciale PDF-ready
4. **Portale** (`index.html`) — entry-point con link ai 3 artefatti
5. **Listino prezzi** A4 PDF (`Listino-Prezzi-2026.html`)

> ⚠️ I file HTML sono **design reference ad alta fedeltà** (hifi). Il compito di Claude Code è ricreare questi design nel codebase di produzione usando il framework scelto (consigliato: **Next.js 14 App Router + Tailwind CSS + shadcn/ui**) e collegarli a backend reali.

---

## Fidelity
**HIGH-FIDELITY** — pixel-accurate per colori, tipografia, spacing, animazioni, interazioni. Il developer deve replicare pixel-perfect usando il design system descritto sotto.

---

## Design System

### Palette colori
```
--ink-0:    #07070a   (bg più scuro)
--ink-1:    #0d0e12   (bg pannelli)
--ink-2:    #15161c   (bg card)
--ink-3:    #1d1e26   (bg input, hover)
--gold-1:   #c39446
--gold-2:   #d4af6a   (accent principale)
--gold-3:   #f5e7a8   (highlight)
--blue-1:   #1e3a8a
--blue-2:   #3b5fb8
--blue-3:   #5a7fb0
--fg:       #ececf1   (testo principale)
--fg-soft:  #c2c3cb   (testo secondario)
--fg-dim:   #8a8b94   (testo terziario)
--live:     #22c55e   (verde live/success)
--line:     rgba(255,255,255,.08)
--line-gold: rgba(212,175,106,.25)
```

### Tipografia
```
Display:  Fraunces (Google Fonts) — weight 300/400, italic per enfasi
Sans:     Geist (Vercel) — weight 300/400/500/600/700
Mono:     JetBrains Mono — weight 400/500, per dati/metriche/KPI
```

### Spacing & radii
```
--r-sm: 6px | --r-md: 10px | --r-lg: 18px | --r-xl: 28px | --r-pill: 999px
```

### Shadows
```
card: 0 20px 40px -20px rgba(0,0,0,.5)
gold-glow: 0 10px 24px -10px rgba(212,175,106,.55)
```

---

## Architettura produzione consigliata

```
tech-stack:
  frontend:    Next.js 14 (App Router) + TypeScript
  styling:     Tailwind CSS + shadcn/ui (dark theme)
  state:       Zustand + React Query (TanStack)
  realtime:    Supabase Realtime / Pusher
  auth:        Clerk o Supabase Auth
  db:          Supabase (PostgreSQL)
  ai-voice:    Twilio + VAPI (https://vapi.ai) per Marco
  ai-llm:      Anthropic Claude claude-haiku-4-5 (già integrato nella landing con window.claude)
  email:       Resend per transazionali + Formspree per il form demo
  billing:     Stripe
  deployment:  Vercel (frontend) + Supabase (backend)
  scraping:    Apify (https://apify.com) per Lead Founder AI
  calendar:    Cal.com per appointment booking
```

---

## Struttura pagine / routes

### 1. Landing pubblica — `/`
**File riferimento:** `landing/Landing.html`

**Sezioni in ordine:**
1. **NAV** — logo + link anchor + lang switch IT/EN + CTA "Prenota demo"
2. **HERO** — headline display 3 righe + waveform animato (canvas/CSS) + 4 KPI + 2 CTA
3. **TRUST** — marquee aziende italiane (CSS animation)
4. **STATS** — 4 celle count-up (IntersectionObserver + requestAnimationFrame)
5. **BENTO 9 prodotti** — CSS Grid 6 colonne, card "AI Voice" hero (span 3×2), 8 standard (span 2)
6. **MARCO DEMO** — widget chat AI con Claude (già funzionante, vedere JS landing)
7. **"MARCO TI CHIAMA"** — form numero telefono → conversazione live Claude API
8. **PROCESS** — 3 step + pilot include list
9. **FAQ** — accordion (solo CSS/JS vanilla)
10. **BOOKING** — form 2 colonne → Formspree/Resend
11. **FOOTER** — link, legal, lang switch

**Interazioni chiave:**
- Marco chat: Claude API, system prompt "sei Marco Ferretti AI commerciale Telesales"
- "Marco ti chiama": inserisci numero → conversazione in-page con Claude
- Form booking: POST a Formspree ID (config in env) o Resend
- Tweaks panel: palette/theme/hero variant, persistiti in localStorage
- IT/EN: i18n senza librerie, oggetto I18N con tutte le chiavi (vedere `landing/Landing.html`)
- Count-up numeri: IntersectionObserver, easing cubica

---

### 2. App console — `/app`
**File riferimento:** `app/App.html`

**Protetta da auth** (Clerk/Supabase Auth, redirecta a `/login` se non autenticato)

**12 moduli (routes nested):**

| Route | Modulo | Dati |
|-------|--------|------|
| `/app` | Dashboard | KPI aggregati, chiamate live, waveform, transcript |
| `/app/calls` | Chiamate | Tabella con filtri, stato live |
| `/app/agents` | Agenti AI | Configurazione agenti voce |
| `/app/pipeline` | Pipeline | Kanban 5 stage drag-n-drop |
| `/app/outreach` | Outreach AI | Flow 7 step, compositor Claude |
| `/app/crm` | CRM War Room | Tabella contatti, search, drawer scheda |
| `/app/scraping` | Lead Founder AI | Mappa SVG, stream live Supabase Realtime |
| `/app/products` | Product Maker AI | Catalogo prodotti digitali |
| `/app/events` | Eventia | Calendario eventi, fill rate |
| `/app/investors` | Investor Founder | Lista fondi con fit score |
| `/app/hr` | Talentia | Posizioni aperte, shortlist candidati, transcript AI |
| `/app/bandi` | PA Winner | Lista bandi con match score, drawer dossier |

**Sistema UX comune (da replicare in ogni modulo):**
- **Command Palette** (`⌘K`): 17+ comandi cercabili (vedere JS app)
- **Toast** (top-right): confirm actions, errors, success
- **Drawer** (slide-in right, 520px): form per ogni azione primaria
- **Sidebar** (260px sticky): nav modulare, logo, kbd shortcuts 1-0

**Ogni drawer ha:**
- Overlay backdrop blur
- Titolo + subtitle
- Form fields (input/select/textarea con styling specifico)
- 2 CTA: ghost (annulla) + primary (conferma)
- Chiude on backdrop click o ESC

---

### 3. Sales Kit — `/sales-kit`
**File riferimento:** `sales-kit/Sales-Kit.html`

14 slide con `deck-stage.js` (web component già incluso). In produzione può restare come HTML statico su Vercel. Per PDF → `window.print()`.

---

### 4. Listino prezzi — `/listino`
**File riferimento:** `Listino-Prezzi-2026.html`

2 pagine A4 dark, auto-print on load. Staticizzare su Vercel.

---

## Integrazioni critiche da implementare

### A) Marco AI Voice — VAPI
```typescript
// config vapi
const vapi = new Vapi(process.env.VAPI_API_KEY);
const call = await vapi.calls.create({
  assistantId: process.env.VAPI_MARCO_ASSISTANT_ID,
  customer: { number: '+39' + phoneNumber }
});
```
Passi:
1. Creare account VAPI (vapi.ai)
2. Creare assistente "Marco Ferretti" con voice ElevenLabs italiana
3. System prompt: vedi `window.MARCO_SCRIPT` in `landing/Landing.html`
4. Sostituire il simulatore in-page con vera chiamata VAPI

### B) Form demo — Resend
```typescript
// POST /api/booking
import { Resend } from 'resend';
const resend = new Resend(process.env.RESEND_API_KEY);
await resend.emails.send({
  from: 'Marco <marco@telesales.it>',
  to: ['nicco@telesales.it'],
  subject: `Demo richiesta: ${nome} ${cognome} - ${az}`,
  html: `<p>Nome: ${nome} ${cognome}</p><p>Email: ${email}</p><p>Tel: ${tel}</p><p>Azienda: ${az}</p>`
});
```
Oppure usare Formspree free tier: `https://formspree.io/f/{ID}` — già configurato nella landing, basta sostituire `SOSTITUISCI_CON_TUO_ID`.

### C) Database — Supabase schema minimo
```sql
-- Contatti CRM
create table contacts (
  id uuid primary key default gen_random_uuid(),
  nome text, cognome text, email text, tel text,
  azienda text, ruolo text, stato text default 'cold',
  score int default 0, note text,
  owner_id uuid references auth.users,
  created_at timestamptz default now()
);

-- Chiamate
create table calls (
  id uuid primary key default gen_random_uuid(),
  contact_id uuid references contacts,
  agent_name text, direction text,
  duration_sec int, status text,
  transcript text, sentiment float,
  created_at timestamptz default now()
);

-- Bandi
create table bandi (
  id uuid primary key default gen_random_uuid(),
  titolo text, ente text, tipo text,
  importo_max int, scadenza date,
  fit_score int, match bool,
  created_at timestamptz default now()
);

-- Candidati HR
create table hr_candidates (
  id uuid primary key default gen_random_uuid(),
  nome text, ruolo text, fit_score int,
  call_duration text, transcript text,
  stato text default 'shortlist',
  created_at timestamptz default now()
);
```

### D) Scraping live stream — Supabase Realtime
```typescript
// Client
const channel = supabase.channel('scraping-stream')
  .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'scraped_contacts' },
    (payload) => addToStream(payload.new))
  .subscribe();
```

---

## Environment variables
```bash
# .env.local
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
RESEND_API_KEY=
VAPI_API_KEY=
VAPI_MARCO_ASSISTANT_ID=
STRIPE_SECRET_KEY=
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
FORMSPREE_ID=
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=
CLERK_SECRET_KEY=
ANTHROPIC_API_KEY=   # per Marco chat in-page
```

---

## Assets inclusi
- `assets/logo-telesales-white.png` — logo bianco PNG trasparente (1136×277px)
- `assets/logo-telesales-gold.png` — logo oro PNG trasparente
- `linkedin-banner-final.png` — banner LinkedIn 1584×396px

---

## File di design reference
```
index.html                  → portale navigazione
landing/Landing.html        → landing completa (2055 righe, tutto inline)
landing/styles.css          → CSS design system (830 righe)
landing/app.js              → JS interazioni landing
landing/i18n.js             → stringhe IT/EN
app/App.html                → console completa (2757 righe, tutto inline)
sales-kit/Sales-Kit.html    → deck 14 slide
Listino-Prezzi-2026.html    → listino A4 2 pagine
dist/                       → bundle standalone offline (pronti per Netlify drop)
```

---

## Deployment Vercel (5 minuti)
```bash
# 1. Init Next.js
npx create-next-app@latest telesales --typescript --tailwind --app

# 2. Installa deps
npm install @clerk/nextjs @supabase/supabase-js resend stripe zustand @tanstack/react-query

# 3. Installa shadcn dark
npx shadcn@latest init  # scegli dark, zinc, CSS variables

# 4. Deploy
vercel --prod
```

---

## Priorità implementazione consigliata
1. **Setup Next.js + auth Clerk** — proteggere `/app/*`
2. **Landing** — statica con form Resend (il JS vanilla può restare)
3. **Dashboard + Chiamate** — connettere Supabase, dati reali
4. **Marco AI Voice** — VAPI integration (highest business value)
5. **CRM** — CRUD completo su Supabase
6. **Outreach AI** — integrazione Resend per sequenze
7. **Lead Founder AI** — Apify webhook → Supabase Realtime
8. **HR AI (Talentia)** — chiamate VAPI per screening
9. **PA Winner (Bandi)** — scraping manuale + Supabase
10. **Investor Founder** — database fondi manuale + matching

---

## Note su Marco chat (landing)
La landing usa `window.claude.complete()` — un helper built-in dell'ambiente Claude design che **non funziona in produzione**. In produzione:
```typescript
// /api/marco/route.ts
import Anthropic from '@anthropic-ai/sdk';
const client = new Anthropic();
export async function POST(req: Request) {
  const { messages } = await req.json();
  const msg = await client.messages.create({
    model: 'claude-haiku-4-5',
    max_tokens: 300,
    system: 'Sei Marco Ferretti, AI commerciale di Telesales.it...',
    messages
  });
  return Response.json({ text: msg.content[0].text });
}
```

---

*Handoff generato il 28 aprile 2026 — Telesales.it*
