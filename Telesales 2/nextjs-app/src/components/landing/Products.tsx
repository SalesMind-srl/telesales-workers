'use client'
import { useEffect, useRef } from 'react'

const PRODUCTS = [
  { n: '01', name: 'Outreach AI', desc: 'Instagram, LinkedIn, email, WhatsApp. Sequenze AI-personalizzate. Reply-detection automatica.', tag: '7 canali · AI-compose' },
  { n: '02', name: 'AI Voice', desc: 'Voci indistinguibili da umano. Cold calling, inbound, customer care. Chiude contratti.', tag: '● flagship', hero: true },
  { n: '03', name: 'CRM War Room', desc: 'Pipeline, scoring real-time, follow-up automatici. Si ricorda tutto.', tag: 'scoring live · 47 fonti' },
  { n: '04', name: 'Talentia · HR AI', desc: 'Sourcing + screening vocale + shortlist pronta. Ti arrivano già filtrati.', tag: 'screening 24/7' },
  { n: '05', name: 'Lead Founder AI', desc: '127k+ record/giorno da 47 fonti globali. 194 paesi. 98.4% accuracy.', tag: '194 paesi · 127k/giorno' },
  { n: '06', name: 'Eventia', desc: 'Ticketing, sponsor outreach, networking AI, check-in vocale.', tag: 'ticketing · networking AI' },
  { n: '07', name: 'Product Maker AI', desc: 'Corsi, playbook, template. Checkout + delivery automatica.', tag: 'checkout · delivery · A/B' },
  { n: '08', name: 'Marketing AI', desc: 'Contenuti, grafica, copy, strategia, ADV. Tutto coordinato.', tag: 'full stack' },
  { n: '09', name: 'Investor Founder', desc: '1.284 fondi screened. Match score ≥80 solo warm intro.', tag: '1.284 fondi · warm intro' },
]

export default function Products() {
  const waveRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = waveRef.current
    if (!el) return
    for (let i = 0; i < 26; i++) {
      const s = document.createElement('span')
      s.style.cssText = `display:block;width:3px;background:linear-gradient(to top,#c39446,#f5e7a8);border-radius:2px;animation:wave 1.4s ease-in-out ${i * 0.04}s infinite`
      el.appendChild(s)
    }
  }, [])

  return (
    <section id="products" className="py-28 border-t border-white/8">
      <div className="max-w-7xl mx-auto px-8">
        <div className="font-mono text-[11px] text-white/40 uppercase tracking-[.18em] mb-5">— 9 Prodotti</div>
        <h2 className="font-display font-light mb-4" style={{ fontSize: 'clamp(36px,5vw,64px)', letterSpacing: '-0.03em' }}>
          Un ecosistema. <em className="italic text-gold">Team interi dentro.</em>
        </h2>
        <p className="text-white/60 text-lg leading-relaxed mb-14 max-w-2xl">
          Nove prodotti che si parlano tra loro. Uno li governa — l'AI Voice — ma ognuno vale da solo.
        </p>

        <div className="grid grid-cols-2 md:grid-cols-6 auto-rows-[minmax(180px,auto)] gap-3.5">
          {PRODUCTS.map(p => (
            <article key={p.n}
              className={`group relative rounded-2xl border p-6 flex flex-col gap-3 overflow-hidden transition-all duration-300 cursor-default
                ${p.hero
                  ? 'col-span-2 md:col-span-3 row-span-2 bg-gradient-to-br from-[rgba(212,175,55,.16)] via-ink-2 to-[rgba(30,58,138,.34)] border-gold/40 hover:border-gold/60'
                  : 'col-span-1 md:col-span-2 bg-ink-2 border-white/8 hover:border-gold/30 hover:-translate-y-0.5 hover:shadow-[0_20px_40px_-20px_rgba(0,0,0,.5)]'
                }`}>
              {p.hero && (
                <span className="absolute top-4 right-4 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[rgba(34,197,94,.1)] border border-[rgba(34,197,94,.3)] font-mono text-[10px] text-[#a7f3d0] uppercase tracking-wide">
                  <span className="dot-live" />LIVE
                </span>
              )}
              <span className="font-mono text-[10.5px] text-white/40 uppercase tracking-wide">{p.n} / 09</span>
              <div className={`w-10 h-10 rounded-xl bg-gradient-to-br from-[rgba(212,175,55,.14)] to-[rgba(212,175,55,.04)] border border-gold/30 ${p.hero ? 'bg-gradient-gold w-12 h-12 rounded-2xl' : ''}`} />
              <h3 className={`font-display font-light leading-tight ${p.hero ? 'text-3xl' : 'text-xl'}`}
                style={{ letterSpacing: '-.015em' }}>{p.name}</h3>
              <p className={`text-white/50 leading-relaxed flex-1 ${p.hero ? 'text-base max-w-md' : 'text-sm'}`}>{p.desc}</p>
              {p.hero && (
                <div ref={waveRef} className="absolute right-6 bottom-6 flex items-center gap-[3px] h-12 w-36 justify-end" aria-hidden />
              )}
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border border-white/14 font-mono text-[10px] text-white/40 uppercase tracking-wide w-fit">
                {p.tag}
              </span>
            </article>
          ))}
        </div>
      </div>
    </section>
  )
}
