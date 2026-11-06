# =========================================================
# 1. IMPORTACIÓN DE LIBRERÍAS
# =========================================================
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# =========================================================
# 2. FUNCIONES MATEMÁTICAS Y DE INGENIERÍA QUÍMICA
# =========================================================
def calcular_concentraciones(ph):
    """Calcula la molaridad de los iones H+ y OH- a partir del pH."""
    h_conc = 10**(-ph)
    oh_conc = 10**(-(14.0 - ph))
    return h_conc, oh_conc

def calcular_dosificacion(caudal_m3h, ph_in, ph_out, reactivo):
    """
    Calcula el flujo másico de reactivo (kg/h) necesario para neutralizar
    el caudal de efluente industrial en una PTAR.
    """
    caudal_L_h = caudal_m3h * 1000.0  # Conversión m³/h a L/h
    delta_h = abs(10**(-ph_in) - 10**(-ph_out))
    moles_h = delta_h * caudal_L_h
    
    # Propiedades químicas: (Peso Molecular g/mol, Valencia equivalente)
    datos_reactivos = {
        "Hidróxido de Sodio (NaOH)": (39.99, 1),
        "Hidróxido de Calcio (Ca(OH)2)": (74.09, 2),
        "Ácido Sulfúrico (H2SO4)": (98.07, 2),
        "Ácido Clorhídrico (HCl)": (36.46, 1)
    }
    pm, eq = datos_reactivos[reactivo]
    
    # Retorna la dosis másica requerida en kg/h
    return ((moles_h / eq) * pm) / 1000.0

# =========================================================
# 3. INTERFAZ GRÁFICA Y WIDGETS (STREAMLIT)
# =========================================================
st.set_page_config(
    page_title="ChemPH - Neutralización PTAR",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 ChemPH: Control Industrial de Neutralización de Efluentes")
st.caption("Planta de Tratamiento de Aguas Residuales Industriales (PTAR)")
st.markdown("---")

# BARRA LATERAL (ENTRADAS DEL USUARIO)
st.sidebar.header("⚙️ Parámetros de Operación")

caudal = st.sidebar.number_input("Caudal del Efluente (m³/h):", min_value=1.0, max_value=500.0, value=50.0, step=5.0)
ph_entrada = st.sidebar.slider("pH Medido de Entrada:", min_value=0.0, max_value=14.0, value=3.5, step=0.1)
ph_salida = st.sidebar.slider("pH Objetivo de Descarga (Norma):", min_value=6.5, max_value=8.5, value=7.0, step=0.1)

# Selección dinámica de reactivo según la naturaleza del efluente
if ph_entrada < 7.0:
    opciones_reactivos = ["Hidróxido de Sodio (NaOH)", "Hidróxido de Calcio (Ca(OH)2)"]
    st.sidebar.info("💧 Efluente Ácido: Se requiere dosificación de base.")
else:
    opciones_reactivos = ["Ácido Sulfúrico (H2SO4)", "Ácido Clorhídrico (HCl)"]
    st.sidebar.info("🔥 Efluente Básico: Se requiere dosificación de ácido.")

reactivo_sel = st.sidebar.selectbox("Reactivo Neutralizante:", opciones_reactivos)

# CÁLCULOS PRINCIPALES
dosis_kgh = calcular_dosificacion(caudal, ph_entrada, ph_salida, reactivo_sel)

# RESULTADOS CLAVE EN PANTALLA (MÉTRICAS)
col1, col2, col3 = st.columns(3)
col1.metric("Caudal Operativo", f"{caudal} m³/h")
col2.metric("pH Medido de Entrada", f"{ph_entrada} pH")
col3.metric("Reactivo Requerido", f"{dosis_kgh:.2f} kg/h")

st.markdown("---")

# =========================================================
# 4. PESTAÑAS DE VISUALIZACIÓN Y REGISTROS
# =========================================================
tab_graficas, tab_tabla = st.tabs(["📊 Gráficas del Proceso", "📋 Registros de Operación (Pandas)"])

with tab_graficas:
    col_g1, col_g2 = st.columns(2)
    
    # GRÁFICA 1: PLOTLY (CURVA DINÁMICA DE TITULACIÓN)
    with col_g1:
        st.subheader("📈 Curva de Titulación Industrial (Plotly)")
        dosis_eje = np.linspace(0, max(dosis_kgh * 2, 1.0), 50)
        
        if ph_entrada < 7.0:
            ph_curva = np.clip(ph_entrada + (dosis_eje / (dosis_kgh + 1e-5)) * (ph_salida - ph_entrada), 0, 14)
        else:
            ph_curva = np.clip(ph_entrada - (dosis_eje / (dosis_kgh + 1e-5)) * (ph_entrada - ph_salida), 0, 14)
            
        fig_plotly = go.Figure()
        fig_plotly.add_trace(go.Scatter(x=dosis_eje, y=ph_curva, mode='lines', name='Curva pH', line=dict(color='#0275d8', width=3)))
        fig_plotly.add_hline(y=ph_salida, line_dash="dash", line_color="green", annotation_text="pH Norma Target")
        fig_plotly.add_vline(x=dosis_kgh, line_dash="dash", line_color="red", annotation_text="Dosis Requerida")
        fig_plotly.update_layout(xaxis_title="Dosis Reactivo (kg/h)", yaxis_title="pH Resultante", height=360)
        st.plotly_chart(fig_plotly, use_container_width=True)

    # GRÁFICA 2: MATPLOTLIB (BALANCE IÓNICO EN ESCALA LOGARÍTMICA)
    with col_g2:
        st.subheader("⚖️ Balance de Iones en Tanque (Matplotlib)")
        h_conc, oh_conc = calcular_concentraciones(ph_entrada)
        
        fig_mat, ax = plt.subplots(figsize=(5, 3.8))
        ax.bar(['[H+]', '[OH-]'], [h_conc, oh_conc], color=['#d9534f', '#0275d8'])
        ax.set_yscale('log')
        ax.set_ylabel('Concentración (mol/L)')
        ax.set_title('Concentración Molar de Iones (Escala Logarítmica)')
        ax.grid(True, which="both", ls="--", alpha=0.5)
        st.pyplot(fig_mat)

with tab_tabla:
    st.subheader("📋 Simulación de Turno Operativo (24 Horas)")
    
    # CREACIÓN Y MANEJO DE TABLAS CON PANDAS Y NUMPY
    np.random.seed(42)
    horas = [f"{i:02d}:00 HRS" for i in range(24)]
    ph_simulado = np.random.normal(loc=ph_entrada, scale=0.25, size=24).round(2)
    caudal_simulado = np.random.normal(loc=caudal, scale=1.0, size=24).round(1)
    
    dosis_simuladas = [
        round(calcular_dosificacion(c, p, ph_salida, reactivo_sel), 2)
        for c, p in zip(caudal_simulado, ph_simulado)
    ]
    
    df_turno = pd.DataFrame({
        "Hora": horas,
        "pH Entrada": ph_simulado,
        "Caudal (m³/h)": caudal_simulado,
        "Reactivo": reactivo_sel,
        "Dosis Necesaria (kg/h)": dosis_simuladas,
        "pH Salida Esperado": [ph_salida] * 24
    })
    
    st.dataframe(df_turno, use_container_width=True)
    
    # BOTÓN PARA DESCARGAR DATOS EN CSV
    st.download_button(
        label="📥 Descargar Reporte de Operación en CSV",
        data=df_turno.to_csv(index=False).encode('utf-8'),
        file_name="reporte_dosificacion_PTAR.csv",
        mime="text/csv"
    )
