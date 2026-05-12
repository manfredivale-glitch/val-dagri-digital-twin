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
coltura = st.sidebar.selectbox("Seleziona Coltura", ["Cereali Antichi", "Mandorle", "Biodiversità Factory Mix"])

# Parametri specifici per coltura (Efficienza e Prezzi)
config = {
    "Cereali Antichi": {"prezzo": 120, "costo_base": 500, "risposta_biochar": 1.1},
    "Mandorle": {"prezzo": 450, "costo_base": 1200, "risposta_biochar": 1.4},
    "Biodiversità Factory Mix": {"prezzo": 300, "costo_base": 800, "risposta_biochar": 1.2}
}
c = config[coltura]

# --- BLOCCO 2: LOGICA RAFFINATA (Il Cuore del Digital Twin) ---
data = []
som = 1.5 # Sostanza organica iniziale
for anno in range(1, 6):
    som += 0.15 
    
    # Lo stock idrico beneficia della porosità del biochar
    ritenzione_idrica = (som * 180) + (biochar_input * 3)
    
    # 1. Efficienza Nutritiva: il biochar riduce il costo dei concimi (meno sprechi)
    risparmio_input = biochar_input * 12 # Risparmiamo 12€/ton di biochar in concimi
    costo_op_netto = c["costo_base"] - risparmio_input
    
    # 2. Resilienza Resa: la resa è protetta dallo stock idrico
    resa = 4.5 * min(c["risposta_biochar"], ritenzione_idrica / 250)
    
    # 3. Risparmio Idrico: meno pompaggio dall'esterno
    fabbisogno_esterno = max(0, 400 - (ritenzione_idrica * 0.6))
    costo_acqua_tot = fabbisogno_esterno * costo_acqua
    
    # 4. Calcolo Margine (MOL)
    ricavi = resa * c["prezzo"]
    mol = ricavi - costo_acqua_tot - costo_op_netto
    
    data.append([anno, som, ritenzione_idrica, resa, mol])

# --- BLOCCO 3: OUTPUT ---
df = pd.DataFrame(data, columns=['Anno', 'SOM_%', 'Water_m3', 'Resa_t', 'MOL_Euro'])

df = pd.DataFrame(data, columns=['Anno', 'SOM_%', 'Water_m3', 'Resa_t', 'MOL_Euro'])

# Visualizzazione dati
st.subheader("Evoluzione Economica ed Ecologica")
col1, col2 = st.columns(2)
col1.metric("Resa Stimata (t/ha)", round(df['Resa_t'].iloc[-1], 2))
col2.metric("MOL Finale (€/ha)", f"{round(df['MOL_Euro'].iloc[-1], 0)}€")

st.line_chart(df.set_index('Anno')[['Water_m3', 'MOL_Euro']])

st.write("Questo modello simula come lo stock di carbonio (SOM + Biochar) de-rischia il cash flow riducendo la dipendenza da input esterni.")
