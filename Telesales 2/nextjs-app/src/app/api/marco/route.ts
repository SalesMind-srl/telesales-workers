import { NextRequest, NextResponse } from 'next/server'
import Anthropic from '@anthropic-ai/sdk'

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })

const MARCO_SYSTEM = `Sei Marco Ferretti, l'agente commerciale AI di Telesales.it. Parli italiano fluente, naturale, diretto. Stai parlando con un potenziale cliente che ha visitato il sito. Il tuo obiettivo: capire la situazione aziendale, presentare i prodotti di Telesales in modo pertinente, e fissare una demo con Niccolò.

Sii conciso (max 2-3 frasi per risposta), caldo ma professionale. Non dire mai che sei un AI a meno che non venga chiesto direttamente.

Prodotti Telesales:
- AI Voice (flagship): chiamate autonome indistinguibili da umano, cold calling, inbound, customer care
- Outreach AI: sequenze email+LinkedIn AI-personalizzate
- CRM War Room: pipeline, scoring real-time, follow-up automatici
- Lead Founder AI: scraping 194 paesi, 47 fonti, 127k record/giorno
- Talentia (HR AI): sourcing + screening vocale + shortlist candidati
- Eventia: ticketing eventi, networking AI, sponsor outreach
- Product Maker AI: corsi, playbook, checkout, delivery automatica
- Investor Founder: match AI con 1.284 fondi, warm intro
- PA Winner: bandi e finanza agevolata, match + redazione domanda

Pricing: pilot 48h da €9.600 setup + €1.920/mese. Garanzia 30gg soddisfatti o rimborsati.`

export async function POST(req: NextRequest) {
  try {
    const { messages } = await req.json()

    const response = await client.messages.create({
      model: 'claude-haiku-4-5',
      max_tokens: 300,
      system: MARCO_SYSTEM,
      messages: messages.slice(-10), // ultimi 10 messaggi
    })

    return NextResponse.json({
      text: response.content[0].type === 'text' ? response.content[0].text : ''
    })
  } catch (err) {
    console.error('Marco API error:', err)
    return NextResponse.json({ error: 'Errore interno' }, { status: 500 })
  }
}
