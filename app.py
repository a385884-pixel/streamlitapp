# =========================================================
# 1. IMPORTACIÓN DE LIBRERÍAS
# =========================================================
import io
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# =========================================================
# 2. CONFIGURACIÓN GENERAL DE LA PÁGINA
# =========================================================
st.set_page_config(
    page_title="El pH en la Ingeniería Química",
    page_icon="🧪",
    layout="wide"
)

# =========================================================
# 3. FUNCIONES DE CÁLCULO QUÍMICO E INGENIERÍA DE PROCESOS
# =========================================================
def calcular_kw(temp_c):
    """Calcula Kw, pKw y el pH neutro real según la temperatura (°C)."""
    pkw = 14.0 - 0.033 * (temp_c - 25.0)
    kw = 10**(-pkw)
    ph_neutro = pkw / 2.0
    return kw, pkw, ph_neutro

def calcular_concentraciones(ph, temp_c=25.0):
    """Calcula la molaridad de [H+] y [OH-] a partir del pH y la temperatura."""
    kw, _, _ = calcular_kw(temp_c)
    h_conc = 10**(-ph)
    oh_conc = kw / h_conc
    return h_conc, oh_conc

def calcular_dosificacion(caudal_m3h, ph_in, ph_out, reactivo, temp_c=25.0):
    """
    Calcula el flujo másico de reactivo (kg/h) necesario para neutralizar
    un caudal industrial mediante balance de carga iónica.
    """
    kw, _, _ = calcular_kw(temp_c)
    caudal_L_h = caudal_m3h * 1000.0  # Conversión m³/h a L/h

    c_net_in = (10**(-ph_in)) - (kw / (10**(-ph_in)))
    c_net_out = (10**(-ph_out)) - (kw / (10**(-ph_out)))

    delta_eq_L = abs(c_net_in - c_net_out)
    moles_eq_h = delta_eq_L * caudal_L_h

    datos_reactivos = {
        "Hidróxido de Sodio (NaOH)": (39.99, 1),
        "Hidróxido de Calcio (Ca(OH)2)": (74.09, 2),
        "Ácido Sulfúrico (H2SO4)": (98.07, 2),
        "Ácido Clorhídrico (HCl)": (36.46, 1)
    }
    pm, eq = datos_reactivos[reactivo]
    return ((moles_eq_h / eq) * pm) / 1000.0

def generar_curva_titulacion(caudal_m3h, ph_in, ph_out, reactivo, temp_c=25.0):
    """Genera la curva sigmoidal exacta de valoración ácido-base."""
    kw, _, _ = calcular_kw(temp_c)
    caudal_L_h = caudal_m3h * 1000.0
    dosis_req = calcular_dosificacion(caudal_m3h, ph_in, ph_out, reactivo, temp_c)

    datos_reactivos = {
        "Hidróxido de Sodio (NaOH)": (39.99, 1),
        "Hidróxido de Calcio (Ca(OH)2)": (74.09, 2),
        "Ácido Sulfúrico (H2SO4)": (98.07, 2),
        "Ácido Clorhídrico (HCl)": (36.46, 1)
    }
    pm, eq = datos_reactivos[reactivo]

    dosis_eje = np.linspace(0, max(dosis_req * 2.0, 0.5), 140)
    c_net_in = (10**(-ph_in)) - (kw / (10**(-ph_in)))
    eq_anadidos_L = ((dosis_eje * 1000.0) / pm * eq) / caudal_L_h

    if ph_in < ph_out:
        c_net_array = c_net_in - eq_anadidos_L
    else:
        c_net_array = c_net_in + eq_anadidos_L

    h_array = (c_net_array + np.sqrt(c_net_array**2 + 4.0 * kw)) / 2.0
    ph_curva = np.clip(-np.log10(h_array), 0.0, 14.0)

    return dosis_eje, ph_curva, dosis_req

# =========================================================
# 4. BARRA LATERAL (OBJETIVO Y GUÍA DE PESTAÑAS)
# =========================================================
st.sidebar.title("🧪 El pH en la Ing. Química")
st.sidebar.markdown("### 🎯 Objetivo de la Aplicación")
st.sidebar.info(
    "Mostrar cómo los conceptos teóricos del **pH** aprendidos en el laboratorio universitario "
    "se transforman en herramientas de **Ingeniería Química** para controlar y neutralizar "
    "descargas de aguas residuales en la industria de Chihuahua."
)

st.sidebar.markdown("### 📑 Contenido por Pestaña")
st.sidebar.markdown(
    """
    **1️⃣ Introducción y Contexto Industrial:**  
    Qué es el pH, qué es la Ingeniería Química, su relación industrial, normas oficiales y contexto en Chihuahua.

    **2️⃣ Principios de la Simulación:**  
    Cómo funciona químicamente la neutralización y en qué principios fisicoquímicos se basa el simulador.

    **3️⃣ Fórmulas y Qué Calculan:**  
    Explicación detallada de cada ecuación, gráficas conceptuales de comportamiento y bibliografía.

    **4️⃣ Simulador Industrial:**  
    Ejemplo industrial práctico, panel interactivo en tiempo real, interpretación de la curva de valoración y bitácora de 24 h.
    """
)
st.sidebar.markdown("---")
st.sidebar.caption("Desarrollado en Python (Streamlit, NumPy, Pandas, Matplotlib y Plotly).")

# =========================================================
# 5. ENCABEZADO Y ESTRUCTURA DE 4 PESTAÑAS
# =========================================================
st.title("🧪 El pH en la Ingeniería Química: Del Laboratorio al Control Industrial")
st.caption("Simulador de Neutralización de Efluentes y Escalamiento de Procesos (PTAR Chihuahua)")

tab1, tab2, tab3, tab4 = st.tabs([
    "1️⃣ Introducción y Contexto Industrial",
    "2️⃣ Principios de la Simulación",
    "3️⃣ Fórmulas y Qué Calculan",
    "4️⃣ Simulador Industrial"
])

# ---------------------------------------------------------
# PESTAÑA 1: INTRODUCCIÓN, NORMAS E INDUSTRIA EN CHIHUAHUA
# ---------------------------------------------------------
with tab1:
    st.header("1. Introducción: El pH, la Ingeniería Química y la Industria")

    st.info(
        "**Propósito de esta aplicación:** Demostrar cómo lo que aprendemos en las materias escolares "
        "(como Química Inorgánica y balances básicos en mililitros) se escala y transforma en ingeniería real "
        "para resolver problemas ambientales y operativos de control de pH en plantas industriales."
    )

    col_i1, col_i2 = st.columns(2)
    with col_i1:
        st.subheader("¿Qué es el pH?")
        st.write(
            "El **pH** (*potencial de hidrógeno*) es una medida que indica el grado de acidez o alcalinidad "
            "de una disolución acuosa en una escala que va de **0 a 14** (siendo $7.0$ el punto neutro a $25\\,^\\circ\\text{C}$). "
            "Químicamente mide la concentración de iones hidrógeno ($H^+$) presentes en el agua."
        )
        st.write(
            "Al tratarse de una **escala logarítmica**, cada unidad de cambio representa un factor de **10 veces** "
            "en la concentración iónica: un agua residual con $\\text{pH } 3$ es **10,000 veces más ácida** que una con $\\text{pH } 7$."
        )

    with col_i2:
        st.subheader("¿Qué es la Ingeniería Química y cómo se relaciona con el pH?")
        st.write(
            "La **Ingeniería Química** es la disciplina que diseña, opera y controla procesos industriales "
            "donde la materia sufre cambios físicos o químicos, llevando reacciones de laboratorio a escalas de "
            "**miles de litros por hora** con seguridad y rentabilidad."
        )
        st.write(
            "Su relación con el **pH** es directa: en la industria, un pH fuera de control corroe tuberías metálicas, "
            "destruye los microorganismos de las plantas tratadoras, impide la precipitación de metales pesados y "
            "genera multas ambientales por descargas contaminantes."
        )

    st.markdown("---")
    st.subheader("Normatividad Oficial Mexicana Aplicable")
    col_n1, col_n2 = st.columns(2)
    with col_n1:
        st.warning(
            "**NOM-002-SEMARNAT-1996 (Descargas al Alcantarillado):**\n\n"
            "Establece los límites máximos permisibles de contaminantes en las descargas de aguas residuales "
            "a los sistemas de alcantarillado urbano o municipal. Exige mantener el **pH entre 5.5 y 10.0 unidades** "
            "para evitar la corrosión de la red pública."
        )
    with col_n2:
        st.success(
            "**NOM-001-SEMARNAT-2021 (Cuerpos Receptores Nacionales):**\n\n"
            "Regula las descargas de aguas residuales en ríos, arroyos, embalses o suelo. "
            "Exige un control más estricto, manteniendo el **pH dentro del rango de 6.0 a 9.0 unidades** "
            "para proteger la vida acuática y el entorno."
        )

    st.markdown("---")
    st.subheader("Conexión con la Industria y Gestión Hídrica en Chihuahua")
    st.write(
        "En una ciudad con clima semidesértico y fuerte vocación manufacturera como **Chihuahua**, el tratamiento "
        "y control de pH en el agua industrial es indispensable para permitir su saneamiento y reúso:"
    )
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown(
            "- **JMAS Chihuahua (Junta Municipal de Agua y Saneamiento):** Opera las plantas **PTAR Norte** y **PTAR Sur**, "
            "supervisando el cumplimiento normativo de las descargas industriales al alcantarillado y distribuyendo agua tratada (línea morada) "
            "a parques industriales y áreas verdes.\n"
            "- **Sector Metalmecánico y Aeroespacial (Complejo Industrial Chihuahua, El Saucito, Supra):** Plantas de maquinado, "
            "anodizado y recubrimientos metálicos generan efluentes ácidos ($\\text{pH } 2.0 - 4.0$) por decapado químico que requieren "
            "dosificación de bases antes de verterse."
        )
    with col_c2:
        st.markdown(
            "- **Industria Alimentaria y Láctea (Grupo Bafar, Zaragoza / Alpura):** Sus ciclos de limpieza y desinfección "
            "CIP (*Clean-In-Place*) emplean sosa cáustica, generando aguas residuales alcalinas ($\\text{pH } 10.5 - 12.5$) que deben "
            "neutralizarse con ácidos.\n"
            "- **Del Laboratorio a la Planta:** Mientras en la escuela titulamos $50\\text{ mL}$ en un matraz, en estas empresas "
            "de Chihuahua se neutralizan flujos continuos de $20$ a $150\\text{ m}^3/\\text{h}$ mediante tanques agitados y bombas automatizadas."
        )

# ---------------------------------------------------------
# PESTAÑA 2: PRINCIPIOS DE LA SIMULACIÓN
# ---------------------------------------------------------
with tab2:
    st.header("2. Principios de la Simulación")
    st.write(
        "El simulador no realiza una simple regla de tres lineal; modela el comportamiento fisicoquímico real "
        "de un reactor continuo de neutralización aplicando cuatro principios de la Ingeniería Química:"
    )

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.subheader("1. Reacción Química de Neutralización")
        st.write(
            "Cuando un efluente ácido (exceso de $H^+$) reacciona con una base (aporte de $OH^-$), o viceversa, "
            "ambos iones se combinan formando agua líquida y desplazando el pH hacia la neutralidad:"
        )
        st.latex(r"H^+_{(ac)} + OH^-_{(ac)} \longrightarrow H_2O_{(l)} \quad (\Delta H^\circ = -57.3\text{ kJ/mol})")
        st.write(
            "Como esta reacción libera calor (es **exotérmica**), cuando los pH de entrada son extremos ($pH < 2.5$ o $pH > 11.5$), "
            "el simulador emite una alerta recomendando neutralizar en **dos etapas** para proteger los equipos."
        )

        st.subheader("2. Efecto de la Temperatura en el Equilibrio ($K_w$)")
        st.write(
            "En el laboratorio solemos asumir que el pH neutro siempre es $7.0$, pero eso solo ocurre a $25\\,^\\circ\\text{C}$. "
            "En procesos industriales el agua residual puede salir fría ($10\\,^\\circ\\text{C}$) o caliente ($45\\,^\\circ\\text{C}$), "
            "modificando la constante de autoionización del agua ($K_w$) y desplazando el pH neutro real."
        )

    with col_p2:
        st.subheader("3. Curva Sigmoidal de Valoración")
        st.write(
            "Al agregar reactivo neutralizante, el pH no cambia de manera

  
