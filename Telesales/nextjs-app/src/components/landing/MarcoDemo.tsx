'use client'
import { useState, useRef } from 'react'

interface Message { role: 'user' | 'assistant'; content: string }

export default function MarcoDemo() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [started, setStarted] = useState(false)
  const [phone, setPhone] = useState('')
  const [calling, setCalling] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  async function startChat() {
    setStarted(true)
    setLoading(true)
    const res = await fetch('/api/marco', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: [{ role: 'user', content: 'Ciao, ho visitato il sito e sono curioso.' }] }),
    })
    const data = await res.json()
    setMessages([{ role: 'assistant', content: data.text }])
    setLoading(false)
  }

  async function sendMessage() {
    if (!input.trim() || loading) return
    const newMessages: Message[] = [...messages, { role: 'user', content: input }]
    setMessages(newMessages)
    setInput('')
    setLoading(true)
    const res = await fetch('/api/marco', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: newMessages }),
    })
    const data = await res.json()
    setMessages(m => [...m, { role: 'assistant', content: data.text }])
    setLoading(false)
    setTimeout(() => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }), 100)
  }

  async function callMe() {
    if (phone.length < 8) return
    setCalling(true)
    await new Promise(r => setTimeout(r, 2000))
    setCalling(false)
    setStarted(true)
    setLoading(true)
    const res = await fetch('/api/marco', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: [{ role: 'user', content: `Il prospect ha inserito il numero +39${phone}. Inizia la chiamata con un saluto naturale e una domanda aperta su cosa fa la sua azienda.` }] }),
    })
    const data = await res.json()
    setMessages([{ role: 'assistant', content: data.text }])
    setLoading(false)
  }

  return (
    <section id="marco" className="py-28 border-t border-white/8 relative overflow-hidden">
      <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(ellipse_70%_60%_at_50%_40%,rgba(212,175,55,.08),transparent_60%)]" />
      <div className="relative max-w-7xl mx-auto px-8 text-center">
        <div className="font-mono text-[11px] text-white/40 uppercase tracking-[.18em] mb-5">— Demo live</div>
        <h2 className="font-display font-light mb-4 max-w-3xl mx-auto" style={{ fontSize: 'clamp(36px,5vw,64px)', letterSpacing: '-0.03em' }}>
          Dimentica lo screenshot. <em className="italic text-gold">Parla con lui.</em>
        </h2>
        <p className="text-white/60 text-lg mb-12 max-w-2xl mx-auto leading-relaxed">
          Marco è il nostro AI commerciale. Conosce i 9 prodotti, risponde a qualunque domanda, prende appuntamenti.
        </p>

        <div className="max-w-2xl mx-auto bg-gradient-to-b from-ink-2 to-[#0a0b14] border border-gold/30 rounded-3xl p-10 shadow-[0_80px_120px_-40px_rgba(0,0,0,.8),0_0_120px_-20px_rgba(212,175,55,.1)]">
          {!started ? (
            <>
              <div className="relative w-36 h-36 mx-auto mb-7 cursor-pointer" onClick={startChat}>
                <div className="absolute inset-0 rounded-full bg-gradient-gold flex items-center justify-center text-ink-0 text-5xl shadow-[0_30px_60px_-20px_rgba(212,175,55,.55)]">
                  <svg width="42" height="42" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="9" y="3" width="6" height="12" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v4"/></svg>
                </div>
                <div className="absolute inset-0 rounded-full border-2 border-gold/40 animate-ping opacity-30" />
              </div>
              <h3 className="font-display text-3xl mb-2">Marco Ferretti<sup className="font-mono text-sm text-gold ml-1">v2.0</sup></h3>
              <p className="text-white/50 mb-6">AI commerciale · 780ms latenza · Italiano nativo</p>
              <button onClick={startChat} className="px-8 py-4 rounded-full bg-gradient-gold text-ink-0 font-semibold text-base shadow-[0_10px_30px_-10px_rgba(212,175,55,.6)] hover:-translate-y-0.5 transition-transform mr-3">
                🎙 Clicca per parlare
              </button>

              {/* Chiamata diretta */}
              <div className="mt-8 pt-8 border-t border-white/8">
                <p className="text-white/40 font-mono text-[11px] uppercase tracking-wide mb-4">— oppure Marco ti chiama lui</p>
                <div className="flex gap-2 justify-center">
                  <span className="flex items-center px-4 py-3 bg-white/4 border border-white/14 rounded-xl font-mono text-white/60 text-sm">🇮🇹 +39</span>
                  <input value={phone} onChange={e => setPhone(e.target.value)} onKeyDown={e => e.key === 'Enter' && callMe()}
                    placeholder="339 123 4567" className="flex-1 bg-white/4 border border-white/14 rounded-xl px-4 py-3 text-white font-mono text-base outline-none focus:border-gold transition-colors" />
                  <button onClick={callMe} disabled={calling} className="px-5 py-3 rounded-xl bg-gradient-gold text-ink-0 font-semibold text-sm disabled:opacity-50 hover:-translate-y-0.5 transition-transform">
                    {calling ? '📞 …' : '📞 Chiamami'}
                  </button>
                </div>
              </div>
            </>
          ) : (
            <>
              <div className="min-h-[220px] max-h-[360px] overflow-y-auto flex flex-col gap-3 mb-4 text-left">
                {messages.map((m, i) => (
                  <div key={i} className={`max-w-[82%] p-3.5 rounded-2xl text-sm leading-relaxed ${m.role === 'assistant' ? 'bg-gold/10 border border-gold/20 self-start rounded-bl-sm' : 'bg-blue-brand/20 border border-blue-mid/30 self-end rounded-br-sm'}`}>
                    {m.role === 'assistant' && <div className="font-mono text-[10px] text-gold uppercase tracking-wide mb-1.5">Marco</div>}
                    {m.content}
                  </div>
                ))}
                {loading && (
                  <div className="bg-gold/10 border border-gold/20 self-start rounded-2xl rounded-bl-sm p-3.5">
                    <div className="font-mono text-[10px] text-gold uppercase tracking-wide mb-1.5">Marco</div>
                    <span className="text-white/40 animate-pulse">●●●</span>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
              <div className="flex gap-2">
                <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && sendMessage()}
                  placeholder="Rispondi a Marco…" className="flex-1 bg-white/4 border border-white/14 rounded-full px-5 py-3 text-white text-sm outline-none focus:border-gold transition-colors" />
                <button onClick={sendMessage} className="px-5 py-3 rounded-full bg-gradient-gold text-ink-0 font-semibold text-sm hover:-translate-y-0.5 transition-transform">Invia</button>
                <button onClick={() => { setStarted(false); setMessages([]); }} className="px-4 py-3 rounded-full border border-red-500/40 text-red-400 text-sm hover:bg-red-500/10 transition-colors">✕</button>
              </div>
            </>
          )}
        </div>

        <div className="mt-10 text-center">
          <div className="font-mono text-[11px] text-white/40 uppercase tracking-wide mb-4">— Prova a chiedergli</div>
          <div className="flex gap-3 justify-center flex-wrap">
            {['Quanto costa davvero?', 'Si integra col mio CRM?', 'Si accorgono che è un\'AI?'].map(q => (
              <button key={q} onClick={() => { if (!started) startChat().then(() => { setInput(q); sendMessage(); }); else { setInput(q); sendMessage(); } }}
                className="px-5 py-3 border border-white/14 rounded-xl text-white/60 text-sm hover:border-gold/40 hover:text-white transition-all">
                {q} ↗
              </button>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
