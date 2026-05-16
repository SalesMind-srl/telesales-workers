'use client'
import { useEffect, useRef } from 'react'
import Link from 'next/link'

const STATS = [
  { n: '1.033', l: 'chiamate · 5gg' },
  { n: '72', l: 'lead qualificati' },
  { n: '340h', l: 'ore risparmiate' },
  { n: '<800ms', l: 'latenza voce' },
]

export default function Hero() {
  const waveRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = waveRef.current
    if (!el) return
    const bars: HTMLSpanElement[] = []
    for (let i = 0; i < 56; i++) {
      const b = document.createElement('span')
      b.style.cssText = 'display:block;min-width:2px;max-width:5px;flex:1;background:linear-gradient(to top,#c39446,#f5e7a8);border-radius:3px;transform-origin:center'
      el.appendChild(b)
      bars.push(b)
    }
    let t0 = performance.now()
    let raf: number
    function tick() {
      const t = (performance.now() - t0) / 1000
      bars.forEach((b, i) => {
        const x = i / bars.length
        const env = 0.35 + 0.35 * Math.sin(x * 5 + t * 2.1) * Math.cos(t * 1.1) + 0.2 * Math.sin(x * 17 + t * 4)
        const h = Math.max(3, Math.min(100, Math.abs(env) * 100))
        b.style.height = h + '%'
        b.style.opacity = String(0.6 + 0.4 * Math.sin(x * 8 + t))
      })
      raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [])

  return (
    <header className="relative min-h-svh flex items-center pt-20 overflow-hidden">
      {/* BG */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_20%_10%,rgba(61,95,184,.22),transparent_55%),radial-gradient(ellipse_70%_50%_at_85%_30%,rgba(212,175,55,.16),transparent_60%)]" />
        <div className="absolute inset-0 opacity-40"
          style={{ backgroundImage: 'linear-gradient(to right,rgba(255,255,255,.025) 1px,transparent 1px),linear-gradient(to bottom,rgba(255,255,255,.025) 1px,transparent 1px)', backgroundSize: '80px 80px' }} />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-8 w-full grid grid-cols-1 lg:grid-cols-2 gap-16 items-center py-20">
        <div>
          <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-white/14 font-mono text-[11px] uppercase tracking-wider text-white/60 bg-white/3 backdrop-blur mb-6">
            <span className="dot-live" />
            1.033 chiamate reali · questa settimana
          </span>

          <h1 className="font-display font-light leading-[.96] tracking-[-0.035em] mb-6" style={{ fontSize: 'clamp(44px,7.5vw,104px)' }}>
            <span className="block">Sostituiamo</span>
            <span className="block text-gold-gradient italic">interi reparti</span>
            <span className="block">aziendali con AI.</span>
          </h1>

          <p className="text-lg text-white/60 leading-relaxed mb-8 max-w-lg">
            Nove prodotti AI che fanno il lavoro di team interi. Commerciale, HR, marketing, customer care — senza pause, senza ferie, senza turnover.
          </p>

          <div className="flex gap-3 flex-wrap mb-10">
            <a href="#marco" className="flex items-center gap-2 px-6 py-3.5 rounded-full bg-gradient-to-br from-gold-3 via-gold to-gold-1 text-ink-0 font-semibold shadow-[0_10px_24px_-10px_rgba(212,175,106,.6)] hover:-translate-y-px transition-transform">
              🎙 Parla con Marco ora →
            </a>
            <a href="#booking" className="px-6 py-3.5 rounded-full border border-white/14 text-white hover:border-gold/40 bg-white/3 backdrop-blur transition-colors">
              Prenota demo gratis
            </a>
          </div>

          <div className="grid grid-cols-4 gap-6 pt-8 border-t border-white/8">
            {STATS.map(s => (
              <div key={s.n}>
                <div className="font-display text-3xl text-gold-gradient font-light">{s.n}</div>
                <div className="font-mono text-[10.5px] text-white/50 uppercase tracking-wide mt-1">{s.l}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Waveform visual */}
        <div className="relative aspect-[4/5] rounded-3xl overflow-hidden border border-white/14 bg-ink-2 shadow-[0_60px_120px_-40px_rgba(0,0,0,.6)] hidden lg:block">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_70%_50%_at_50%_30%,rgba(212,175,55,.14),transparent_60%)]" />
          <div className="absolute top-5 left-5 right-5 flex justify-between font-mono text-[10.5px] uppercase tracking-wide text-white/40">
            <span className="text-[#22c55e] flex items-center gap-1.5"><span className="dot-live" />live</span>
            <span>marco · v2.0</span>
          </div>
          <div className="absolute inset-0 flex items-center justify-center px-8">
            <div ref={waveRef} className="flex items-center justify-center gap-[3px] w-full" style={{ height: '50%' }} />
          </div>
          <div className="absolute bottom-5 left-5 right-5 flex justify-between font-mono text-[10.5px] uppercase tracking-wide text-white/40">
            <span>italiano · toscana</span>
            <span>800ms</span>
          </div>
        </div>
      </div>
    </header>
  )
}
