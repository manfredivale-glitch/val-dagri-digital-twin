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
# --- BLOCCO 1: SCELTA DELLA COLTURA ---
# --- 1. CONFIGURAZIONE DELLE COLTURE (Fabbisogni e Prezzi) ---
coltura = st.sidebar.selectbox("Seleziona Coltura", ["Cereali Antichi", "Mandorle", "Orticole Premium"])

config = {
    "Cereali Antichi": {
        "prezzo": 120, 
        "costo_base": 500, 
        "risposta_biochar": 1.1,
        "fabbisogno_irriguo_base": 400  # m3/ha (basso)
    },
    "Mandorle": {
        "prezzo": 450, 
        "costo_base": 1200, 
        "risposta_biochar": 1.4,
        "fabbisogno_irriguo_base": 1200 # m3/ha (alto)
    },
    "Orticole Premium": {
        "prezzo": 350, 
        "costo_base": 1500, 
        "risposta_biochar": 1.6,
        "fabbisogno_irriguo_base": 2500 # m3/ha (molto alto)
    }
}
c = config[coltura]

# --- 2. LOGICA DI CALCOLO DINAMICA ---
data = []
som = 1.5 
for anno in range(1, 6):
    som += 0.15
    
    # Stock idrico (la "spugna")
    ritenzione_idrica = (som * 180) + (biochar_input * 3)
    
    # RISPOSTA ALL'ACQUA: 
    # Calcoliamo quanto dell'acqua necessaria viene coperta dalla "spugna"
    # Più biochar metti, più abbatti il fabbisogno esterno
    fabbisogno_esterno = max(100, c["fabbisogno_irriguo_base"] - (ritenzione_idrica * 1.8))
    costo_acqua_annuo = fabbisogno_esterno * costo_acqua
    
    # Efficienza input (concimi)
    risparmio_input = biochar_input * 12
    costo_op_netto = c["costo_base"] - risparmio_input
    
    # Resa
    resa = 4.5 * min(c["risposta_biochar"], ritenzione_idrica / 250)
    
    # MOL
    ricavi = resa * c["prezzo"]
    mol = ricavi - costo_acqua_annuo - costo_op_netto
    
    data.append([anno, som, ritenzione_idrica, resa, mol])

df = pd.DataFrame(data, columns=['Anno', 'SOM_%', 'Water_m3', 'Resa_t', 'MOL_Euro'])
st.subheader("Evoluzione Economica ed Ecologica")
col1, col2 = st.columns(2)
col1.metric("Resa Stimata (t/ha)", round(df['Resa_t'].iloc[-1], 2))
col2.metric("MOL Finale (€/ha)", f"{round(df['MOL_Euro'].iloc[-1], 0)}€")

st.line_chart(df.set_index('Anno')[['Water_m3', 'MOL_Euro']])

st.write("Questo modello simula come lo stock di carbonio (SOM + Biochar) de-rischia il cash flow riducendo la dipendenza da input esterni.")
