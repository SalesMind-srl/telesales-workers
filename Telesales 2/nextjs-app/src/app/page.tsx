import Nav from '@/components/landing/Nav'
import Hero from '@/components/landing/Hero'
import TrustBar from '@/components/landing/TrustBar'
import Stats from '@/components/landing/Stats'
import Products from '@/components/landing/Products'
import MarcoDemo from '@/components/landing/MarcoDemo'
import Process from '@/components/landing/Process'
import Faq from '@/components/landing/Faq'
import Booking from '@/components/landing/Booking'
import Footer from '@/components/landing/Footer'

export default function HomePage() {
  return (
    <main className="overflow-x-hidden">
      <Nav />
      <Hero />
      <TrustBar />
      <Stats />
      <Products />
      <MarcoDemo />
      <Process />
      <Faq />
      <Booking />
      <Footer />
    </main>
  )
}
