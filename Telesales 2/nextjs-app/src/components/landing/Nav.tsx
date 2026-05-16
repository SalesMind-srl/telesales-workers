'use client'
import { useState, useEffect } from 'react'
import Link from 'next/link'
import Image from 'next/image'

const links = [
  { href: '#products', label: 'Prodotti' },
  { href: '#marco', label: 'Demo' },
  { href: '#process', label: 'Come funziona' },
  { href: '#faq', label: 'FAQ' },
  { href: '/app', label: 'App ↗' },
]

export default function Nav() {
  const [scrolled, setScrolled] = useState(false)
  const [lang, setLang] = useState<'it'|'en'>('it')

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled ? 'bg-ink-0/80 backdrop-blur-xl border-b border-white/8' : ''}`}>
      <div className="max-w-7xl mx-auto px-8 h-[72px] flex items-center justify-between">
        <Link href="/" className="flex items-center gap-3">
          <img src="/logo.png" alt="Telesales" className="h-7 opacity-95" />
        </Link>

        <div className="hidden md:flex items-center gap-7">
          {links.map(l => (
            <Link key={l.href} href={l.href} className="text-sm text-white/60 hover:text-white transition-colors">
              {l.label}
            </Link>
          ))}
        </div>

        <div className="flex items-center gap-3">
          <div className="flex overflow-hidden border border-white/14 rounded-full font-mono text-[11px]">
            {(['it','en'] as const).map(l => (
              <button key={l} onClick={() => setLang(l)}
                className={`px-3 py-1.5 transition-colors ${lang === l ? 'bg-white text-ink-0 font-medium' : 'text-white/50'}`}>
                {l.toUpperCase()}
              </button>
            ))}
          </div>
          <Link href="#booking"
            className="px-5 py-2.5 rounded-full bg-gradient-to-br from-gold-3 via-gold to-gold-1 text-ink-0 text-sm font-semibold shadow-[0_10px_24px_-10px_rgba(212,175,106,.6)] hover:-translate-y-px transition-transform">
            Prenota demo →
          </Link>
        </div>
      </div>
    </nav>
  )
}
