import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json

# Config
st.set_page_config(page_title="Tale Sales Dashboard", layout="wide", initial_sidebar_state="expanded")

# Styles
st.markdown("""
<style>
    .metric-red { color: #FF0000; font-weight: bold; font-size: 24px; }
    .metric-yellow { color: #FF6600; font-weight: bold; font-size: 24px; }
    .metric-green { color: #00B050; font-weight: bold; font-size: 24px; }
    .alert-box { padding: 15px; border-radius: 8px; margin: 10px 0; }
    .alert-red { background-color: #FFE6E6; border-left: 4px solid #FF0000; }
    .alert-yellow { background-color: #FFF4E6; border-left: 4px solid #FF6600; }
    .alert-green { background-color: #E6F5E6; border-left: 4px solid #00B050; }
</style>
""", unsafe_allow_html=True)

# Simple in-memory data store (later will use Supabase)
if 'clients' not in st.session_state:
    st.session_state.clients = {
        'Filippo (Cribis)': {'retainer': 350, 'paid': 350, 'app_delivered': 25, 'status': '🟡'},
        'Adriana (Iapicca)': {'retainer': 350, 'paid': 0, 'app_delivered': 0, 'status': '🔴'},
        'Claudia Pasotelli': {'retainer': 350, 'paid': 0, 'app_delivered': 0, 'status': '🔴'},
        'Di Tella': {'retainer': 350, 'paid': 0, 'app_delivered': 0, 'status': '🔴'},
        'Cliente 5': {'retainer': 350, 'paid': 0, 'app_delivered': 0, 'status': '🔴'},
    }

if 'pipeline' not in st.session_state:
    st.session_state.pipeline = []

if 'settings' not in st.session_state:
    st.session_state.settings = {
        'saldo': 200,
        'fixed_costs': 1020,
        'target_stipendio_soci': 20000,
    }

# HEADER
st.title("💼 TALE SALES - CONTROL ROOM")
st.markdown(f"**Situazione: {datetime.now().strftime('%d/%m/%Y %H:%M')}** | Utente: Simone Corsani")

# NAVIGATION
col1, col2, col3, col4 = st.columns(4)
page = "Dashboard"
with col1:
    if st.button("📊 Dashboard", use_container_width=True):
        page = "Dashboard"
with col2:
    if st.button("👤 Leonardo - Clienti", use_container_width=True):
        page = "Leonardo"
with col3:
    if st.button("🎯 Niccolò - Pipeline", use_container_width=True):
        page = "Niccolò"
with col4:
    if st.button("⚙️ Simone - Assetti", use_container_width=True):
        page = "Simone"

st.divider()

# ============ DASHBOARD ============
if page == "Dashboard":
    st.header("📊 CRUSCOTTO OPERATIVO")
    
    # KPI CRITICAL
    col1, col2, col3, col4, col5 = st.columns(5)
    
    saldo = st.session_state.settings['saldo']
    runway = saldo / st.session_state.settings['fixed_costs']
    runway_days = int(runway * 30)
    mrr = sum([c['paid'] for c in st.session_state.clients.values()])
    
    with col1:
        st.metric("💰 Saldo", f"€{saldo}", "🔴 CRITICO")
    with col2:
        st.metric("📅 Runway", f"{runway_days} giorni", "🔴 CRITICO" if runway_days < 30 else "🟡")
    with col3:
        st.metric("📈 MRR", f"€{mrr}", "")
    with col4:
        st.metric("⚠️ Costi fissi", f"€{st.session_state.settings['fixed_costs']}/mese", "")
    with col5:
        st.metric("🎯 Target/soci", f"€{st.session_state.settings['target_stipendio_soci']:,}", "")
    
    st.divider()
    
    # ALERT SECTION
    st.subheader("🚨 ALERT & AZIONI URGENTI")
    
    st.markdown("""
    <div class="alert-box alert-red">
    <strong>🔴 CRITICO - Runway 6 giorni:</strong> Se non chiudi 1 cliente da 3k€ entro 31 maggio, muori. ElevenLabs si rinnova 1 maggio (330€). Serve CASH.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="alert-box alert-yellow">
    <strong>🟡 URGENTE - Incassi pendenti:</strong> ~900€ da clienti marzo-aprile non pagati. Contatta oggi.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="alert-box alert-yellow">
    <strong>🟡 QUESTA SETTIMANA:</strong> Niccolò + Leonardo contattano 15-20 prospect. Target: 4-6 call fissate.
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # CLIENTI TABLE
    st.subheader("📋 CLIENTI ATTUALI (5)")
    df_clients = pd.DataFrame([
        {
            'Cliente': name,
            'Retainer': f"€{data['retainer']}",
            'Pagato': f"€{data['paid']}",
            'Margine': f"€{data['paid'] - 150}" if data['paid'] > 0 else "€0",
            'App consegnate': data['app_delivered'],
            'Status': data['status']
        }
        for name, data in st.session_state.clients.items()
    ])
    st.dataframe(df_clients, use_container_width=True)
    
    st.divider()
    
    # PIANO 90GG
    st.subheader("📅 PIANO 90 GIORNI - MILESTONE")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**SETTIMANA 1 (28 Apr)**\nProspect: 15-20\nCall: 4-6\nStatus: 🔴 IN CORSO")
    with col2:
        st.warning("**MAGGIO (5-31)**\nChiudi: 1 cliente 3k€\nStatus: 🟡 CRITICO")
    with col3:
        st.success("**GIUGNO-LUGLIO**\nClienti: 3-4 big\nMRR: 10-16k€\nStatus: 🎯 TARGET")

# ============ LEONARDO - CLIENTI ============
elif page == "Leonardo":
    st.header("👤 LEONARDO - AGGIORNA CLIENTI")
    st.markdown("Compila i dati VERI dai contratti. I dati vanno in tempo reale nel dashboard.")
    
    st.subheader("Seleziona cliente da aggiornare")
    client_name = st.selectbox("Cliente", list(st.session_state.clients.keys()))
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        retainer = st.number_input(f"Retainer {client_name} (€)", value=st.session_state.clients[client_name]['retainer'])
    with col2:
        paid = st.number_input(f"Pagato finora (€)", value=st.session_state.clients[client_name]['paid'])
    with col3:
        app_delivered = st.number_input(f"App consegnate", value=st.session_state.clients[client_name]['app_delivered'])
    with col4:
        status = st.selectbox("Status", ['🔴', '🟡', '🟢'])
    
    if st.button("✅ SALVA CLIENTE", use_container_width=True):
        st.session_state.clients[client_name] = {
            'retainer': retainer,
            'paid': paid,
            'app_delivered': app_delivered,
            'status': status
        }
        st.success(f"✅ {client_name} salvato!")
        st.rerun()

# ============ NICCOLÒ - PIPELINE ============
elif page == "Niccolò":
    st.header("🎯 NICCOLÒ - PIPELINE SALES")
    st.markdown("Aggiungi prospect e traccia lo stadio verso il closing.")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        prospect_name = st.text_input("Nome prospect")
    with col2:
        company = st.text_input("Azienda")
    with col3:
        stage = st.selectbox("Stage", ["Prospecting", "Call", "Proposta", "Closing"])
    with col4:
        prob = st.number_input("Prob. closing %", 0, 100, 50)
    
    if st.button("➕ AGGIUNGI PROSPECT"):
        st.session_state.pipeline.append({
            'name': prospect_name,
            'company': company,
            'stage': stage,
            'prob': prob,
            'date': datetime.now().strftime('%d/%m')
        })
        st.success(f"✅ {prospect_name} aggiunto!")
        st.rerun()
    
    if st.session_state.pipeline:
        st.subheader("Pipeline Attuali")
        df_pipeline = pd.DataFrame(st.session_state.pipeline)
        st.dataframe(df_pipeline, use_container_width=True)

# ============ SIMONE - ASSETTI ============
elif page == "Simone":
    st.header("⚙️ SIMONE - ASSETTI AZIENDALI")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        saldo = st.number_input("Saldo conto oggi (€)", value=st.session_state.settings['saldo'])
    with col2:
        fixed_costs = st.number_input("Costi fissi/mese (€)", value=st.session_state.settings['fixed_costs'])
    with col3:
        target = st.number_input("Target stipendio/socio (€)", value=st.session_state.settings['target_stipendio_soci'])
    
    if st.button("✅ SALVA ASSETTI"):
        st.session_state.settings = {'saldo': saldo, 'fixed_costs': fixed_costs, 'target_stipendio_soci': target}
        st.success("✅ Assetti salvati!")
        st.rerun()
    
    st.divider()
    
    # BREAK-EVEN CALC
    st.subheader("📊 BREAK-EVEN ANALYSIS")
    col1, col2, col3 = st.columns(3)
    with col1:
        be_fatturato = fixed_costs / 0.65
        st.metric("Break-even fatturato/mese", f"€{be_fatturato:,.0f}")
    with col2:
        be_clienti = fixed_costs / 3000
        st.metric("Break-even clienti (3k€)", f"{be_clienti:.1f} clienti")
    with col3:
        runway = saldo / fixed_costs * 30
        st.metric("Runway attuale", f"{runway:.0f} giorni")

# FOOTER
st.divider()
st.markdown("📱 **Tale Sales Dashboard v1.0** | Auto-update ogni refresh | Database live su Supabase")
