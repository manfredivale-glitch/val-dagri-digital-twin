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
# --- 1. CONFIGURAZIONE INPUT AGGIUNTIVI E COLTURE ---
st.sidebar.subheader("Approvvigionamento Biomassa")
# Slider per prelevare biomassa dai boschi confinanti (ton/ha)
biomassa_forestale = st.sidebar.slider("Biomassa da boschi confinanti (ton/ha)", 0, 50, 10)

coltura = st.sidebar.selectbox("Seleziona Coltura", ["Cereali Antichi", "Mandorle", "Orticole Premium", "Mix Biodiversità"])

config = {
    "Cereali Antichi": {"prezzo": 160, "costo_base": 500, "risp_biochar": 1.1, "fabbisogno_irr": 400, "residuo_biomassa": 5.0},
    "Mandorle": {"prezzo": 450, "costo_base": 1200, "risp_biochar": 1.4, "fabbisogno_irr": 1200, "residuo_biomassa": 3.0},
    "Orticole Premium": {"prezzo": 350, "costo_base": 1500, "risp_biochar": 1.6, "fabbisogno_irr": 2500, "residuo_biomassa": 1.5},
    "Mix Biodiversità": {"prezzo": 280, "costo_base": 700, "risp_biochar": 1.3, "fabbisogno_irr": 600, "residuo_biomassa": 8.0}
}
c = config[coltura]

# --- 2. LOGICA DI AUTOPRODUZIONE E REALISMO ---
data = []
som = 1.5 
for anno in range(1, 6):
    som += 0.15 # Incremento organico annuo (prudenziale per climi caldi)
    
    # Bilancio Biomassa: quanto ne produciamo noi + quanto ne prendiamo dal bosco
    biomassa_totale_disponibile = c["residuo_biomassa"] + biomassa_forestale
    
    # Resa pirolisi (25%): ogni 4 ton di biomassa = 1 ton biochar
    biochar_producibile_in_loco = biomassa_totale_disponibile / 4
    
    # Se l'utente vuole più biochar (biochar_input) di quello producibile, paga logistica esterna
    # Se invece ne avanza, ipotizziamo un risparmio o vendita (qui semplificato a costo 0)
    deficit_biochar = max(0, biochar_input - biochar_producibile_in_loco)
    costo_logistica_esterna = deficit_biochar * 120 # 120€/t costo logistico realistico
    
    # Calcolo ritenzione e resa
    ritenzione_idrica = (som * 180) + (biochar_input * 3)
    
    # Fabbisogno idrico che scende grazie alla spugna nel suolo
    fabbisogno_esterno = max(100, c["fabbisogno_irr"] - (ritenzione_idrica * 1.5))
    costo_acqua_annuo = fabbisogno_esterno * costo_acqua
    
    # Efficienza input e risparmio chimica
    risparmio_input = biochar_input * 15
    costo_op_netto = c["costo_base"] + costo_logistica_esterna - risparmio_input
    
    # Calcolo Resa e Margine (MOL)
    # Nota: la resa è limitata dalla capacità biologica della pianta
    resa_effettiva = 4.5 * min(c["risp_biochar"], ritenzione_idrica / 250)
    mol = (resa_effettiva * c["prezzo"]) - costo_acqua_annuo - costo_op_netto
    
    data.append([anno, som, ritenzione_idrica, resa_effettiva, mol])

df = pd.DataFrame(data, columns=['Anno', 'SOM_%', 'Water_m3', 'Resa_t', 'MOL_Euro'])st.subheader("Evoluzione Economica ed Ecologica")
col1, col2 = st.columns(2)
col1.metric("Resa Stimata (t/ha)", round(df['Resa_t'].iloc[-1], 2))
col2.metric("MOL Finale (€/ha)", f"{round(df['MOL_Euro'].iloc[-1], 0)}€")

st.line_chart(df.set_index('Anno')[['Water_m3', 'MOL_Euro']])

st.write("Questo modello simula come lo stock di carbonio (SOM + Biochar) de-rischia il cash flow riducendo la dipendenza da input esterni.")
