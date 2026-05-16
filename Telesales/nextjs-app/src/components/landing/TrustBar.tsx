'use client'

const COMPANIES = [
  'Tessitura Lascialfari','Studio Anna Masi','Pelletterie Claudia','Morellino',
  'CIA Servizi Livorno','NIPAL','MOEL','SI-FUR','Mida SB','Officina Toscana',
  'Lanificio Pratese','Caseificio del Casentino','Oleificio Chianti','Ceramica Montelupo',
  'Calzaturificio Montegranaro','Mobilificio Brianza','Vetreria Muranese','Conceria Santa Croce',
]

export default function TrustBar() {
  const all = [...COMPANIES, ...COMPANIES]
  return (
    <section className="py-14 border-t border-white/8">
      <p className="text-center font-mono text-[11px] uppercase tracking-[.18em] text-white/40 mb-7">
        in conversazione con aziende italiane vere
      </p>
      <div className="overflow-hidden [mask-image:linear-gradient(90deg,transparent,#000_10%,#000_90%,transparent)]">
        <div className="flex gap-3.5 w-max animate-marquee">
          {all.map((c, i) => (
            <span key={i} className="px-4 py-2 rounded-full border border-white/14 text-white/50 text-sm font-medium whitespace-nowrap bg-white/2">
              {c}
            </span>
          ))}
        </div>
      </div>
    </section>
  )
}
