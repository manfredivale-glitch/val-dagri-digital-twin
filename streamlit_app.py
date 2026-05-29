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
st.sidebar.subheader("Regenerative Water System")

water_retention = st.sidebar.slider("Water Retention Capacity", 0, 100, 30)
evap_reduction = st.sidebar.slider("Evaporation Reduction", 0, 100, 20)
agro_stability = st.sidebar.slider("Agroecological Stability", 0, 100, 25)

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

def run_simulation(sc):

    data = []
    som = soil["som_init"]
    contamination_factor = soil["contamination"]

    water_stock = 100  # stato iniziale stabile

    for anno in range(1, 6):

        # -----------------------------
        # 1. SHOCK CLIMATICO
        # -----------------------------
        shock_pool = (
            ["good", "normal", "bad", "bad"] if sc["bad_bias"] > 0.4 else
            ["good", "normal", "bad"] if sc["bad_bias"] > 0.25 else
            ["good", "normal", "normal"]
        )

        shock = random.choice(shock_pool)

        climate_multiplier = (
            1.1 if shock == "good" else
            0.8 if shock == "bad" else
            1.0
        ) * sc["climate"]

        # -----------------------------
        # 2. SOM (STOCK DINAMICO)
        # -----------------------------
        som += (
            biochar_input * 0.02 +
            biomassa_forestale * 0.01 -
            som * 0.01
        )
        som = max(0, som)

        # -----------------------------
        # 3. CONTAMINATION
        # -----------------------------
        remediation_effect = (
            biochar_input * 0.01 +
            som * 0.002
        )

        contamination_factor += (
            sc["bad_bias"] * 0.02
            - remediation_effect
        )

        contamination_factor = min(max(contamination_factor, 0), 1)

        soil_recovery_bonus = (1 - contamination_factor)

        # -----------------------------
        # 4. WATER SYSTEM
        # -----------------------------
        water_inflow = soil["water_factor"] * 50
        water_loss = (1 - som * 0.02) * 40

        water_stock = max(0, water_inflow - water_loss)

        # -----------------------------
        # 5. SOIL HEALTH INDEX
        # -----------------------------
        soil_health = (
            som * 0.4 +
            (water_stock / 100) * 0.4 +
            (1 - contamination_factor) * 0.2
        )

        # -----------------------------
        # 6. YIELD
        # -----------------------------
        resa = (
            4.5 *
            soil_health *
            c["risp_biochar"] *
            climate_multiplier
        )

        # -----------------------------
        # 7. PRICE
        # -----------------------------
        price_trend = 1 + (premium_factor_time - 1) * (anno - 1)

        prezzo_effettivo = (
            c["prezzo"] *
            sc["price"] *
            premium_factor *
            price_trend
        )

        mol_ha = (resa * prezzo_effettivo) - c["costo_base"]

        # -----------------------------
        # 8. STORE
        # -----------------------------
        data.append([
            anno,
            som,
            water_stock,
            resa,
            mol_ha
        ])

    return pd.DataFrame(
        data,
        columns=['Anno', 'SOM_%', 'Water_m3', 'Resa_t', 'MOL_Euro']
    )
    
# --- 3. OUTPUT ---
df_base = run_simulation(scenario_config["Base Case"])

df_up = run_simulation(scenario_config["Upside Case"])

df_down = run_simulation(scenario_config["Downside Case"])

df = {
    "Base Case": df_base,
    "Upside Case": df_up,
    "Downside Case": df_down
}[scenario]

slide = st.sidebar.radio(
    "Seleziona Slide",
    [
        "Context",
        "Ecology",
        "Yield",
        "Finance",
        "Energy Nexus",
        "Multi-Scenario",
        "Investment Summary"
    ]
)

st.subheader("📊 Investment Slide Engine")

if len(df) > 0:
    last = df.iloc[-1]

    if slide == "Context":
        st.subheader("🌍 Project Context")
        st.write({
            "Scenario": scenario,
            "Crop": coltura,
            "Area (ha)": superficie_totale,
            "Soil Type": soil_type
        })

    elif slide == "Ecology":

        st.subheader("🌱 Soil System Evolution")

        col1, col2 = st.columns(2)

        col1.metric("Soil Organic Matter", f"{last['SOM_%']:.2f}")
        col2.metric("Water Stock (index)", f"{last['Water_m3']:.1f}")

        st.line_chart(df.set_index("Anno")[["SOM_%", "Water_m3"]])
    
    elif slide == "Yield":
        st.subheader("🌾 Yield Trajectory")
        st.line_chart(df.set_index("Anno")[["Resa_t"]])

    elif slide == "Finance":

        st.subheader("💰 Financial Performance")

        col1, col2 = st.columns(2)

        col1.metric("Final Margin", f"{last['MOL_Euro']:.0f}€")
        col2.metric("Avg Margin", f"{df['MOL_Euro'].mean():.0f}€")

        st.line_chart(df.set_index("Anno")[["MOL_Euro"]])
    
    elif slide == "Energy Nexus":

        st.subheader("⚡ Energy & Water Nexus")

        st.metric("Water Efficiency Proxy", f"{last['Water_m3']:.1f}")

        st.line_chart(df.set_index("Anno")[["Water_m3"]])
    
    elif slide == "Multi-Scenario":

        st.subheader("📊 Scenario Comparison")

        comparison_df = pd.DataFrame({
            "Base": df_base.set_index("Anno")["MOL_Euro"],
            "Upside": df_up.set_index("Anno")["MOL_Euro"],
            "Downside": df_down.set_index("Anno")["MOL_Euro"]
        })

        st.line_chart(comparison_df)
    
    elif slide == "Investment Summary":
        
        st.subheader("📊 Investment Score")

        avg_margin = df["MOL_Euro"].mean()
        volatility = df["MOL_Euro"].std()

        investment_score = (
            (avg_margin / 1000) * 0.4 +
            (last["Resa_t"]) * 0.3 +
            (last["SOM_%"]) * 0.2 -
            (volatility / 500) * 0.1
        )

        col1, col2, col3 = st.columns(3)

        col1.metric("Yield", round(last["Resa_t"], 2))
        col2.metric("Margin", f"{round(last['MOL_Euro'], 0)}€")
        col3.metric("Soil", round(last["SOM_%"], 2))

        st.metric("Investment Score", round(investment_score, 2))

        if investment_score > 5:
            st.success("🟢 High attractiveness")
        elif investment_score > 3:
            st.warning("🟡 Medium attractiveness")
        else:
            st.error("🔴 Low attractiveness")

else:
    st.warning("Simulazione non disponibile")
