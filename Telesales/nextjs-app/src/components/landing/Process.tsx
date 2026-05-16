export default function Process() {
  const steps = [
    { n: '01', title: 'Discovery · 15 minuti', desc: 'Ti facciamo domande su cosa vendi, a chi, e dove si inceppa. Zero vendita.', dur: '15 min · gratis' },
    { n: '02', title: 'Pilot su misura · 48h', desc: 'Marco addestrato sul tuo prodotto. 200 contatti veri. Vedi i risultati in dashboard.', dur: 'dati reali · no mockup' },
    { n: '03', title: 'Scali solo se funziona', desc: 'Il pilot deve portare lead misurabili. Se no, non paghi lo scale-up. Fine.', dur: 'performance based' },
  ]
  const includes = ['Training su tuoi prodotti e obiezioni','Integrazione con CRM esistente','Compliance GDPR + registro consensi','Handoff umano su lead caldi','Registrazione e trascrizione call','Dashboard real-time con sentiment']

  return (
    <section id="process" className="py-28 border-t border-white/8">
      <div className="max-w-7xl mx-auto px-8">
        <div className="font-mono text-[11px] text-white/40 uppercase tracking-[.18em] mb-5">— Come funziona</div>
        <h2 className="font-display font-light mb-4" style={{ fontSize: 'clamp(36px,5vw,64px)', letterSpacing: '-0.03em' }}>
          Dalla call al risultato <em className="italic text-gold">in 48 ore.</em>
        </h2>
        <p className="text-white/60 text-lg mb-14 max-w-xl">Nessuna offerta da 40 pagine. Nessun contratto vincolante prima di vedere i numeri.</p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-10">
          {steps.map(s => (
            <div key={s.n} className="bg-ink-2 border border-white/8 rounded-2xl p-8">
              <div className="font-display font-light text-gold-gradient text-7xl leading-none mb-4">{s.n}</div>
              <h4 className="font-display text-xl mb-3">{s.title}</h4>
              <p className="text-white/50 text-sm leading-relaxed mb-5">{s.desc}</p>
              <span className="font-mono text-[10.5px] text-gold uppercase tracking-wide">{s.dur}</span>
            </div>
          ))}
        </div>

        <div className="bg-gradient-to-br from-blue-brand/18 to-gold/5 border border-white/14 rounded-2xl p-10 grid grid-cols-1 md:grid-cols-2 gap-10">
          <div>
            <h5 className="font-display text-2xl mb-2">Cosa include ogni pilot</h5>
            <p className="text-white/40 text-sm">Incluso nel pilot 48h — senza costi aggiuntivi.</p>
          </div>
          <ul className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {includes.map(i => (
              <li key={i} className="flex gap-3 items-start text-sm text-white/60 leading-relaxed">
                <span className="w-3.5 h-3.5 rounded-full bg-gradient-gold flex-shrink-0 mt-0.5 shadow-[0_0_0_3px_rgba(212,175,106,.08)]" />
                {i}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  )
}
