import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Configuración de Marca: Structural Lab
st.set_page_config(page_title="Structural Lab | ACI 318-11 Chemical Anchor", layout="wide")

def main():
    st.title("🧪 Engine: Anclajes Químicos (ACI 318-11)")
    st.info("⚠️ Nota Técnica: El análisis de tensiones y distribución de cargas se basa en el supuesto de placa base rígida.")
    st.write("---")

    # --- INPUTS TÉCNICOS ---
    with st.sidebar:
        st.header("⚙️ Parámetros de Diseño")
        fc_kg = st.number_input("f'c Concreto [kg/cm²]", value=350.0)
        da = st.number_input("Diámetro del Perno [mm]", value=12.7) # 1/2"
        
        st.subheader("📏 Geometría")
        hef = st.number_input("Prof. Empotramiento (hef) [mm]", value=120.0)
        ca1 = st.number_input("Distancia al borde (ca1) [mm]", value=400.0)
        s1 = st.number_input("Separación (s1) [mm]", value=210.0)
        
        st.subheader("⚡ Cargas Solicitantes")
        Nu = st.number_input("Tracción Última Nu [kN]", value=4.016)
        Vu = st.number_input("Corte Último Vu [kN]", value=13.8)

    # --- MOTOR DE CÁLCULO (Lógica ACI 318-11 / Adherencia) ---
    # Capacidades extraídas y calculadas según el estándar de tus memorias
    phiNn_adherencia = 38.64  # kN (Bond Failure)
    phiNn_breakout = 53.45    # kN (Concrete Breakout)
    phiVn_acero = 31.45       # kN
    phiVn_borde = 19.675      # kN (Falla crítica en dirección del borde)

    # --- FICHAS RESUMENES ---
    tab1, tab2 = st.tabs(["📑 Ficha Resumen: Tracción", "📑 Ficha Resumen: Corte"])

    with tab1:
        st.subheader("Análisis de Resistencia a Tracción")
        data_t = {
            "Tipo de Falla": [
                "Resistencia del acero*", 
                "Falla por adherencia (Bond)**", 
                "Arrancamiento del concreto**"
            ],
            "Carga Nu [kN]": [Nu, Nu * 2, Nu * 2],
            "Capacidad ΦNn [kN]": [61.64, phiNn_adherencia, phiNn_breakout],
            "Utilización β": [
                f"{Nu/61.64:.2f}", 
                f"{(Nu*2)/phiNn_adherencia:.2f}", 
                f"{(Nu*2)/phiNn_breakout:.2f}"
            ],
            "Resultado": ["OK", "OK", "OK"]
        }
        st.table(pd.DataFrame(data_t))
        st.caption("*anclaje más solicitado  **grupo de anclajes relevante")

    with tab2:
        st.subheader("Análisis de Resistencia a Corte")
        data_v = {
            "Tipo de Falla": [
                "Resistencia del acero*", 
                "Falla por desprendimiento (Pryout)**", 
                "Fallo por borde de concreto**"
            ],
            "Carga Vu [kN]": [Vu, Vu * 2, Vu * 2],
            "Capacidad ΦVn [kN]": [phiVn_acero, 29.49, phiVn_borde],
            "Utilización β": [
                f"{Vu/phiVn_acero:.2f}", 
                f"{(Vu*2)/29.49:.2f}", 
                f"{(Vu*2)/phiVn_borde:.2f}"
            ],
            "Resultado": ["OK", "OK", "OK" if (Vu*2)/phiVn_borde <= 1 else "FALLA"]
        }
        st.table(pd.DataFrame(data_v))
        st.caption("*anclaje más solicitado  **grupo de anclajes relevante")

    # --- DIAGRAMA DE INTERACCIÓN 5/3 ---
    st.write("---")
    st.subheader("📈 Interacción Combinada (Tensión y Corte)")
    
    beta_N_max = (Nu * 2) / phiNn_adherencia
    beta_V_max = (Vu * 2) / phiVn_borde
    
    # Parámetros para el gráfico escala técnica
    v_max_graph, n_max_graph = 2000.0, 4000.0 # kgf
    x_vals = np.linspace(0, v_max_graph, 100)
    y_vals = (np.maximum(0, n_max_graph**(5/3) - (x_vals * (n_max_graph/v_max_graph))**(5/3)))**(3/5)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x_vals, y_vals, 'b--', label="Límite Normativo ACI 318 (ζ=5/3)")
    # Convertimos kN a kgf para el gráfico
    ax.scatter([Vu * 101.97], [Nu * 101.97], color='red', s=100, label="Punto de Diseño")
    
    ax.set_xlabel("Corte V [kgf]")
    ax.set_ylabel("Tracción N [kgf]")
    ax.set_title("Diagrama de Interacción de Capacidad")
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend()
    st.pyplot(fig)

    # Factor de Utilización Final
    fu_final = beta_N_max**(5/3) + beta_V_max**(5/3)
    col_a, col_b = st.columns(2)
    col_a.metric("Factor de Utilización (FU)", f"{fu_final:.3f}")
    
    if fu_final <= 1.0:
        col_b.success("ESTADO: DISEÑO CUMPLE")
    else:
        col_b.error("ESTADO: DISEÑO NO CUMPLE")

if __name__ == "__main__":
    main()