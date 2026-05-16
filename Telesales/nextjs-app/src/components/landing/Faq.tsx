'use client'
import { useState } from 'react'

const FAQ = [
  { q: 'Funziona davvero? Sembra troppo bello.', a: 'Abbiamo fatto 1.033 chiamate reali in 5 giorni sulle nostre aziende target. Puoi ascoltare le registrazioni durante la discovery. Non ti chiediamo di fidarti, ti chiediamo di verificare.' },
  { q: 'Quanto costa?', a: 'Pilot 48h: da €9.600 setup + €1.920/mese. Niente setup fee nascoste, niente minimi annui. Se il pilot non porta lead misurabili, lo scale-up non parte.' },
  { q: 'I miei clienti si accorgeranno che è un\'AI?', a: 'No. Marco parla italiano nativo con cadenza toscana, pause naturali, gestisce interruzioni. Abbiamo registrazioni che puoi ascoltare in blind test. Spoiler: non indovini.' },
  { q: 'Si integra con il mio CRM?', a: 'Sì. HubSpot, Salesforce, Pipedrive, Zoho, Freshsales, e custom via API. Ogni call scrive automaticamente contatto, trascrizione, sentiment, next action.' },
  { q: 'E la privacy / GDPR?', a: 'Registro consensi integrato. Server UE. Nessun dato fuori dall\'EEA. DPA firmabile prima del pilot.' },
  { q: 'Quanto ci mette a partire?', a: 'Da contratto firmato a prima chiamata reale: 48 ore. Niente onboarding da 3 mesi, niente consulenti, niente Gantt di 40 righe.' },
]

export default function Faq() {
  const [open, setOpen] = useState<number | null>(null)
  return (
    <section id="faq" className="py-28 border-t border-white/8">
      <div className="max-w-7xl mx-auto px-8 grid grid-cols-1 md:grid-cols-[320px_1fr] gap-20">
        <div>
          <div className="font-mono text-[11px] text-white/40 uppercase tracking-[.18em] mb-5">— FAQ</div>
          <h2 className="font-display font-light" style={{ fontSize: 'clamp(32px,4vw,48px)', letterSpacing: '-0.03em' }}>
            Le domande <em className="italic text-gold">che ci fanno davvero.</em>
          </h2>
        </div>
        <div>
          {FAQ.map((f, i) => (
            <div key={i} className="border-b border-white/8">
              <button onClick={() => setOpen(open === i ? null : i)}
                className="w-full text-left py-6 flex justify-between items-center gap-6 font-display text-xl hover:text-gold transition-colors">
                {f.q}
                <span className={`w-7 h-7 rounded-full border border-white/14 grid place-items-center flex-shrink-0 transition-all ${open === i ? 'bg-gradient-gold border-transparent rotate-135 text-ink-0' : ''}`}>
                  +
                </span>
              </button>
              {open === i && (
                <div className="pb-6 text-white/60 text-[15.5px] leading-relaxed max-w-2xl">{f.a}</div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
