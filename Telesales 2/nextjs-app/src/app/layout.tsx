import type { Metadata } from 'next'
import { Geist, JetBrains_Mono } from 'next/font/google'
import { Fraunces } from 'next/font/google'
import './globals.css'
import { Providers } from '@/components/providers'
import { Toaster } from 'sonner'

const geist = Geist({
  subsets: ['latin'],
  variable: '--font-geist',
})

const fraunces = Fraunces({
  subsets: ['latin'],
  variable: '--font-fraunces',
  axes: ['opsz'],
})

const jetbrains = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-jetbrains',
})

export const metadata: Metadata = {
  title: 'Telesales.it — Sostituiamo interi reparti aziendali con AI',
  description: '9 prodotti AI che fanno il lavoro di team interi. Commerciale, HR, marketing, customer care. 1.033 chiamate reali in 5 giorni.',
  openGraph: {
    title: 'Telesales.it',
    description: 'Sostituiamo interi reparti aziendali con AI.',
    url: 'https://telesales.it',
    siteName: 'Telesales',
    locale: 'it_IT',
    type: 'website',
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="it" className="dark">
      <body className={`${geist.variable} ${fraunces.variable} ${jetbrains.variable} font-sans bg-ink-0 text-white antialiased`}>
        <Providers>
          {children}
          <Toaster
            position="top-right"
            toastOptions={{
              style: {
                background: 'rgba(18,18,26,.96)',
                border: '1px solid rgba(212,175,106,.3)',
                color: '#ececf1',
                fontFamily: 'var(--font-geist)',
              },
            }}
          />
        </Providers>
      </body>
    </html>
  )
}
