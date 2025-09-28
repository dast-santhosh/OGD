import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def create_air_quality_dashboard():
    st.header("🌬️ Air Quality Dashboard")

    # Simulated Air Quality Data
    np.random.seed(42)
    pollutants = ["PM2.5", "PM10", "NO2", "SO2", "O3", "CO"]
    data = {
        "Pollutant": pollutants,
        "Concentration (µg/m³)": np.random.randint(10, 200, len(pollutants)),
        "Safe Limit (µg/m³)": [60, 100, 80, 80, 100, 2000]
    }
    df = pd.DataFrame(data)

    # Table
    st.subheader("📊 Pollutant Levels")
    st.dataframe(df, use_container_width=True)

    # Bar Chart
    st.subheader("📈 Pollutant Concentration vs Safe Limit")
    fig, ax = plt.subplots(figsize=(6,4))
    ax.bar(df["Pollutant"], df["Concentration (µg/m³)"], label="Concentration")
    ax.plot(df["Pollutant"], df["Safe Limit (µg/m³)"], "r--", label="Safe Limit")
    ax.set_ylabel("µg/m³")
    ax.legend()
    st.pyplot(fig)

    # Warning Messages
    for _, row in df.iterrows():
        if row["Concentration (µg/m³)"] > row["Safe Limit (µg/m³)"]:
            st.warning(f"⚠️ {row['Pollutant']} exceeds safe limit!")

    st.info("💡 Data is simulated. In production, connect to NASA/ISRO APIs or CPCB live data feeds.")
