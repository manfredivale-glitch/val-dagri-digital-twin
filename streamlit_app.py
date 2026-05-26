import streamlit as st
import pandas as pd

# --- 1. MOTORE DI CALCOLO (Con VAN integrato) ---
def calcola_van(flussi_cassa, tasso_sconto=0.05):
    """Calcola il Valore Attuale Netto dei flussi di cassa."""
    van = sum([flusso / ((1 + tasso_sconto) ** anno) for anno, flusso in enumerate(flussi_cassa, 1)])
    return van

def calcola_scenario(params, config):
    data = []
    som = 1.5
    for anno in range(1, 6):
        som += 0.15
        
        # Logica di calcolo
        riduzione_evap = 1.0 - (0.4 * params['agrivoltaico'] / 100)
        ricavo_energia_ha = 2200 * (params['agrivoltaico'] / 100)
        bonus = max(0, 500 * (1 - params['agrivoltaico']/100)) if params['biochar'] > 15 else 0
        
        ritenzione = (som * 180) + (params['biochar'] * 3)
        fabbisogno_base = config['fabbisogno_irr'] * riduzione_evap
        risparmio_perm = fabbisogno_base * (params['permacultura'] / 100)
        fabbisogno_est = max(50, fabbisogno_base - (ritenzione * 1.5) - risparmio_perm)
        
        # Risultato operativo (MOL)
        resa = 4.5 * min(config['risp_biochar'], ritenzione / 250)
        mol = (resa * config['prezzo']) + ricavo_energia_ha + bonus - config['costo_base'] - (fabbisogno_est * params['costo_h2o'])
        
        data.append({'Anno': anno, 'MOL_Euro': mol})
    return pd.DataFrame(data)

# --- 2. CONFIGURAZIONI ---
config_colture = {
    "Cereali Antichi": {"prezzo": 160, "costo_base": 500, "risp_biochar": 1.1, "fabbisogno_irr": 400},
    "Mandorle": {"prezzo": 450, "costo_base": 1200, "risp_biochar": 1.4, "fabbisogno_irr": 1200},
    "Orticole Premium": {"prezzo": 350, "costo_base": 1500, "risp_biochar": 1.6, "fabbisogno_irr": 2500}
}

# --- 3. INTERFACCIA STREAMLIT ---
st.title("🌱 Digital Twin: Progetto RAP - Val d'Agri")

with st.sidebar:
    st.header("Parametri Progetto")
    biochar = st.slider("Biochar (ton/ha)", 0, 30, 10)
    agrivoltaico = st.slider("Agrivoltaico (%)", 0, 100, 20)
    costo_h2o = st.slider("Costo Acqua (€/m3)", 0.1, 1.0, 0.45)
    coltura = st.selectbox("Coltura", list(config_colture.keys()))

# --- 4. ANALISI E KPI ---
params_rap = {'biochar': biochar, 'agrivoltaico': agrivoltaico, 'costo_h2o': costo_h2o, 'permacultura': 20}
params_base = {'biochar': 0, 'agrivoltaico': 0, 'costo_h2o': costo_h2o, 'permacultura': 0}

df_rap = calcola_scenario(params_rap, config_colture[coltura])
df_base = calcola_scenario(params_base, config_colture[coltura])

# Calcolo VAN (assumendo tasso di sconto 5%)
van_rap = calcola_van(df_rap['MOL_Euro'])
van_base = calcola_van(df_base['MOL_Euro'])

st.subheader("Confronto: Scenario RAP vs Standard")
st.line_chart(pd.DataFrame({'RAP': df_rap['MOL_Euro'], 'Standard': df_base['MOL_Euro']}))

col1, col2 = st.columns(2)
col1.metric("VAN Progetto RAP", f"{round(van_rap, 0)} €/ha")
col2.metric("Valore Aggiunto (Delta VAN)", f"{round(van_rap - van_base, 0)} €/ha")
