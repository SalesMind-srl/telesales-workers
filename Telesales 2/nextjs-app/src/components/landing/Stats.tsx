'use client'
import { useEffect, useRef } from 'react'

const STATS = [
  { count: 1033, label: 'chiamate effettuate da Marco in autonomia', src: 'Periodo: 5 giorni' },
  { count: 72, label: 'lead qualificati interessati a una call', src: 'Tasso: 6.97%' },
  { count: 30, label: 'email dirette raccolte da centralino', src: 'Database pulito, GDPR' },
  { count: 340, suffix: 'h', label: 'ore di lavoro umano risparmiate', src: '≈ 2 full-time per settimana' },
]

function StatCell({ count, suffix = '', label, src }: typeof STATS[0]) {
  const numRef = useRef<HTMLDivElement>(null)
  const observed = useRef(false)

  useEffect(() => {
    const el = numRef.current
    if (!el) return
    const io = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && !observed.current) {
        observed.current = true
        const dur = 1400, t0 = performance.now()
        const fmt = (n: number) => n.toLocaleString('it-IT')
        function step(t: number) {
          const p = Math.min(1, (t - t0) / dur)
          const e = 1 - Math.pow(1 - p, 3)
          el!.textContent = fmt(Math.round(count * e)) + suffix
          if (p < 1) requestAnimationFrame(step)
        }
        requestAnimationFrame(step)
      }
    }, { threshold: 0.4 })
    io.observe(el)
    return () => io.disconnect()
  }, [count, suffix])

  return (
    <div className="bg-ink-2 p-10">
      <div ref={numRef} className="font-display font-light text-gold-gradient leading-none mb-4"
        style={{ fontSize: 'clamp(44px,6vw,84px)', letterSpacing: '-0.03em' }}>
        0{suffix}
      </div>
      <div className="text-white/60 text-[14.5px] leading-snug mb-5" dangerouslySetInnerHTML={{ __html: label }} />
      <div className="font-mono text-[10.5px] text-white/40 uppercase tracking-wide">{src}</div>
    </div>
  )
}

export default function Stats() {
  return (
    <section className="py-28 border-t border-white/8">
      <div className="max-w-7xl mx-auto px-8">
        <div className="mb-16">
          <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-white/14 font-mono text-[11px] uppercase tracking-wider text-white/60 bg-white/3 mb-5">
            <span className="dot-live" />Dati live · aggiornati oggi
          </span>
          <h2 className="font-display font-light leading-none mb-4" style={{ fontSize: 'clamp(36px,5vw,64px)', letterSpacing: '-0.03em' }}>
            Usiamo i nostri prodotti <em className="italic text-gold">su noi stessi.</em>
          </h2>
          <p className="text-white/60 text-lg leading-relaxed max-w-xl">
            Cinque giorni di Marco che chiama aziende italiane vere, per vendere Telesales. Non mockup. Non stime. Registro reale.
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 border border-white/8 rounded-2xl overflow-hidden divide-x divide-y md:divide-y-0 divide-white/8">
          {STATS.map(s => <StatCell key={s.count} {...s} />)}
        </div>
      </div>
    </section>
  )
}
