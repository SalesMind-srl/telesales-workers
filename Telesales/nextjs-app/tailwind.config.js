/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        ink: {
          0: '#07070a',
          1: '#0d0e12',
          2: '#15161c',
          3: '#1d1e26',
        },
        gold: {
          1: '#c39446',
          2: '#d4af6a',
          3: '#f5e7a8',
          DEFAULT: '#d4af6a',
        },
        blue: {
          brand: '#1e3a8a',
          mid: '#3b5fb8',
          light: '#5a7fb0',
        },
      },
      fontFamily: {
        display: ['var(--font-fraunces)', 'Georgia', 'serif'],
        sans: ['var(--font-geist)', 'system-ui', 'sans-serif'],
        mono: ['var(--font-jetbrains)', 'ui-monospace', 'monospace'],
      },
      backgroundImage: {
        'gradient-gold': 'linear-gradient(135deg, #f5e7a8 0%, #d4af6a 45%, #7a5e18 100%)',
        'gradient-dark': 'linear-gradient(180deg, #07070a, #0c0d14)',
      },
      animation: {
        'pulse-live': 'pulseLive 1.8s ease-in-out infinite',
        'wave': 'wave 1.4s ease-in-out infinite',
        'marquee': 'marquee 50s linear infinite',
      },
      keyframes: {
        pulseLive: {
          '0%, 100%': { boxShadow: '0 0 0 0 rgba(34,197,94,.55)' },
          '70%': { boxShadow: '0 0 0 8px rgba(34,197,94,0)' },
        },
        wave: {
          '0%, 100%': { height: '20%' },
          '50%': { height: '90%' },
        },
        marquee: {
          to: { transform: 'translateX(-50%)' },
        },
      },
    },
  },
  plugins: [],
}
