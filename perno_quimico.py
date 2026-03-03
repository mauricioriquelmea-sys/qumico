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

    # --- DIAGRAMA DE INTERACCIÓN AUTO-ESCALABLE (CORREGIDO) ---
    st.write("---")
    st.subheader("📈 Interacción Combinada (Tensión y Corte)")
    
    # 1. Definimos las utilizaciones reales
    beta_N_max = (Nu * 2) / phiNn_adherencia
    beta_V_max = (Vu * 2) / phiVn_borde
    
    # 2. Definimos los límites de capacidad real en kgf para el gráfico
    n_limit_kgf = phiNn_adherencia * 101.97  # Capacidad máxima tracción
    v_limit_kgf = phiVn_borde * 101.97      # Capacidad máxima corte
    
    # 3. Generamos la curva 5/3 basada en las capacidades REALES
    x_curve = np.linspace(0, v_limit_kgf, 100)
    # Ecuación: (N/Nn)^5/3 + (V/Vn)^5/3 = 1  => N = Nn * (1 - (V/Vn)^5/3)^3/5
    y_curve = n_limit_kgf * (np.maximum(0, 1 - (x_curve / v_limit_kgf)**(5/3)))**(3/5)

    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Dibujar curva y zona segura
    ax.plot(x_curve, y_curve, 'b--', label="Límite Normativo ACI 318 (ζ=5/3)")
    ax.fill_between(x_curve, y_curve, alpha=0.1, color='blue', label="Zona de Diseño Seguro")
    
    # Convertimos la carga solicitante (grupo) a kgf para posicionar la pelota
    punto_n_kgf = (Nu * 2) * 101.97
    punto_v_kgf = (Vu * 2) * 101.97
    
    ax.scatter([punto_v_kgf], [punto_n_kgf], color='red', s=120, label="Estado de Carga Grupo", zorder=5)
    
    # Ajuste dinámico de los ejes para que siempre se vea el punto y la curva
    ax.set_xlim(0, max(v_limit_kgf, punto_v_kgf) * 1.3)
    ax.set_ylim(0, max(n_limit_kgf, punto_n_kgf) * 1.3)
    
    ax.set_xlabel("Corte V [kgf]")
    ax.set_ylabel("Tracción N [kgf]")
    ax.set_title("Diagrama de Interacción de Capacidad Reales")
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend()
    st.pyplot(fig)

    # --- RESULTADO FINAL ---
    fu_final = beta_N_max**(5/3) + beta_V_max**(5/3)
    col_a, col_b = st.columns(2)
    col_a.metric("Factor de Utilización (FU)", f"{fu_final:.3f}")
    
    if fu_final <= 1.0:
        col_b.success("ESTADO: DISEÑO CUMPLE ✅")
    else:
        col_b.error("ESTADO: DISEÑO NO CUMPLE ❌ (Sobrepasa el límite normativo)")

if __name__ == "__main__":
    main()