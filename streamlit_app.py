import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("🌱 Val d’Agri Digital Twin - Biodiversity Factory")
st.sidebar.header("Parametri di Simulazione")

# Cursori interattivi per Faleschini
biochar_input = st.sidebar.slider("Biochar aggiunto (ton/ha)", 0, 30, 10)
prezzo_premium = st.sidebar.slider("Prezzo Prodotto Premium (€/ton)", 80, 250, 120)
costo_acqua = st.sidebar.slider("Costo Energia/Acqua (€/m3)", 0.1, 1.0, 0.45)

# La nostra logica di calcolo (semplificata)
anni = 5
som = 1.5
data = []
# --- 1. CONFIGURAZIONE AVANZATA (SIDEBAR) ---
st.sidebar.header("Parametri di Scala e Ottimizzazione")
superficie_totale = st.sidebar.number_input("Superficie Progetto (ha)", 10, 5000, 500)
biomassa_forestale = st.sidebar.slider("Biomassa dai boschi (ton/ha)", 0, 50, 10)

st.sidebar.subheader("Nexus Energetico")
copertura_agrivoltaico = st.sidebar.slider("Copertura Agrivoltaico (%)", 0, 100, 0)
efficienza_permacultura = st.sidebar.slider("Efficienza Permacultura (%)", 0, 100, 20)

coltura = st.sidebar.selectbox("Seleziona Coltura", ["Cereali Antichi", "Mandorle", "Orticole Premium", "Mix Biodiversità"])

config = {
    "Cereali Antichi": {"prezzo": 160, "costo_base": 500, "risp_biochar": 1.1, "fabbisogno_irr": 400, "residuo_biomassa": 5.0},
    "Mandorle": {"prezzo": 450, "costo_base": 1200, "risp_biochar": 1.4, "fabbisogno_irr": 1200, "residuo_biomassa": 3.0},
    "Orticole Premium": {"prezzo": 350, "costo_base": 1500, "risp_biochar": 1.6, "fabbisogno_irr": 2500, "residuo_biomassa": 1.5},
    "Mix Biodiversità": {"prezzo": 280, "costo_base": 700, "risp_biochar": 1.3, "fabbisogno_irr": 600, "residuo_biomassa": 8.0}
}
c = config[coltura]

# --- 2. LOGICA DI CALCOLO DINAMICA (NEXUS COMPLETO) ---
data = []
som = 1.5 
for anno in range(1, 6):
    som += 0.15
    
    # A. Effetto Modulato Agrivoltaico (Ombra e Ricavi)
    riduzione_evap = 1.0 - (0.4 * copertura_agrivoltaico / 100)
    ricavo_energia_ha = 2200 * (copertura_agrivoltaico / 100)
    
    # B. Bonus Rigenerazione (decresce se l'energia diventa predominante)
    bonus_rigenerazione = max(0, 500 * (1 - copertura_agrivoltaico/100)) if biochar_input > 15 else 0
    
    # C. Bilancio Idrico Critico (Siccità e Permacultura)
    costo_h2o_base = costo_acqua * (3.0 if costo_acqua > 0.5 else 1.0)
    ritenzione_idrica = (som * 180) + (biochar_input * 3)
    fabbisogno_base = c["fabbisogno_irr"] * riduzione_evap
    
    # La permacultura agisce sul fabbisogno reale
    risparmio_perm = fabbisogno_base * (efficienza_permacultura / 100)
    fabbisogno_est = max(50, fabbisogno_base - (ritenzione_idrica * 1.5) - risparmio_perm)
    
    # D. Economia di Scala e Biomassa
    biochar_auto = (c["residuo_biomassa"] + biomassa_forestale) / 4
    # Il costo logistico scende all'aumentare della scala
    costo_log_unitario = 150 * (0.8 ** (superficie_totale / 500))
    deficit = max(0, biochar_input - biochar_auto)
    costo_logistica = deficit * costo_log_unitario
    
    # E. Produzione Energetica da Pirolisi (abbatte costo acqua)
    energia_pirolisi = (biochar_auto * superficie_totale) * 2
    costo_h2o_finale = max(0.05, costo_h2o_base - (energia_pirolisi / 10000))
    
    # F. Calcolo Resa (La variabile mancante!)
    resa = 4.5 * min(c["risp_biochar"], ritenzione_idrica / 250)
    
    # G. Margine Operativo Lordo (MOL)
    mol_ha = (resa * c["prezzo"]) + ricavo_energia_ha + bonus_rigenerazione - c["costo_base"] - costo_logistica - (fabbisogno_est * costo_h2o_finale)
    
    data.append([anno, som, ritenzione_idrica, resa, mol_ha])

df = pd.DataFrame(data, columns=['Anno', 'SOM_%', 'Water_m3', 'Resa_t', 'MOL_Euro'])
st.subheader("Evoluzione Economica ed Ecologica")
col1, col2 = st.columns(2)
col1.metric("Resa Stimata (t/ha)", round(df['Resa_t'].iloc[-1], 2))
col2.metric("MOL Finale (€/ha)", f"{round(df['MOL_Euro'].iloc[-1], 0)}€")

st.line_chart(df.set_index('Anno')[['Water_m3', 'MOL_Euro']])

st.write("Questo modello simula come lo stock di carbonio (SOM + Biochar) de-rischia il cash flow riducendo la dipendenza da input esterni.")
