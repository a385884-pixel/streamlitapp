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
    page_title="ChemPH - Ingeniería Química y Control de pH",
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
    """Genera la curva sigmoidal de valoración ácido-base."""
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

    dosis_eje = np.linspace(0, max(dosis_req * 2.0, 0.5), 120)
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
st.sidebar.title("🧪 Proyecto ChemPH")
st.sidebar.markdown("### 🎯 Objetivo General")
st.sidebar.info(
    "Demostrar cómo los fundamentos teóricos del **pH y la neutralización ácido-base** "
    "estudiados en el laboratorio de Química se escalan mediante balances de materia "
    "en **Ingeniería Química** para controlar descargas de aguas residuales en la industria de Chihuahua."
)

st.sidebar.markdown("### 📑 ¿Qué muestra cada pestaña?")
st.sidebar.markdown(
    """
    **1️⃣ Introducción:**  
    Por qué elegimos la Ingeniería Química, qué estudia esta carrera y su relación directa con el control de pH.

    **2️⃣ Parte Teórica:**  
    Explicación detallada de cada fórmula (qué significa y para qué sirve) y cómo funciona químicamente la neutralización.

    **3️⃣ Escala Industrial y Chihuahua:**  
    Cómo pasan los cálculos de mililitros a caudales industriales, empresas de Chihuahua que tratan agua y referencias bibliográficas.

    **4️⃣ Simulador ChemPH:**  
    Ejemplo industrial práctico paso a paso, controles interactivos de operación, gráficas descargables y bitácora de 24 horas.
    """
)
st.sidebar.markdown("---")
st.sidebar.caption("Desarrollado en Python con Streamlit, NumPy, Pandas, Matplotlib y Plotly.")

# =========================================================
# 5. ENCABEZADO Y ESTRUCTURA DE 4 PESTAÑAS
# =========================================================
st.title("🧪 ChemPH: Del pH en el Laboratorio al Control Industrial")
st.caption("Aplicación de la Ingeniería Química en la Neutralización de Efluentes Industriales")

tab1, tab2, tab3, tab4 = st.tabs([
    "1️⃣ Introducción",
    "2️⃣ Parte Teórica",
    "3️⃣ Escala Industrial y Chihuahua",
    "4️⃣ Simulador ChemPH"
])

# ---------------------------------------------------------
# PESTAÑA 1: INTRODUCCIÓN
# ---------------------------------------------------------
with tab1:
    st.header("1. Introducción: La Ingeniería Química y el pH")

    col1, col2 = st.columns([1.3, 1])
    with col1:
        st.subheader("¿Por qué elegimos el tema de la Ingeniería Química?")
        st.write(
            "Elegimos enfocar este proyecto en la **Ingeniería Química** porque es la disciplina encargada de transformar "
            "materias primas y resolver problemas ambientales mediante procesos químicos controlados a gran escala. "
            "Muchas veces en las materias de Química vemos el pH únicamente como un número en un vaso de precipitados, "
            "pero en la ingeniería real ese valor define si una planta cumple la ley ambiental o si daña sus equipos y el ecosistema."
        )

        st.subheader("¿Qué es la Ingeniería Química?")
        st.write(
            "La **Ingeniería Química** combina los principios de la química, la física, las matemáticas y la biología "
            "para diseñar, operar y optimizar procesos industriales donde ocurren cambios en la composición o propiedades "
            "de la materia. Su objetivo es lograr que una reacción que funciona en mililitros dentro de un laboratorio "
            "opere de forma **segura, continua, económica y sustentable** a niveles de miles de litros por hora."
        )

    with col2:
        st.subheader("¿Cómo se relaciona con el pH?")
        st.info(
            "**El pH como variable crítica de control:**\n\n"
            "- **Protección de infraestructura:** Un efluente muy ácido ($pH < 5$) corroe tuberías metálicas, bombas y redes de drenaje.\n"
            "- **Tratamiento biológico:** Las bacterias que depuran el agua en una planta tratadora mueren si el pH sale del rango $6.5 - 8.5$.\n"
            "- **Precipitación de contaminantes:** Ajustar el pH permite separar metales pesados disueltos en forma de hidróxidos sólidos.\n"
            "- **Calidad de producto:** En alimentos, fármacos y recubrimientos metálicos, el pH controla la velocidad y eficiencia de reacción."
        )

# ---------------------------------------------------------
# PESTAÑA 2: PARTE TEÓRICA (FÓRMULAS EXPLICADAS Y NEUTRALIZACIÓN)
# ---------------------------------------------------------
with tab2:
    st.header("2. Parte Teórica: Fórmulas y Fundamento de la Neutralización")

    st.subheader("¿Cómo funciona la neutralización?")
    st.write(
        "La **neutralización** es una reacción química entre un **ácido** (sustancia que libera iones hidrógeno $H^+$) "
        "y una **base o álcali** (sustancia que aporta iones hidroxilo $OH^-$). Al mezclarse en un tanque reactor con agitación, "
        "los iones $H^+$ y $OH^-$ se combinan para formar **agua ($H_2O$)** y una sal disuelta, desplazando el pH del efluente "
        "hacia un punto neutro seguro (cercano a $pH = 7.0$)."
    )
    st.latex(r"H^+_{(ac)} + OH^-_{(ac)} \longrightarrow H_2O_{(l)} \quad (\Delta H^\circ = -57.3\text{ kJ/mol})")

    st.markdown("---")
    st.subheader("Fórmulas Fundamentales: Qué significan y para qué sirven")

    # Fórmula 1
    st.markdown("#### 1. Definición de pH y Concentración de Iones Hidrógeno")
    c_f1, c_f2 = st.columns([1, 1.4])
    with c_f1:
        st.latex(r"\text{pH} = -\log_{10}[H^+] \quad \Longrightarrow \quad [H^+] = 10^{-\text{pH}}")
    with c_f2:
        st.markdown(
            "- **Explicación:** Relaciona la escala logarítmica de pH con la concentración molar real de iones hidrógeno $[H^+]$ en $\\text{mol/L}$.\n"
            "- **¿Para qué sirve?** Permite convertir la lectura digital de un potenciómetro (pH) en una cantidad química medible ($\\text{mol/L}$) "
            "para poder hacer cálculos estequiométricos."
        )

    # Fórmula 2
    st.markdown("#### 2. Producto Iónico del Agua ($K_w$) y Relación con pOH")
    c_f3, c_f4 = st.columns([1, 1.4])
    with c_f3:
        st.latex(r"K_w = [H^+][OH^-] \quad \Longrightarrow \quad \text{pH} + \text{pOH} = \text{p}K_w")
    with c_f4:
        st.markdown(
            "- **Explicación:** En cualquier solución acuosa, el producto de $[H^+]$ por $[OH^-]$ es constante a una temperatura dada ($K_w = 1.0 \\times 10^{-14}$ a $25\\,^\\circ\\text{C}$).\n"
            "- **¿Para qué sirve?** Sirve para calcular cuántos iones básicos $[OH^-]$ hay en el agua cuando conocemos el pH, y para corregir "
            "el punto neutro cuando el agua residual sale caliente del proceso."
        )

    # Fórmula 3
    st.markdown("#### 3. Escalamiento de Caudal Volumétrico")
    c_f5, c_f6 = st.columns([1, 1.4])
    with c_f5:
        st.latex(r"Q_{\text{L/h}} = \dot{V}_{\text{m}^3/\text{h}} \times 1000\,\frac{\text{L}}{\text{m}^3}")
    with c_f6:
        st.markdown(
            "- **Explicación:** Transforma el flujo volumétrico medido en la tubería de la planta ($\\text{m}^3/\\text{h}$) a litros por hora ($\\text{L/h}$).\n"
            "- **¿Para qué sirve?** Homologa las unidades del caudal industrial con las unidades de concentración química ($\\text{mol/L}$)."
        )

    # Fórmula 4
    st.markdown("#### 4. Flujo Molar de Carga Iónica a Neutralizar")
    c_f7, c_f8 = st.columns([1, 1.4])
    with c_f7:
        st.latex(r"\dot{n}_{\text{eq}} = \left| C_{\text{net, entrada}} - C_{\text{net, objetivo}} \right| \times Q_{\text{L/h}}")
    with c_f8:
        st.markdown(
            "- **Explicación:** Multiplica la diferencia de concentración iónica entre el agua cruda y la norma ($\\text{eq/L}$) por el caudal ($\\text{L/h}$).\n"
            "- **¿Para qué sirve?** Determina exactamente cuántos **equivalentes químicos por hora ($\\text{eq/h}$)** de ácido o base deben "
            "alimentarse al tanque reactor para alcanzar el pH deseado."
        )

    # Fórmula 5
    st.markdown("#### 5. Dosificación Másica de Reactivo Industrial")
    c_f9, c_f10 = st.columns([1, 1.4])
    with c_f9:
        st.latex(r"\dot{m}_{\text{reactivo}} \left[\frac{\text{kg}}{\text{h}}\right] = \frac{\dot{n}_{\text{eq}}}{\nu_{\text{eq}}} \times \frac{PM}{1000}")
    with c_f10:
        st.markdown(
            "- **Explicación:** Convierte los equivalentes por hora ($\\dot{n}_{\\text{eq}}$) a masa usando el peso molecular ($PM$, en $\\text{g/mol}$) "
            "y la valencia equivalente del reactivo ($\\nu_{\\text{eq}}$, en $\\text{eq/mol}$).\n"
            "- **¿Para qué sirve?** Entrega el dato operativo real en **kilogramos por hora ($\\text{kg/h}$)** con el que el ingeniero programa "
            "las bombas dosificadoras y calcula el costo diario de insumos."
        )

# ---------------------------------------------------------
# PESTAÑA 3: ESCALA INDUSTRIAL, CHIHUAHUA Y BIBLIOGRAFÍA
# ---------------------------------------------------------
with tab3:
    st.header("3. Escala Industrial y Contexto en Chihuahua")

    st.subheader("¿Cómo escalan los cálculos de pH a la industria?")
    st.write(
        "En un laboratorio universitario se titulan muestras estáticas de $50\\text{ mL}$. En una **Planta de Tratamiento de Aguas Residuales (PTAR)** "
        "el flujo nunca se detiene: entran decenas de metros cúbicos cada hora. Por ello, los ingenieros químicos trabajan con **caudales ($\\text{m}^3/\\text{h}$)** "
        "y **flujos másicos ($\\text{kg/h}$)**, seleccionando reactivos según su eficiencia equivalente:"
    )

    df_reactivos_info = pd.DataFrame({
        "Reactivo Industrial": [
            "Hidróxido de Sodio (NaOH)",
            "Hidróxido de Calcio (Ca(OH)2)",
            "Ácido Sulfúrico (H2SO4)",
            "Ácido Clorhídrico (HCl)"
        ],
        "Función": [
            "Neutralizar efluentes ácidos",
            "Neutralizar efluentes ácidos (alto caudal)",
            "Neutralizar efluentes básicos/alcalinos",
            "Neutralizar efluentes básicos sin sulfatos"
        ],
        "Peso Molecular (g/mol)": [39.99, 74.09, 98.07, 36.46],
        "Valencia (eq/mol)": [1, 2, 2, 1],
        "Ventaja en Planta": [
            "Rápida disolución y dosificación líquida precisa",
            "Aporta 2 OH⁻ por mol: requiere menor masa y costo",
            "Alto poder acidificante y bajo costo por tonelada",
            "Evita incrustaciones de sulfato de calcio en tuberías"
        ]
    })
    st.dataframe(df_reactivos_info, use_container_width=True)

    st.markdown("---")
    st.subheader("Empresas y Organismos en Chihuahua Relacionados con el Control de pH")
    col_ch1, col_ch2 = st.columns(2)
    with col_ch1:
        st.markdown(
            "- **JMAS Chihuahua (Junta Municipal de Agua y Saneamiento):** Opera las plantas **PTAR Norte** y **PTAR Sur**, "
            "vigilando que las descargas industriales al alcantarillado cumplan la norma y suministrando agua tratada (línea morada) "
            "a los parques industriales de la ciudad.\n"
            "- **Industria Metalmecánica y Aeroespacial (Complejo Industrial Chihuahua, El Saucito, Supra):** Plantas de maquinado, "
            "anodizado y recubrimientos metálicos generan aguas ácidas ($\\text{pH } 2.0 - 4.0$) por decapado químico que deben "
            "neutralizarse antes de descargarse."
        )
    with col_ch2:
        st.markdown(
            "- **Industria Alimentaria y Láctea (Grupo Bafar, Zaragoza / Alpura):** Sus procesos de lavado sanitario CIP (*Clean-In-Place*) "
            "con sosa cáustica producen efluentes alcalinos ($\\text{pH } 10.5 - 12.5$) que requieren dosificación de ácido.\n"
            "- **Normatividad Oficial Mexicana Aplicable:**\n"
            "  - **NOM-002-SEMARNAT-1996:** Exige un rango de **pH de 5.5 a 10.0** para descargar al alcantarillado municipal.\n"
            "  - **NOM-001-SEMARNAT-2021:** Exige un rango estricto de **pH de 6.0 a 9.0** para descargas en ríos o cuerpos receptores."
        )

    st.markdown("---")
    st.subheader("📚 Bibliografía y Referencias")
    st.markdown(
        """
        1. **Chang, R., & Goldsby, K. A.** (2017). *Química* (12.ª ed.). McGraw-Hill Education. (Equilibrios ácido-base, autoionización del agua y curvas de valoración).
        2. **Housecroft, C. E., & Sharpe, A. G.** (2018). *Química Inorgánica* (4.ª ed.). Pearson Educación. (Química de disoluciones acuosas y fuerza de ácidos y bases).
        3. **Felder, R. M., & Rousseau, R. W.** (2016). *Principios Elementales de los Procesos Químicos* (4.ª ed.). Limusa Wiley. (Balances de materia en procesos continuos).
        4. **Metcalf & Eddy, Inc.** (2014). *Wastewater Engineering: Treatment and Resource Recovery* (5th ed.). McGraw-Hill. (Neutralización química de aguas residuales industriales).
        5. **SEMARNAT.** (1998). *Norma Oficial Mexicana NOM-002-SEMARNAT-1996* (Límites máximos permisibles en descargas al alcantarillado urbano o municipal). Diario Oficial de la Federación.
        6. **SEMARNAT.** (2022). *Norma Oficial Mexicana NOM-001-SEMARNAT-2021* (Límites permisibles en descargas de aguas residuales en cuerpos receptores). Diario Oficial de la Federación.
        7. **Junta Municipal de Agua y Saneamiento de Chihuahua (JMAS).** *Reglamento y Lineamientos Técnicos para Descargas Industriales y Operación de PTAR Norte y Sur, Chihuahua, Chih.*
        """
    )

# ---------------------------------------------------------
# PESTAÑA 4: SIMULADOR CHEMPH Y EJEMPLO PRÁCTICO INDUSTRIAL
# ---------------------------------------------------------
with tab4:
    st.header("4. Simulador Interactivo ChemPH")

    # EJEMPLO PRÁCTICO INDUSTRIAL DENTRO DE LA SIMULACIÓN
    with st.expander("📌 Ejemplo Industrial Práctico (Planta Metalmecánica en Chihuahua) — Haz clic para ver el desarrollo", expanded=True):
        st.write(
            "**Caso Práctico:** Una empresa de tratamientos superficiales en el **Complejo Industrial Chihuahua** descarga "
            "**$40\\text{ m}^3/\\text{h}$** de agua ácida de enjuague con **$pH_{\\text{entrada}} = 3.0$** a **$25\\,^\\circ\\text{C}$**, "
            "y necesita llevarla a **$pH_{\\text{objetivo}} = 7.0$** para cumplir la norma."
        )
        dosis_ej_naoh = calcular_dosificacion(40.0, 3.0, 7.0, "Hidróxido de Sodio (NaOH)", 25.0)
        dosis_ej_caoh = calcular_dosificacion(40.0, 3.0, 7.0, "Hidróxido de Calcio (Ca(OH)2)", 25.0)

        st.markdown(
            f"""
            **Resolución paso a paso con las fórmulas vistas:**
            1. **Caudal en litros/hora:** $Q = 40\\text{{ m}}^3/\\text{{h}} \\times 1000 = 40,000\\text{{ L/h}}$.
            2. **Concentración inicial de protones:** $[H^+] = 10^{{-3.0}} = 0.001\\text{{ mol/L}}$ (en $pH = 7.0$, $[H^+] = 10^{{-7}}\\text{{ mol/L}}$).
            3. **Flujo molar a neutralizar:** $\\dot{{n}}_{{\\text{{eq}}}} = 0.001\\text{{ eq/L}} \\times 40,000\\text{{ L/h}} = 40.0\\text{{ eq/h}}$.
            4. **Dosificación necesaria:**
               - Usando **$NaOH$** ($PM = 39.99$, $\\nu = 1$): **{dosis_ej_naoh:.2f} kg/h** (**{dosis_ej_naoh*24:.1f} kg/día**).
               - Usando **$Ca(OH)_2$** ($PM = 74.09$, $\\nu = 2$): **{dosis_ej_caoh:.2f} kg/h** (**{dosis_ej_caoh*24:.1f} kg/día**), logrando un ahorro de **{(dosis_ej_naoh - dosis_ej_caoh)*24:.1f} kg/día** de reactivo gracias al análisis estequiométrico.
            """
        )

    st.markdown("---")
    st.subheader("🎛️ Panel de Control del Simulador")
    st.caption("Ajusta los parámetros operativos para observar cómo cambian la dosificación, las gráficas y la bitácora:")

    # CONTROLES INTERACTIVOS AQUÍ MISMO EN LA SIMULACIÓN
    c_ctrl1, c_ctrl2, c_ctrl3, c_ctrl4 = st.columns(4)
    with c_ctrl1:
        caudal = st.number_input("Caudal del Efluente (m³/h):", min_value=1.0, max_value=500.0, value=40.0, step=5.0)
    with c_ctrl2:
        ph_entrada = st.slider("pH de Entrada:", min_value=0.0, max_value=14.0, value=3.0, step=0.1)
    with c_ctrl3:
        ph_salida = st.slider("pH Objetivo (Norma):", min_value=6.0, max_value=9.0, value=7.0, step=0.1)
    with c_ctrl4:
        temp_efluente = st.slider("Temperatura (°C):", min_value=5.0, max_value=50.0, value=25.0, step=1.0)

    kw_actual, pkw_actual, ph_neutro_T = calcular_kw(temp_efluente)

    col_sel1, col_sel2 = st.columns([1, 2])
    with col_sel1:
        if ph_entrada < ph_salida:
            opciones_reactivos = ["Hidróxido de Sodio (NaOH)", "Hidróxido de Calcio (Ca(OH)2)"]
            tipo_efluente = "💧 Efluente Ácido → Dosificar Base"
        else:
            opciones_reactivos = ["Ácido Sulfúrico (H2SO4)", "Ácido Clorhídrico (HCl)"]
            tipo_efluente = "🔥 Efluente Básico → Dosificar Ácido"

        reactivo_sel = st.selectbox("Reactivo Neutralizante:", opciones_reactivos)

    with col_sel2:
        st.write("")
        if ph_entrada <= 2.5 or ph_entrada >= 11.5:
            st.error(f"**{tipo_efluente}** | ⚠️ **pH Extremo:** Se recomienda neutralización en 2 etapas en serie para evitar calentamiento excesivo.")
        elif temp_efluente >= 35.0:
            st.warning(f"**{tipo_efluente}** | 🌡️ **Temperatura Alta ({temp_efluente} °C):** El pH neutro real se desplaza a **{ph_neutro_T:.2f}**.")
        else:
            st.success(f"**{tipo_efluente}** | ✅ **Operación Estable:** Tiempo de residencia recomendado de 15 a 20 min con agitación continua.")

    # CÁLCULOS EN TIEMPO REAL
    dosis_kgh = calcular_dosificacion(caudal, ph_entrada, ph_salida, reactivo_sel, temp_efluente)
    h_in, oh_in = calcular_concentraciones(ph_entrada, temp_efluente)
    h_out, oh_out = calcular_concentraciones(ph_salida, temp_efluente)
    factor_cambio = 10**abs(ph_salida - ph_entrada)

    # MÉTRICAS PRINCIPALES
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Caudal Operativo", f"{caudal} m³/h", f"{caudal*1000:,.0f} L/h")
    m2.metric("Cambio de pH", f"{ph_entrada} → {ph_salida}", f"ΔpH = {ph_salida - ph_entrada:+.1f}")
    m3.metric("Reactivo Requerido", f"{dosis_kgh:.2f} kg/h", f"{dosis_kgh*24:.1f} kg/día")
    m4.metric("pH Neutro a T (°C)", f"{ph_neutro_T:.2f}", f"Kw = {kw_actual:.2e}")

    st.markdown("---")

    # GRÁFICAS FUNCIONALES CON EXPLICACIÓN Y DESCARGA DE IMAGEN
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("📈 Curva de Valoración Industrial (Plotly)")
        dosis_eje, ph_curva, dosis_req = generar_curva_titulacion(
            caudal, ph_entrada, ph_salida, reactivo_sel, temp_efluente
        )
        fig_plotly = go.Figure()
        fig_plotly.add_trace(go.Scatter(
            x=dosis_eje, y=ph_curva, mode='lines',
            name='Curva de Titulación',
            line=dict(color='#0275d8', width=3)
        ))
        fig_plotly.add_hline(y=ph_salida, line_dash="dash", line_color="green", annotation_text=f"pH Norma ({ph_salida})")
        fig_plotly.add_vline(x=dosis_req, line_dash="dash", line_color="red", annotation_text=f"Dosis: {dosis_req:.2f} kg/h")
        fig_plotly.update_layout(
            xaxis_title=f"Flujo de {reactivo_sel} (kg/h)",
            yaxis_title="pH Resultante",
            yaxis=dict(range=[0, 14]),
            height=370
        )
        st.plotly_chart(fig_plotly, use_container_width=True)
        st.caption("💡 Puedes descargar esta gráfica como imagen PNG usando el ícono de cámara 📷 en la esquina superior derecha del gráfico.")
        st.info(
            f"**¿Qué cambia en esta gráfica?** Al variar el caudal ({caudal} m³/h) o el pH de entrada ({ph_entrada}), "
            f"la línea vertical roja se mueve indicando los **{dosis_req:.2f} kg/h** exactos necesarios para cruzar la meta verde. "
            f"La zona vertical muestra qué tan sensible es el agua cerca de la neutralidad."
        )

    with col_g2:
        st.subheader("⚖️ Balance de Iones Entrada vs. Salida (Matplotlib)")
        fig_mat, ax = plt.subplots(figsize=(5.5, 4.0))
        etiquetas = ['[H⁺] Entrada', '[H⁺] Salida', '[OH⁻] Entrada', '[OH⁻] Salida']
        valores = [h_in, h_out, oh_in, oh_out]
        colores = ['#d9534f', '#f0ad4e', '#0275d8', '#5bc0de']

        ax.bar(etiquetas, valores, color=colores)
        ax.set_yscale('log')
        ax.set_ylim(1e-15, 10)
        ax.set_ylabel('Concentración Molar (mol/L) [Escala Log]')
        ax.set_title(f'Cambio de Concentración Iónica a {temp_efluente} °C')
        ax.grid(True, which="both", ls="--", alpha=0.5)
        plt.xticks(rotation=15)
        plt.tight_layout()
        st.pyplot(fig_mat)

        # Exportar figura de Matplotlib a PNG usando librería nativa io
        buffer_png = io.BytesIO()
        fig_mat.savefig(buffer_png, format="png", dpi=200)
        buffer_png.seek(0)
        plt.close(fig_mat)

        st.download_button(
            label="📥 Descargar Gráfica de Iones (PNG)",
            data=buffer_png,
            file_name="grafica_balance_iones_chemph.png",
            mime="image/png"
        )
        st.info(
            f"**¿Qué cambia en esta gráfica?** Muestra en escala logarítmica cómo se reducen los iones contaminantes: "
            f"para pasar de **pH {ph_entrada}** a **pH {ph_salida}**, la concentración de $H^+$ cambia en un factor de "
            f"**{factor_cambio:,.1f} veces** (de `{h_in:.2e}` a `{h_out:.2e}` mol/L)."
        )

    st.markdown("---")
    st.subheader("📋 Bitácora de Operación Simulada (Turno de 24 Horas)")

    np.random.seed(42)
    horas = [f"{i:02d}:00 HRS" for i in range(24)]
    ph_simulado = np.clip(np.random.normal(loc=ph_entrada, scale=0.20, size=24), 0.1, 13.9).round(2)
    caudal_simulado = np.clip(np.random.normal(loc=caudal, scale=1.5, size=24), 1.0, 500.0).round(1)

    dosis_simuladas = [
        round(calcular_dosificacion(c, p, ph_salida, reactivo_sel, temp_efluente), 2)
        for c, p in zip(caudal_simulado, ph_simulado)
    ]

    df_turno = pd.DataFrame({
        "Hora": horas,
        "pH Entrada": ph_simulado,
        "Caudal (m³/h)": caudal_simulado,
        "Temp (°C)": [temp_efluente] * 24,
        "Reactivo": reactivo_sel,
        "Dosis Necesaria (kg/h)": dosis_simuladas,
        "pH Salida Norma": [ph_salida] * 24
    })

    st.dataframe(df_turno, use_container_width=True)

    st.download_button(
        label="📥 Descargar Bitácora de Operación (CSV)",
        data=df_turno.to_csv(index=False).encode('utf-8'),
        file_name="bitacora_operacion_PTAR_Chihuahua.csv",
        mime="text/csv"
    )
