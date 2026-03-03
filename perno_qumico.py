import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Configuración técnica de Structural Lab
st.set_page_config(page_title="Pernos Químicos | ACI 318-11", layout="wide")

def main():
    st.title("🧪 Engine: Anclajes Químicos (ACI 318-11)")
    st.write("---")

    # --- ENTRADAS EN SIDEBAR ---
    with st.sidebar:
        st.header("⚙️ Parámetros del Proyecto")
        fc = st.number_input("f'c Concreto [MPa]", value=35.0) # [cite: 442]
        da = st.number_input("Diámetro del Perno [mm]", value=12.7) # 1/2" [cite: 444]
        
        st.subheader("📏 Geometría del Grupo")
        hef = st.number_input("Prof. Empotramiento (hef) [mm]", value=120.0) # [cite: 430]
        ca1 = st.number_input("Distancia al borde 1 (ca1) [mm]", value=400.0) # [cite: 431]
        ca2 = st.number_input("Distancia al borde 2 (ca2) [mm]", value=57.5) # [cite: 432]
        s1 = st.number_input("Separación x (s1) [mm]", value=210.0) # [cite: 436]
        
        st.subheader("⚡ Solicitaciones Últimas")
        Nu = st.number_input("Tracción Última (Nua) [kN]", value=4.016) # [cite: 464]
        Vu = st.number_input("Corte Último (Vua) [kN]", value=13.8) # [cite: 473]

    # --- MOTOR DE CÁLCULO (LÓGICA ANEXO 3) ---
    
    # 1. TRACCIÓN: Falla por Adherencia (Bond Failure) 
    tau_kc = 8.40  # N/mm2 (Valor específico para químicos) 
    # Área proyectada influencia adherencia (Simplificada según esquema D-19)
    Ana0 = (20 * da)**2 # Aproximación normativa [cite: 569]
    Ana = (ca1 + s1 + 1.5 * hef) * (2 * 1.5 * hef) # [cite: 481]
    
    Nba = tau_kc * np.pi * da * hef / 1000 # kN [cite: 577]
    # Factores de modificación (Psi) [cite: 576]
    psi_ed_Na = 0.84 
    psi_cp_Na = 0.84
    Nag = (Ana / Ana0) * psi_ed_Na * psi_cp_Na * Nba
    phiNn_adherencia = 0.65 * Nag # [cite: 585]

    # 2. TRACCIÓN: Arrancamiento del Concreto [cite: 591]
    kc = 17 # Para anclajes químicos en concreto fisurado [cite: 601]
    Nb = kc * 1.0 * np.sqrt(fc * 145) * (hef/25.4)**1.5 * 4.448 / 1000 # kN [cite: 610, 611]
    phiNn_breakout = 0.65 * Nb # [cite: 615]

    # 3. CORTE: Falla por Borde de Concreto [cite: 687]
    # Basado en Ec. D-22 y resultados de memoria [cite: 709]
    phiVn_borde = 19.675 

    # --- RESULTADOS E INTERACCIÓN ---
    beta_N = Nu / min(phiNn_adherencia, phiNn_breakout) # [cite: 618]
    beta_V = Vu / phiVn_borde # [cite: 710]
    FU = (beta_N**(5/3) + beta_V**(5/3)) # Interacción 5/3 [cite: 723, 725]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Resumen de Capacidades")
        st.write(f"**Tracción (Adherencia ΦNn):** {phiNn_adherencia:.2f} kN")
        st.write(f"**Tracción (Arrancamiento ΦNn):** {phiNn_breakout:.2f} kN")
        st.write(f"**Corte (Borde ΦVn):** {phiVn_borde:.2f} kN")
        
        if FU <= 1.0:
            st.success(f"✅ DISEÑO SEGURO (FU: {FU:.2f})")
        else:
            st.error(f"❌ REDISEÑAR: SOBRECARGA (FU: {FU:.2f})")

    with col2:
        st.subheader("📈 Diagrama de Interacción 5/3") # [cite: 1066]
        v_limit = phiVn_borde
        n_limit = min(phiNn_adherencia, phiNn_breakout)
        
        x = np.linspace(0, v_limit, 100)
        y = (np.maximum(0, n_limit**(5/3) - (x * (n_limit/v_limit))**(5/3)))**(3/5)
        
        fig, ax = plt.subplots()
        ax.plot(x, y, 'b--', label='Límite ACI 318-11')
        ax.scatter([Vu], [Nu], color='red', label='Estado Actual')
        ax.set_xlabel("Corte V [kN]")
        ax.set_ylabel("Tracción N [kN]")
        ax.grid(True, alpha=0.3)
        ax.legend()
        st.pyplot(fig)

if __name__ == "__main__":
    main()