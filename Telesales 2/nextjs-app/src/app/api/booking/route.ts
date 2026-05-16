import { NextRequest, NextResponse } from 'next/server'
import { Resend } from 'resend'
import { createClient } from '@/lib/supabase/server'

const resend = new Resend(process.env.RESEND_API_KEY)

export async function POST(req: NextRequest) {
  try {
    const body = await req.json()
    const { nome, cognome, email, tel, az, msg } = body

    if (!nome || !email) {
      return NextResponse.json({ error: 'Nome e email obbligatori' }, { status: 400 })
    }

    // Salva su Supabase
    const supabase = createClient()
    await supabase.from('demo_bookings').insert({
      nome, cognome, email, tel,
      azienda: az, messaggio: msg,
      source: 'landing',
    })

    // Invia email notifica a Niccolò
    await resend.emails.send({
      from: 'Telesales <notifiche@telesales.it>',
      to: [process.env.BOOKING_EMAIL || 'nicco@telesales.it'],
      subject: `🎯 Nuova demo: ${nome} ${cognome || ''} — ${az || 'N/D'}`,
      html: `
        <div style="font-family:sans-serif;max-width:600px;margin:0 auto;background:#07070a;color:#ececf1;padding:32px;border-radius:12px;border:1px solid rgba(212,175,106,.3)">
          <h2 style="font-size:24px;margin:0 0 24px;color:#d4af6a">Nuova richiesta demo</h2>
          <table style="width:100%;border-collapse:collapse">
            <tr><td style="padding:8px 0;color:#8a8b94;font-size:13px">Nome</td><td style="padding:8px 0;font-weight:500">${nome} ${cognome || ''}</td></tr>
            <tr><td style="padding:8px 0;color:#8a8b94;font-size:13px">Email</td><td style="padding:8px 0"><a href="mailto:${email}" style="color:#d4af6a">${email}</a></td></tr>
            <tr><td style="padding:8px 0;color:#8a8b94;font-size:13px">Telefono</td><td style="padding:8px 0">${tel || '—'}</td></tr>
            <tr><td style="padding:8px 0;color:#8a8b94;font-size:13px">Azienda</td><td style="padding:8px 0">${az || '—'}</td></tr>
            ${msg ? `<tr><td style="padding:8px 0;color:#8a8b94;font-size:13px">Messaggio</td><td style="padding:8px 0">${msg}</td></tr>` : ''}
          </table>
          <a href="mailto:${email}?subject=Demo Telesales — Risposta" style="display:inline-block;margin-top:24px;padding:12px 24px;background:linear-gradient(135deg,#f5e7a8,#d4af6a);color:#07070a;border-radius:999px;font-weight:600;font-size:14px;text-decoration:none">Rispondi a ${nome}</a>
        </div>
      `,
    })

    // Invia conferma al prospect
    await resend.emails.send({
      from: 'Marco Ferretti <marco@telesales.it>',
      to: [email],
      subject: `Perfetto ${nome} — Ci sentiamo presto`,
      html: `
        <div style="font-family:sans-serif;max-width:600px;margin:0 auto;background:#07070a;color:#ececf1;padding:32px;border-radius:12px;border:1px solid rgba(212,175,106,.3)">
          <h2 style="font-size:24px;margin:0 0 16px">Ciao ${nome},</h2>
          <p style="color:#c2c3cb;line-height:1.6;margin:0 0 16px">Ho ricevuto la tua richiesta. Niccolò ti risponderà personalmente entro 24 ore per fissare la demo.</p>
          <p style="color:#c2c3cb;line-height:1.6;margin:0 0 24px">Nel frattempo puoi esplorare la piattaforma su <a href="https://telesales.it" style="color:#d4af6a">telesales.it</a> o parlarmi direttamente — rispondo 24/7.</p>
          <p style="color:#8a8b94;font-size:13px;margin:0">Marco Ferretti<br>AI Commerciale — Telesales.it</p>
        </div>
      `,
    })

    return NextResponse.json({ success: true })
  } catch (err) {
    console.error('Booking error:', err)
    return NextResponse.json({ error: 'Errore invio' }, { status: 500 })
  }
}
