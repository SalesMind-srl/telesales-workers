'use client'
import { useState } from 'react'
import { toast } from 'sonner'

export default function Booking() {
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({ nome: '', cognome: '', email: '', tel: '', az: '', msg: '' })

  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
    setForm(f => ({ ...f, [k]: e.target.value }))

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await fetch('/api/booking', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      if (res.ok) {
        toast.success('Demo prenotata!', { description: 'Niccolò ti risponde entro 24h. Controlla la mail.' })
        setForm({ nome: '', cognome: '', email: '', tel: '', az: '', msg: '' })
      } else {
        throw new Error()
      }
    } catch {
      toast.error('Errore invio', { description: 'Scrivici a info@telesales.it' })
    }
    setLoading(false)
  }

  const field = 'w-full bg-white/2 border border-white/14 rounded-xl px-4 py-3 text-white text-sm outline-none focus:border-gold transition-colors placeholder:text-white/30'

  return (
    <section id="booking" className="py-28 border-t border-white/8 relative overflow-hidden">
      <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(ellipse_80%_60%_at_80%_20%,rgba(30,58,138,.22),transparent_60%)]" />
      <div className="relative max-w-7xl mx-auto px-8 grid grid-cols-1 lg:grid-cols-2 gap-20 items-start">
        <div>
          <div className="font-mono text-[11px] text-white/40 uppercase tracking-[.18em] mb-5">— 15 minuti con Niccolò</div>
          <h2 className="font-display font-light mb-5" style={{ fontSize: 'clamp(36px,4vw,56px)', letterSpacing: '-0.03em' }}>
            Demo su misura.<br /><em className="italic text-gold">Zero vendita.</em>
          </h2>
          <p className="text-white/60 text-lg leading-relaxed mb-10">
            Ti mostriamo Marco dal vivo che chiama un tuo prospect. Se ti convinci, parliamo di pilot. Se no, ci salutiamo.
          </p>
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-gradient-gold flex items-center justify-center font-display text-ink-0 text-lg font-medium">N</div>
            <div>
              <div className="font-display text-xl">Niccolò Pratesi</div>
              <div className="font-mono text-[11px] text-white/40 uppercase tracking-wide">CEO & Co-Founder</div>
            </div>
          </div>
          <p className="text-white/40 text-sm italic mt-4 leading-relaxed max-w-sm">
            "Rispondo io alle call. Se non ti è utile, lo dico dopo 5 minuti e ti lascio andare."
          </p>
        </div>

        <form onSubmit={submit} className="bg-ink-2/80 backdrop-blur border border-white/14 rounded-3xl p-9 shadow-[0_60px_120px_-40px_rgba(0,0,0,.6)]">
          <div className="grid grid-cols-2 gap-3.5 mb-3.5">
            <div><label className="font-mono text-[10px] text-white/40 uppercase tracking-wide block mb-2">Nome</label><input required value={form.nome} onChange={set('nome')} className={field} /></div>
            <div><label className="font-mono text-[10px] text-white/40 uppercase tracking-wide block mb-2">Cognome</label><input required value={form.cognome} onChange={set('cognome')} className={field} /></div>
          </div>
          <div className="mb-3.5"><label className="font-mono text-[10px] text-white/40 uppercase tracking-wide block mb-2">Email</label><input required type="email" value={form.email} onChange={set('email')} className={field} /></div>
          <div className="mb-3.5"><label className="font-mono text-[10px] text-white/40 uppercase tracking-wide block mb-2">Cellulare</label><input type="tel" value={form.tel} onChange={set('tel')} className={field} /></div>
          <div className="mb-3.5"><label className="font-mono text-[10px] text-white/40 uppercase tracking-wide block mb-2">Azienda</label><input required value={form.az} onChange={set('az')} className={field} /></div>
          <div className="mb-5"><label className="font-mono text-[10px] text-white/40 uppercase tracking-wide block mb-2">Messaggio (opzionale)</label><textarea value={form.msg} onChange={set('msg')} rows={3} className={field + ' resize-none'} /></div>
          <button type="submit" disabled={loading}
            className="w-full py-4 rounded-full bg-gradient-gold text-ink-0 font-semibold text-base shadow-[0_10px_30px_-10px_rgba(212,175,55,.5)] hover:-translate-y-0.5 transition-transform disabled:opacity-60">
            {loading ? 'Invio in corso…' : 'Prenota demo →'}
          </button>
          <p className="text-center font-mono text-[10px] text-white/30 uppercase tracking-wide mt-4">Dati al sicuro · GDPR · Mai venduti a terzi</p>
        </form>
      </div>
    </section>
  )
}
