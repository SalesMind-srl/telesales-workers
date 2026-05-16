# Telesales Cloudflare Workers Backend

Phase 1: FastAPI → Cloudflare Workers migration

## Setup

### Prerequisites
- Cloudflare account with API token
- GitHub repo (nostor)
- Node.js 18+ (for local development)
- ElevenLabs, Anthropic API keys

### Installation

```bash
npm install
```

### Environment Variables

Create `.env.local` for local development:

```bash
ELEVENLABS_API_KEY=xxx
ANTHROPIC_API_KEY=xxx
GOOGLE_SHEETS_API_KEY=xxx
```

Add GitHub secrets:
- `CLOUDFLARE_API_TOKEN` (from Cloudflare dashboard)
- `CLOUDFLARE_ACCOUNT_ID` (from Cloudflare dashboard)
- `ELEVENLABS_API_KEY`
- `ANTHROPIC_API_KEY`
- `GOOGLE_SHEETS_API_KEY`

### Local Development

```bash
npm run dev
```

Visit `http://localhost:8787`

### Deploy

```bash
npm run deploy
```

Or push to GitHub main branch for auto-deploy.

## Endpoints

- `GET /health` — Health check + scheduler status
- `GET /batches` — List recent batches
- `POST /process/{batch_id}` — Manual batch processing
- `GET /stats` — Overall KPIs
- `POST /internal/check` — Cron trigger (internal)

## Architecture

- **Runtime**: Cloudflare Workers (edge)
- **Storage**: Cloudflare KV (state + cache)
- **Scheduler**: Cloudflare Cron Trigger (every 5 min)
- **Routing**: Hono.js
- **APIs**: ElevenLabs, Google Sheets, Claude

## Flow

1. Cron fires every 5 minutes → calls `POST /internal/check`
2. Handler fetches completed batches from ElevenLabs
3. Extracts analysis (interest_level, appointment_scheduled, etc.)
4. Appends results to Google Sheets (via queue in KV)
5. Marks batch as processed (idempotency)
6. Updates stats in KV

## Monitoring

- Cloudflare dashboard: Workers analytics
- KV usage: batch state, processed list, stats
- Logs: `wrangler tail` for real-time logs

## Rollback

If needed, switch DNS back to Railway:
```bash
# Keep Workers paused for 1 week parallel
# Monitor KV + Sheets for consistency
# If stable: dismiss Railway
```

## Phase 2 (Next)

- [ ] Dashboard Next.js on Cloudflare Pages
- [ ] Google Sheets API proper integration
- [ ] Prompt optimizer (Claude) integration
- [ ] Callback handling

---

**Status**: Week 1 ✅ (Setup + Core endpoints)
**Next**: Week 2 (EL + Sheets integration)
