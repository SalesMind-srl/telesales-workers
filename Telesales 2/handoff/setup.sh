#!/bin/bash
# Telesales — Quick Start per Claude Code
# Esegui: bash setup.sh

echo "🚀 Telesales — Setup produzione"

# 1. Crea Next.js app
npx create-next-app@latest telesales-app \
  --typescript \
  --tailwind \
  --app \
  --no-eslint \
  --src-dir

cd telesales-app

# 2. Installa dipendenze
npm install \
  @clerk/nextjs \
  @supabase/supabase-js \
  @supabase/ssr \
  resend \
  stripe \
  @stripe/stripe-js \
  zustand \
  @tanstack/react-query \
  @tanstack/react-query-devtools \
  framer-motion \
  @radix-ui/react-dialog \
  @radix-ui/react-dropdown-menu \
  @radix-ui/react-toast \
  lucide-react \
  clsx \
  tailwind-merge

# 3. Init shadcn (dark theme)
npx shadcn@latest init --base-color zinc --style default

# 4. Aggiungi componenti shadcn necessari
npx shadcn@latest add button input textarea select dialog toast badge

# 5. Crea .env.local
cat > .env.local << 'EOF'
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
RESEND_API_KEY=
VAPI_API_KEY=
VAPI_MARCO_ASSISTANT_ID=
STRIPE_SECRET_KEY=
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
FORMSPREE_ID=
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=
CLERK_SECRET_KEY=
ANTHROPIC_API_KEY=
NEXT_PUBLIC_APP_URL=http://localhost:3000
EOF

echo "✅ Setup completato. Compila .env.local e poi: npm run dev"
echo "📖 Leggi README.md per le istruzioni complete"
