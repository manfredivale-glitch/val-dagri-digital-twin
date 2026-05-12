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
for anno in range(1, anni + 1):
    som += 0.15 # Incremento rigenerativo
    ritenzione_idrica = (som * 180) + (biochar_input * 3)
    resa = 4.5 * min(1.2, ritenzione_idrica / 300)
    risparmio_idrico = max(0, 400 - (ritenzione_idrica * 0.5))
    costo_tot_acqua = risparmio_idrico * costo_acqua
    mol = (resa * prezzo_premium) - costo_tot_acqua - 800
    data.append([anno, som, ritenzione_idrica, resa, mol])

df = pd.DataFrame(data, columns=['Anno', 'SOM_%', 'Water_m3', 'Resa_t', 'MOL_Euro'])

# Visualizzazione dati
st.subheader("Evoluzione Economica ed Ecologica")
col1, col2 = st.columns(2)
col1.metric("Resa Stimata (t/ha)", round(df['Resa_t'].iloc[-1], 2))
col2.metric("MOL Finale (€/ha)", f"{round(df['MOL_Euro'].iloc[-1], 0)}€")

st.line_chart(df.set_index('Anno')[['Water_m3', 'MOL_Euro']])

st.write("Questo modello simula come lo stock di carbonio (SOM + Biochar) de-rischia il cash flow riducendo la dipendenza da input esterni.")
