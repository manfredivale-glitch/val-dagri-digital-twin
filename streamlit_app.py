import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random

st.title("🌱 Val d’Agri Digital Twin - Biodiversity Factory")
st.sidebar.header("Parametri di Simulazione")

# --- 1. CONFIGURAZIONE AVANZATA (SIDEBAR) ---
st.sidebar.subheader("Tipologia Pedologica")

soil_type = st.sidebar.selectbox(
    "Tipo di suolo",
    [
        "Sandy Degraded",
        "Clay Agricultural",
        "Mediterranean Calcareous",
        "Organic High Carbon",
        "Contaminated Brownfield"
    ]
)

soil_config = {
    "Sandy Degraded": {
        "som_init": 0.8,
        "water_factor": 0.6,
        "fertility_factor": 0.7,
        "contamination": 0.1
    },
    "Clay Agricultural": {
        "som_init": 1.5,
        "water_factor": 1.0,
        "fertility_factor": 1.0,
        "contamination": 0.0
    },
    "Mediterranean Calcareous": {
        "som_init": 1.2,
        "water_factor": 0.8,
        "fertility_factor": 0.9,
        "contamination": 0.0
    },
    "Organic High Carbon": {
        "som_init": 2.8,
        "water_factor": 1.4,
        "fertility_factor": 1.3,
        "contamination": 0.0
    },
    "Contaminated Brownfield": {
        "som_init": 0.9,
        "water_factor": 0.7,
        "fertility_factor": 0.5,
        "contamination": 0.8
    }
}

soil = soil_config[soil_type]

st.sidebar.header("Parametri di Scala e Ottimizzazione")
biochar_input = st.sidebar.slider("Biochar aggiunto (ton/ha)", 0, 30, 10)
costo_acqua = st.sidebar.slider("Costo Energia/Acqua (€/m3)", 0.1, 1.0, 0.45)
superficie_totale = st.sidebar.number_input("Superficie Progetto (ha)", 10, 5000, 500)
biomassa_forestale = st.sidebar.slider("Biomassa dai boschi (ton/ha)", 0, 50, 10)

st.sidebar.subheader("Nexus Energetico")
copertura_agrivoltaico = st.sidebar.slider("Copertura Agrivoltaico (%)", 0, 100, 0)
efficienza_permacultura = st.sidebar.slider("Efficienza Permacultura (%)", 0, 100, 20)

coltura = st.sidebar.selectbox("Seleziona Coltura", ["Cereali Antichi", "Mandorle", "Orticole Premium", "Mix Biodiversità"])

# Definiamo i cursori del PREZZO fuori dal ciclo
st.sidebar.subheader("Dinamiche di Mercato")
premium_factor = st.sidebar.slider(f"Premium Factor ({coltura})", 1.0, 2.0, 1.2)
premium_factor_time = st.sidebar.slider(f"Premium Factor Time ({coltura})", 1.0, 1.5, 1.1)

st.sidebar.subheader("Scenario di Investimento")

scenario = st.sidebar.selectbox(
    "Seleziona scenario",
    ["Base Case", "Upside Case", "Downside Case"]
)

config = {
    "Cereali Antichi": {"prezzo": 160, "costo_base": 500, "risp_biochar": 1.1, "fabbisogno_irr": 400, "residuo_biomassa": 5.0},
    "Mandorle": {"prezzo": 450, "costo_base": 1200, "risp_biochar": 1.4, "fabbisogno_irr": 1200, "residuo_biomassa": 3.0},
    "Orticole Premium": {"prezzo": 350, "costo_base": 1500, "risp_biochar": 1.6, "fabbisogno_irr": 2500, "residuo_biomassa": 1.5},
    "Mix Biodiversità": {"prezzo": 280, "costo_base": 700, "risp_biochar": 1.3, "fabbisogno_irr": 600, "residuo_biomassa": 8.0}
}
c = config[coltura]
scenario_config = {
    "Base Case": {
        "climate": 1.0,
        "price": 1.0,
        "price_trend": 1.0,
        "remediation": 1.0,
        "bad_bias": 0.33
    },
    "Upside Case": {
        "climate": 1.1,
        "price": 1.2,
        "price_trend": 1.15,
        "remediation": 1.2,
        "bad_bias": 0.2
    },
    "Downside Case": {
        "climate": 0.9,
        "price": 0.85,
        "price_trend": 0.9,
        "remediation": 0.8,
        "bad_bias": 0.5
    }
}

sc = scenario_config[scenario]
# --- 2. LOGICA DI CALCOLO DINAMICA ---
data = []
som = soil["som_init"]
contamination_factor = soil["contamination"]

for anno in range(1, 6):
    
    r = random.random()

    if r < sc["bad_bias"]:
        shock = "bad"
    elif r < sc["bad_bias"] + 0.3:
        shock = "normal"
    else:
        shock = "good"
    climate_multiplier = (
        1.1 if shock == "good" else
        0.8 if shock == "bad" else
        1.0
    )

    climate_multiplier *= sc["climate"]
    remediation_gain = min(0.2, biochar_input * 0.01) * sc["remediation"]
    contamination_factor = contamination_factor * (1 - remediation_gain)
    contamination_factor = max(0, contamination_factor)

    soil_recovery_bonus = (1 - contamination_factor)
    som += 0.08 + (biochar_input * 0.003)    
    riduzione_evap = 1.0 - (0.4 * copertura_agrivoltaico / 100)
    ricavo_energia_ha = 2200 * (copertura_agrivoltaico / 100)
    bonus_rigenerazione = max(0, 500 * (1 - copertura_agrivoltaico/100)) if biochar_input > 15 else 0
    
    costo_h2o_base = costo_acqua * (3.0 if costo_acqua > 0.5 else 1.0)
    ritenzione_idrica = (som * 180) + (biochar_input * 3)
    fabbisogno_base = c["fabbisogno_irr"] * riduzione_evap
    
    risparmio_perm = fabbisogno_base * (efficienza_permacultura / 100)
    fabbisogno_est = max(50, fabbisogno_base - (ritenzione_idrica * 1.5) - risparmio_perm)
    
    biochar_auto = (c["residuo_biomassa"] + biomassa_forestale) / 4
    costo_log_unitario = 150 * (0.8 ** (superficie_totale / 500))
    deficit = max(0, biochar_input - biochar_auto)
    costo_logistica = deficit * costo_log_unitario
    
    energia_pirolisi = (biochar_auto * superficie_totale) * 2
    costo_h2o_finale = max(0.05, costo_h2o_base - (energia_pirolisi / 10000))
    
    fattore_suolo = 1 - (1 / (1 + (ritenzione_idrica / 300)))
    resa = (
        4.5
        * (1 + fattore_suolo)
        * c["risp_biochar"]
        * soil["fertility_factor"]
        * soil_recovery_bonus
        * climate_multiplier
    )
    market_multiplier = sc["price"] * premium_factor
    time_multiplier = 1 + (premium_factor_time - 1) * (anno - 1)

    prezzo_effettivo = c["prezzo"] * market_multiplier * time_multiplier
    mol_ha = (resa * prezzo_effettivo) + ricavo_energia_ha + bonus_rigenerazione - c["costo_base"] - costo_logistica - (fabbisogno_est * costo_h2o_finale)
    data.append([anno, som, ritenzione_idrica, resa, mol_ha])

# --- 3. OUTPUT ---
df = pd.DataFrame(data, columns=['Anno', 'SOM_%', 'Water_m3', 'Resa_t', 'MOL_Euro'])

st.subheader("Evoluzione Economica ed Ecologica")

if len(df) > 0:
    last = df.iloc[-1]

    st.subheader("📊 Investment View Layer")

    yield_kpi = last["Resa_t"]
    margin_kpi = last["MOL_Euro"]
    water_kpi = last["Water_m3"]
    soil_kpi = last["SOM_%"]

    avg_margin = df["MOL_Euro"].mean()
    volatility = df["MOL_Euro"].std()

    investment_score = (
        (avg_margin / 1000) * 0.4 +
        (yield_kpi) * 0.3 +
        (soil_kpi) * 0.2 -
        (volatility / 500) * 0.1
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Yield (t/ha)", round(yield_kpi, 2))
    col1.metric("Soil Health (SOM)", round(soil_kpi, 2))

    col2.metric("Margin (€/ha)", f"{round(margin_kpi, 0)}€")
    col2.metric("Avg Margin", f"{round(avg_margin, 0)}€")

    col3.metric("Water Stress", round(water_kpi, 2))
    col3.metric("Volatility", round(volatility, 0))

    st.metric("Investment Score", round(investment_score, 2))

    if investment_score > 5:
        st.success("🟢 High attractiveness")
    elif investment_score > 3:
        st.warning("🟡 Medium attractiveness")
    else:
        st.error("🔴 Low attractiveness")

else:
    st.warning("Simulazione non disponibile: nessun dato generato.")

st.line_chart(df.set_index('Anno')[['Water_m3', 'MOL_Euro']])
