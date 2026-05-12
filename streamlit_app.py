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
# --- 1. CONFIGURAZIONE INPUT (SIDEBAR) ---
st.sidebar.header("Parametri di Distretto")
superficie_totale = st.sidebar.number_input("Superficie Totale Progetto (ha)", 10, 5000, 500)
biomassa_forestale = st.sidebar.slider("Biomassa da boschi confinanti (ton/ha)", 0, 50, 10)

st.sidebar.subheader("Infrastruttura Energetica e Idrica")
usa_agrivoltaico = st.sidebar.checkbox("Attiva Agrivoltaico", value=False)
efficienza_permacultura = st.sidebar.slider("Efficienza Raccolta Acqua (Ponds/Swales %)", 0, 50, 20)

coltura = st.sidebar.selectbox("Seleziona Coltura", ["Cereali Antichi", "Mandorle", "Orticole Premium", "Mix Biodiversità"])

# --- 2. DIZIONARIO CONFIGURAZIONE ---
config = {
    "Cereali Antichi": {"prezzo": 160, "costo_base": 500, "risp_biochar": 1.1, "fabbisogno_irr": 400, "residuo_biomassa": 5.0},
    "Mandorle": {"prezzo": 450, "costo_base": 1200, "risp_biochar": 1.4, "fabbisogno_irr": 1200, "residuo_biomassa": 3.0},
    "Orticole Premium": {"prezzo": 350, "costo_base": 1500, "risp_biochar": 1.6, "fabbisogno_irr": 2500, "residuo_biomassa": 1.5},
    "Mix Biodiversità": {"prezzo": 280, "costo_base": 700, "risp_biochar": 1.3, "fabbisogno_irr": 600, "residuo_biomassa": 8.0}
}
c = config[coltura]

# --- 3. LOGICA DI SISTEMA (NEXUS) ---
data = []
som = 1.5 
for anno in range(1, 6):
    som += 0.15
    
    # Effetto Agrivoltaico
    riduzione_evaporazione = 0.75 if usa_agrivoltaico else 1.0
    ricavo_energia_ha = 1800 if usa_agrivoltaico else 0 # Leggermente alzato per includere elasticità storage
    
    # Bilancio Biomassa ed Energia
    biomassa_ha_tot = c["residuo_biomassa"] + biomassa_forestale
    biochar_prodotto_ha = biomassa_ha_tot / 4
    energia_pirolisi_mwh = (biochar_prodotto_ha * superficie_totale) * 2
    
    # Costo acqua dinamico
    costo_acqua_effettivo = max(0.05, costo_acqua - (energia_pirolisi_mwh / 10000))
    
    # Bilancio Idrico
    ritenzione_idrica_ha = (som * 180) + (biochar_input * 3)
    fabbisogno_base = c["fabbisogno_irr"] * riduzione_evaporazione
    fabbisogno_esterno = max(50, fabbisogno_base - (ritenzione_idrica_ha * 1.5) - (fabbisogno_base * efficienza_permacultura / 100))
    
    # Logistica e Biochar
    costo_log_unitario = max(35, 120 - (superficie_totale / 15))
    deficit_biochar = max(0, biochar_input - biochar_prodotto_ha)
    costo_logistica = deficit_biochar * costo_log_unitario
    
    # Calcolo Margine
    resa = 4.5 * min(c["risp_biochar"], ritenzione_idrica_ha / 250)
    ricavi = (resa * c["prezzo"]) + ricavo_energia_ha
    costi = c["costo_base"] + costo_logistica + (fabbisogno_esterno * costo_acqua_effettivo) - (biochar_input * 15)
    
    mol_ha = ricavi - costi
    data.append([anno, som, ritenzione_idrica_ha, resa, mol_ha, costo_acqua_effettivo])

df = pd.DataFrame(data, columns=['Anno', 'SOM_%', 'Water_m3', 'Resa_t', 'MOL_Euro', 'Costo_H2O'])
st.subheader("Evoluzione Economica ed Ecologica")
col1, col2 = st.columns(2)
col1.metric("Resa Stimata (t/ha)", round(df['Resa_t'].iloc[-1], 2))
col2.metric("MOL Finale (€/ha)", f"{round(df['MOL_Euro'].iloc[-1], 0)}€")

st.line_chart(df.set_index('Anno')[['Water_m3', 'MOL_Euro']])

st.write("Questo modello simula come lo stock di carbonio (SOM + Biochar) de-rischia il cash flow riducendo la dipendenza da input esterni.")
