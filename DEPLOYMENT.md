# Tale Sales Dashboard - Deployment Guide

## Live URL (quando sarà deployato)
Verrà fornito qui dopo il deployment su Streamlit Cloud.

## Deployment Steps

### 1. Accedi a Streamlit Cloud
1. Vai a https://streamlit.io/cloud
2. Clicca "Sign in with GitHub"
3. Autorizza Streamlit con il tuo account GitHub

### 2. Deploy l'app
1. Clicca "New app"
2. Seleziona:
   - Repository: `simocors/telesales-auto-callback`
   - Branch: `main`
   - Main file path: `tale_sales_dashboard.py`
3. Clicca "Deploy!"

### 3. Configura Supabase (OPZIONALE per persistenza)
1. Vai a https://supabase.com e registrati
2. Crea un nuovo project
3. Nel Streamlit Cloud dashboard dell'app:
   - Clicca "Settings" → "Secrets"
   - Aggiungi:
     ```
     SUPABASE_URL = "https://[YOUR_PROJECT].supabase.co"
     SUPABASE_KEY = "[YOUR_API_KEY]"
     ```
4. Redeploy l'app

## Come usarla

### Simone (Control Room)
- Accedi al Dashboard per vedere KPI
- Sezione "Simone - Assetti" per aggiornare saldo, costi, target

### Leonardo (Data Client)
- Sezione "Leonardo - Clienti" per aggiornare dati cliente
- Compila: retainer, pagato, app consegnate, status

### Niccolò (Sales Pipeline)
- Sezione "Niccolò - Pipeline" per aggiungere prospect
- Traccia: nome, azienda, stage, probabilità

## Note
- Data persiste durante la sessione (browser aperto)
- Senza Supabase: data scompare quando l'app si ricarica
- Con Supabase: data persiste permanentemente
