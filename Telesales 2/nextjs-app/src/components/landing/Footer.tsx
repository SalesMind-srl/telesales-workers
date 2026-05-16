import Link from 'next/link'

export default function Footer() {
  return (
    <footer className="py-16 border-t border-white/8 text-center">
      <div className="max-w-7xl mx-auto px-8">
        <img src="/logo.png" alt="Telesales" className="h-7 mx-auto mb-4 opacity-90" />
        <p className="text-white/40 text-sm mb-2">Sostituiamo interi reparti aziendali con AI.</p>
        <p className="text-white/30 text-sm mb-6">© 2026 Telesales Srl · P.IVA 0123456789</p>
        <div className="flex justify-center gap-5 flex-wrap text-sm text-white/40">
          <Link href="/privacy" className="hover:text-white transition-colors">Privacy</Link>
          <Link href="/termini" className="hover:text-white transition-colors">Termini</Link>
          <Link href="/gdpr" className="hover:text-white transition-colors">GDPR</Link>
          <Link href="/app" className="hover:text-white transition-colors text-gold">App interna ↗</Link>
        </div>
      </div>
    </footer>
  )
}
