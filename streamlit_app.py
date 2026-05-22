import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# =========================================================
# VAL D’AGRI DIGITAL TWIN V2
# Stochastic Regenerative Resilience Engine
# =========================================================

st.set_page_config(layout="wide")

st.title("🌱 Val d’Agri Digital Twin V2")
st.subheader("Regenerative Resilience Engine")

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("Scenario Configuration")

coltura = st.sidebar.selectbox(
    "Crop System",
    [
        "Cereali Antichi",
        "Mandorle",
        "Orticole Premium",
        "Mix Biodiversità"
    ]
)

biochar_input = st.sidebar.slider(
    "Biochar Added (t/ha)",
    0,
    40,
    10
)

superficie_totale = st.sidebar.number_input(
    "Project Area (ha)",
    20,
    10000,
    500
)

copertura_agrivoltaico = st.sidebar.slider(
    "Agrivoltaic Coverage (%)",
    0,
    100,
    20
)

efficienza_permacultura = st.sidebar.slider(
    "Permaculture Efficiency (%)",
    0,
    100,
    25
)

biomassa_forestale = st.sidebar.slider(
    "Forest Biomass Input (t/ha)",
    0,
    50,
    10
)

carbon_price = st.sidebar.slider(
    "Carbon Price (€ / tCO2e)",
    0,
    300,
    80
)

water_cost = st.sidebar.slider(
    "Water/Energy Cost (€ / m3)",
    0.1,
    2.0,
    0.45
)

scenario = st.sidebar.selectbox(
    "Climate Scenario",
    [
        "Normal",
        "Moderate Drought",
        "Extreme Drought",
        "Flood Variability",
        "Energy Crisis"
    ]
)

simulazioni = st.sidebar.slider(
    "Monte Carlo Simulations",
    50,
    1000,
    250
)

anni = st.sidebar.slider(
    "Simulation Horizon (Years)",
    5,
    20,
    10
)

# =========================================================
# CROP CONFIG
# =========================================================

config = {
    "Cereali Antichi": {
        "prezzo": 160,
        "costo_base": 500,
        "resa_base": 4.5,
        "fabbisogno_irr": 400,
        "residuo_biomassa": 5.0
    },
    "Mandorle": {
        "prezzo": 450,
        "costo_base": 1200,
        "resa_base": 3.0,
        "fabbisogno_irr": 1200,
        "residuo_biomassa": 3.0
    },
    "Orticole Premium": {
        "prezzo": 350,
        "costo_base": 1500,
        "resa_base": 7.0,
        "fabbisogno_irr": 2500,
        "residuo_biomassa": 1.5
    },
    "Mix Biodiversità": {
        "prezzo": 280,
        "costo_base": 700,
        "resa_base": 5.5,
        "fabbisogno_irr": 600,
        "residuo_biomassa": 8.0
    }
}

c = config[coltura]

# =========================================================
# CLIMATE SHOCK PARAMETERS
# =========================================================

scenario_shocks = {
    "Normal": (-0.10, 0.10),
    "Moderate Drought": (-0.25, 0.05),
    "Extreme Drought": (-0.45, 0.02),
    "Flood Variability": (-0.35, 0.15),
    "Energy Crisis": (-0.15, 0.08)
}

shock_min, shock_max = scenario_shocks[scenario]

# =========================================================
# STORAGE
# =========================================================

results = []

# =========================================================
# MONTE CARLO ENGINE
# =========================================================

for sim in range(simulazioni):

    som = 1.5
    cumulative_cashflow = 0

    for anno in range(1, anni + 1):

        # =================================================
        # SOIL ORGANIC MATTER EVOLUTION
        # =================================================

        som_growth = np.random.normal(0.12, 0.03)

        if biochar_input > 15:
            som_growth += 0.03

        som += max(0.03, som_growth)

        # Saturation effect
        if som > 4:
            som_growth *= 0.5

        # =================================================
        # WATER RETENTION
        # =================================================

        water_retention = (som * 180) + (biochar_input * 3)

        # =================================================
        # CLIMATE SHOCK
        # =================================================

        climate_shock = np.random.uniform(shock_min, shock_max)

        # =================================================
        # AGRIVOLTAIC EFFECT
        # =================================================

        evap_reduction = 1.0 - (
            0.4 * copertura_agrivoltaico / 100
        )

        energy_revenue = (
            2200 * (copertura_agrivoltaico / 100)
        )

        # =================================================
        # WATER DEMAND
        # =================================================

        irrigation_need = (
            c["fabbisogno_irr"] * evap_reduction
        )

        permaculture_saving = (
            irrigation_need *
            (efficienza_permacultura / 100)
        )

        irrigation_final = max(
            50,
            irrigation_need -
            (water_retention * 1.5) -
            permaculture_saving
        )

        # =================================================
        # WATER COST VOLATILITY
        # =================================================

        water_price_shock = np.random.normal(1.0, 0.15)

        water_cost_final = (
            water_cost *
            water_price_shock
        )

        # =================================================
        # BIOMASS / PYROLYSIS
        # =================================================

        biochar_auto = (
            c["residuo_biomassa"] +
            biomassa_forestale
        ) / 4

        pyro_energy = (
            biochar_auto *
            superficie_totale *
            2
        )

        water_cost_final = max(
            0.05,
            water_cost_final -
            (pyro_energy / 10000)
        )

        # =================================================
        # YIELD MODEL
        # =================================================

        resilience_bonus = min(
            1.25,
            water_retention / 250
        )

        resa = (
            c["resa_base"] *
            resilience_bonus *
            (1 + climate_shock)
        )

        resa = max(0.5, resa)

        # =================================================
        # INPUT COST VOLATILITY
        # =================================================

        fertilizer_shock = np.random.normal(1.0, 0.20)

        input_cost = (
            c["costo_base"] *
            fertilizer_shock
        )

        # =================================================
        # CARBON REMOVAL
        # =================================================

        soc_carbon = som * 2.2

        biochar_carbon = biochar_input * 2.5

        total_carbon = (
            soc_carbon +
            biochar_carbon
        )

        carbon_revenue = (
            total_carbon *
            carbon_price
        ) * 0.15

        # =================================================
        # GROSS OPERATING MARGIN
        # =================================================

        mol_ha = (
            (resa * c["prezzo"]) +
            energy_revenue +
            carbon_revenue -
            input_cost -
            (irrigation_final * water_cost_final)
        )

        cumulative_cashflow += (
            mol_ha * superficie_totale
        )

    # =====================================================
    # STORE RESULTS
    # =====================================================

    results.append([
        cumulative_cashflow,
        mol_ha,
        total_carbon,
        som
    ])

# =========================================================
# RESULTS DATAFRAME
# =========================================================

df = pd.DataFrame(
    results,
    columns=[
        "CashFlow",
        "Final_MOL_ha",
        "Carbon_Removal",
        "Final_SOM"
    ]
)

# =========================================================
# KPIs
# =========================================================

mean_cf = df["CashFlow"].mean()

worst_cf = df["CashFlow"].quantile(0.1)

best_cf = df["CashFlow"].quantile(0.9)

loss_probability = (
    (df["CashFlow"] < 0).mean() * 100
)

# =========================================================
# DASHBOARD
# =========================================================

st.header("📊 Resilience Dashboard")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Average Cash Flow",
    f"€ {round(mean_cf/1e6,2)} M"
)

col2.metric(
    "10% Worst Case",
    f"€ {round(worst_cf/1e6,2)} M"
)

col3.metric(
    "90% Best Case",
    f"€ {round(best_cf/1e6,2)} M"
)

col4.metric(
    "Loss Probability",
    f"{round(loss_probability,1)} %"
)

# =========================================================
# HISTOGRAM
# =========================================================

st.subheader("Cash Flow Distribution")

fig, ax = plt.subplots(figsize=(10,5))

ax.hist(df["CashFlow"], bins=30)

ax.set_xlabel("Cumulative Cash Flow (€)")
ax.set_ylabel("Frequency")

st.pyplot(fig)

# =========================================================
# RESILIENCE METRICS
# =========================================================

st.subheader("Ecological Performance")

col5, col6 = st.columns(2)

col5.metric(
    "Final SOM %",
    round(df["Final_SOM"].mean(),2)
)

col6.metric(
    "Carbon Removal (tCO2e/ha)",
    round(df["Carbon_Removal"].mean(),2)
)

# =========================================================
# EXPLANATION
# =========================================================

st.write("""
This stochastic model simulates how regenerative land systems 
reduce cash-flow volatility through:

- Soil carbon accumulation
- Water retention improvement
- Reduced fossil input dependency
- Biochar-enhanced resilience
- Agrivoltaic integration
- Carbon-linked revenues

The objective is not maximizing peak yield, 
but stabilizing long-term biological and financial performance 
under climate uncertainty.
""")
