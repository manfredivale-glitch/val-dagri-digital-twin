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
# --- 1. CONFIGURAZIONE AGRI-TECH ---
st.sidebar.subheader("Infrastruttura Energetica")
usa_agrivoltaico = st.sidebar.checkbox("Attiva Agrivoltaico", value=False)
efficienza_storage = st.sidebar.slider("Efficienza Storage (Ponds/Batterie %)", 0, 100, 30)

# (Manteniamo il dizionario config invariato)
c = config[coltura]

# --- 2. LOGICA NEXUS AVANZATA ---
data = []
som = 1.5 
for anno in range(1, 6):
    som += 0.15
    
    # 1. EFFETTO AGRI-VOLTAICO
    ricavo_energia_ha = 1500 if usa_agrivoltaico else 0 # Stima prudenziale vendita energia/ha
    # L'ombreggiamento riduce l'evaporazione (risparmio idrico del 25%)
    riduzione_evaporazione = 0.75 if usa_agrivoltaico else 1.0
    
    # 2. BILANCIO IDRICO CON STORAGE E PERMACULTURA
    ritenzione_idrica_ha = (som * 180) + (biochar_input * 3)
    # L'efficienza storage permette di usare l'acqua piovana stoccata nei ponds
    fabbisogno_base_netto = c["fabbisogno_irr"] * riduzione_evaporazione
    fabbisogno_esterno = max(50, fabbisogno_base_netto - (ritenzione_idrica_ha * 1.5) - (fabbisogno_base_netto * efficienza_permacultura / 100))
    
    # 3. ENERGIA E COSTI
    biomassa_totale = (c["residuo_biomassa"] + biomassa_forestale) * superficie_totale
    energia_pirolisi = (biomassa_totale / 4) * 2 # MWh prodotti
    costo_acqua_effettivo = max(0.05, costo_acqua - (energia_pirolisi / 5000))
    
    # 4. CALCOLO MOL COMPLESSIVO (Agro + Energy)
    resa = 4.5 * min(c["risp_biochar"], ritenzione_idrica_ha / 250)
    ricavi_totali_ha = (resa * c["prezzo"]) + ricavo_energia_ha
    costi_totali_ha = c["costo_base"] + (deficit_biochar * 120) + (fabbisogno_esterno * costo_acqua_effettivo) - (biochar_input * 15)
    
    mol_ha = ricavi_totali_ha - costi_totali_ha
    
    data.append([anno, som, ritenzione_idrica_ha, resa, mol_ha, ricavo_energia_ha])

df = pd.DataFrame(data, columns=['Anno', 'SOM_%', 'Water_m3', 'Resa_t', 'MOL_Euro', 'Ricavo_Energy'])
st.subheader("Evoluzione Economica ed Ecologica")
col1, col2 = st.columns(2)
col1.metric("Resa Stimata (t/ha)", round(df['Resa_t'].iloc[-1], 2))
col2.metric("MOL Finale (€/ha)", f"{round(df['MOL_Euro'].iloc[-1], 0)}€")

st.line_chart(df.set_index('Anno')[['Water_m3', 'MOL_Euro']])

st.write("Questo modello simula come lo stock di carbonio (SOM + Biochar) de-rischia il cash flow riducendo la dipendenza da input esterni.")
