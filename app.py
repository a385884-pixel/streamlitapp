# =========================================================
# 1. IMPORTACIÓN DE LIBRERÍAS
# =========================================================
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# =========================================================
# 2. CONFIGURACIÓN DE PÁGINA
# =========================================================
st.set_page_config(
    page_title="ChemPH - Del Laboratorio al Control Industrial",
    page_icon="🧪",
    layout="wide")

# =========================================================
# 3. FUNCIONES DE INGENIERÍA QUÍMICA Y TERMODINÁMICA
# =========================================================
def calcular_kw(temp_c):
    """
    Calcula la constante de autoionización del agua (Kw) en función de la temperatura (°C).
    A 25 °C, pKw = 14.0 (Kw = 1e-14). En climas extremos o descargas calientes, Kw varía.
    """
    pkw = 14.0 - 0.033 * (temp_c - 25.0)
    kw = 10**(-pkw)
    ph_neutro = pkw / 2.0
    return kw, pkw, ph_neutro

def calcular_concentraciones(ph, temp_c=25.0):
    """Calcula la molaridad de los iones [H+] y [OH-] considerando Kw(T)."""
    kw, _, _ = calcular_kw(temp_c)
    h_conc = 10**(-ph)
    oh_conc = kw / h_conc
    return h_conc, oh_conc

def calcular_dosificacion(caudal_m3h, ph_in, ph_out, reactivo, temp_c=25.0):
    """
    Calcula el flujo másico de reactivo (kg/h) necesario para neutralizar
    un caudal industrial mediante balance de carga iónica ([H+] - [OH-]).
    """
    kw, _, _ = calcular_kw(temp_c)
    caudal_L_h = caudal_m3h * 1000.0  # Escalamiento dimensional: m³/h -> L/h

    # Carga neta inicial y final (mol/L)
    c_net_in = (10**(-ph_in)) - (kw / (10**(-ph_in)))
    c_net_out = (10**(-ph_out)) - (kw / (10**(-ph_out)))

    delta_eq_L = abs(c_net_in - c_net_out)
    moles_eq_h = delta_eq_L * caudal_L_h

    # Base de datos de reactivos industriales: (Peso Molecular g/mol, Valencia equivalente eq/mol)
    datos_reactivos = {
        "Hidróxido de Sodio (NaOH)": (39.99, 1),
        "Hidróxido de Calcio (Ca(OH)2)": (74.09, 2),
        "Ácido Sulfúrico (H2SO4)": (98.07, 2),
        "Ácido Clorhídrico (HCl)": (36.46, 1)}
    pm, eq = datos_reactivos[reactivo]

    # Flujo másico requerido en kg/h
    return ((moles_eq_h / eq) * pm) / 1000.0

def generar_curva_titulacion(caudal_m3h, ph_in, ph_out, reactivo, temp_c=25.0):
    """
    Calcula la curva sigmoidal real de valoración ácido-base (Química Inorgánica III)
    resolviendo la ecuación cuadrática de equilibrio iónico del agua en cada punto de dosis.
    """
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

    # Equivalentes añadidos por litro de efluente en cada paso de dosificación
    eq_anadidos_L = ((dosis_eje * 1000.0) / pm * eq) / caudal_L_h

    if ph_in < ph_out:
        # Adición de base (reduce acidez neta)
        c_net_array = c_net_in - eq_anadidos_L
    else:
        # Adición de ácido (incrementa acidez neta)
        c_net_array = c_net_in + eq_anadidos_L

    # Solución exacta de equilibrio: [H+]^2 - C_net*[H+] - Kw = 0
    h_array = (c_net_array + np.sqrt(c_net_array**2 + 4.0 * kw)) / 2.0
    ph_curva = np.clip(-np.log10(h_array), 0.0, 14.0)

    return dosis_eje, ph_curva, dosis_req

# =========================================================
# 4. BARRA LATERAL (PARÁMETROS DE OPERACIÓN GLOBALES)
# =========================================================
st.sidebar.header("⚙️ Parámetros de Operación PTAR")
st.sidebar.caption("Modifica estas variables para actualizar el simulador y los cálculos industriales:")

caudal = st.sidebar.number_input(
    "Caudal del Efluente (m³/h):",
    min_value=1.0, max_value=500.0, value=40.0, step=5.0
)
ph_entrada = st.sidebar.slider(
    "pH Medido de Entrada:",
    min_value=0.0, max_value=14.0, value=3.0, step=0.1
)
ph_salida = st.sidebar.slider(
    "pH Objetivo de Descarga (Norma):",
    min_value=6.0, max_value=9.0, value=7.0, step=0.1
)
temp_efluente = st.sidebar.slider(
    "Temperatura del Efluente (°C):",
    min_value=5.0, max_value=50.0, value=25.0, step=1.0,
    help="En Chihuahua las temperaturas ambientales y de proceso varían entre 5 °C y 45 °C, modificando Kw."
)

kw_actual, pkw_actual, ph_neutro_T = calcular_kw(temp_efluente)

# Selección dinámica de reactivo según acidez o basicidad
if ph_entrada < ph_salida:
    opciones_reactivos = ["Hidróxido de Sodio (NaOH)", "Hidróxido de Calcio (Ca(OH)2)"]
    st.sidebar.info("💧 **Efluente Ácido:** Se requiere dosificación de álcali (base).")
else:
    opciones_reactivos = ["Ácido Sulfúrico (H2SO4)", "Ácido Clorhídrico (HCl)"]
    st.sidebar.info("🔥 **Efluente Básico:** Se requiere dosificación de ácido.")

reactivo_sel = st.sidebar.selectbox("Reactivo Neutralizante:", opciones_reactivos)

# Recomendación operativa automática según clima/temperatura y pH
st.sidebar.markdown("---")
st.sidebar.subheader("🩺 Recomendación Operativa")
if ph_entrada <= 2.5 or ph_entrada >= 11.5:
    st.sidebar.error("⚠️ **pH Extremo:** Dosificar en 2 etapas (tanques en serie) para evitar choques térmicos por calor de neutralización y corrosión en tuberías.")
elif temp_efluente >= 35.0:
    st.sidebar.warning(f"🌡️ **Alta Temperatura ({temp_efluente} °C):** El pH neutro real se desplaza a **{ph_neutro_T:.2f}**. Verificar calibración de compensación automática de temperatura (ATC) en el electrodo.")
else:
    st.sidebar.success("✅ **Condición Estable:** Control PID en una etapa con agitación continua (tiempo de residencia hidráulico recomendado: 15–20 min).")

# =========================================================
# 5. ENCABEZADO PRINCIPAL Y NAVEGACIÓN EN 6 SECCIONES
# =========================================================
st.title("🧪 Del pH en el laboratorio al control industrial")
st.markdown("**Aplicaciones de la ingeniería química en los procesos de neutralización de efluentes (ChemPH PTAR)**")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "1️⃣ Portada: Ingeniería Química y pH",
    "2️⃣ Fundamentos Químicos",
    "3️⃣ De la Escuela a la Industria",
    "4️⃣ Caso Industrial en Chihuahua",
    "5️⃣ Simulador ChemPH",
    "6️⃣ Bibliografía y Referencias"
])

# ---------------------------------------------------------
# SECCIÓN 1: PORTADA: INGENIERÍA QUÍMICA Y EL pH
# ---------------------------------------------------------
with tab1:
    st.header("1. Ingeniería Química y el Control del pH")
    
    col_p1, col_p2 = st.columns([1.4, 1])
    with col_p1:
        st.subheader("¿Qué es la Ingeniería Química y cómo se relaciona con el pH?")
        st.write(
            "La **Ingeniería Química** es la rama de la ingeniería encargada de diseñar, operar, controlar y optimizar "
            "procesos donde la materia experimenta transformaciones físicas, químicas o biológicas a escala industrial. "
            "Mientras que en el laboratorio se trabaja con mililitros en matraces, el ingeniero químico escala esas reacciones "
            "a **miles de litros por hora** manteniendo seguridad, rentabilidad y cumplimiento ambiental."
        )
        st.write(
            "Dentro de las variables críticas de proceso (temperatura, presión, flujo y concentración), el **pH** es uno de los "
            "parámetros más determinantes porque gobierna la velocidad de reacción, la corrosión de equipos metálicos, "
            "la solubilidad de metales pesados, la actividad enzimática en biorreactores y la viabilidad de los ecosistemas receptores."
        )

    with col_p2:
        st.info(
            "### Importancia del pH en la Industria\n"
            "- **Tratamiento de Aguas (PTAR):** Neutralización obligatoria antes de descargar al drenaje o ríos.\n"
            "- **Metalmecánica y Galvanoplastia:** Control de baños de decapado ácido y precipitación de hidróxidos metálicos.\n"
            "- **Industria Alimentaria y Láctea:** Control de fermentación, pasteurización y lavado alcalino CIP.\n"
            "- **Minería e Hidrometalurgia:** Lixiviación selectiva de minerales y control de drenaje ácido."
        )

    st.markdown("---")
    st.subheader("¿Cómo funciona el tratamiento de neutralización en una PTAR?")
    c_et1, c_et2, c_et3 = st.columns(3)
    with c_et1:
        st.markdown("**1. Homogeneización**")
        st.caption("El agua residual industrial llega con pH variable a un tanque pulmón que amortigua picos de caudal y concentración.")
    with c_et2:
        st.markdown("**2. Dosificación y Mezcla Rápida**")
        st.caption("Un sensor de pH envía señal al controlador, el cual activa bombas dosificadoras de ácido o base en un reactor agitado.")
    with c_et3:
        st.markdown("**3. Verificación y Descarga**")
        st.caption("Se confirma que el efluente cumpla el rango normativo (pH 6.0 – 9.0) antes de su descarga o reúso industrial.")

# ---------------------------------------------------------
# SECCIÓN 2: FUNDAMENTOS QUÍMICOS (QUÍMICA INORGÁNICA III)
# ---------------------------------------------------------
with tab2:
    st.header("2. Fundamentos Químicos (Química Inorgánica III)")
    st.write(
        "El concepto de **pH** (potencial de hidrógeno), introducido por Søren Sørensen en 1909, mide la actividad "
        "de los iones hidronio ($H_3O^+$ o $H^+$) en disolución acuosa mediante una escala logarítmica inversa."
    )

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.subheader("Ecuaciones de Equilibrio Ácido-Base")
        st.latex(r"\text{pH} = -\log_{10}[H^+] \quad \Longleftrightarrow \quad [H^+] = 10^{-\text{pH}}")
        st.latex(r"\text{pOH} = -\log_{10}[OH^-] \quad \Longleftrightarrow \quad [OH^-] = 10^{-\text{pOH}}")
        st.latex(r"K_w = [H^+][OH^-] = 1.0 \times 10^{-14} \quad (\text{a } 25\,^\circ\text{C})")
        st.latex(r"\text{pH} + \text{pOH} = \text{p}K_w")
        st.warning(
            "**Naturaleza Logarítmica:** Un cambio de **1 unidad de pH** representa un cambio de **10 veces** en la concentración de $H^+$. "
            "Un efluente a $\\text{pH } 3$ es **1,000 veces más ácido** que uno a $\\text{pH } 6$."
        )

    with col_f2:
        st.subheader("Neutralización y Uso de la Curva de Valoración")
        st.write(
            "La **reacción de neutralización** entre un ácido fuerte y una base fuerte produce sal y agua:"
        )
        st.latex(r"H^+_{(ac)} + OH^-_{(ac)} \longrightarrow H_2O_{(l)} \quad (\Delta H^\circ = -57.3\text{ kJ/mol})")
        st.write(
            "**¿Para qué sirve una Curva de Valoración (Titulación)?**\n"
            "1. **Identificar el punto de equivalencia:** Muestra exactamente cuántos moles o kg/h de reactivo se requieren para alcanzar la neutralidad.\n"
            "2. **Visualizar la zona de alta sensibilidad:** Alrededor de $\\text{pH } 7$, la curva tiene una pendiente casi vertical; "
            "una mínima sobredosificación dispara el pH hacia extremos alcalinos o ácidos.\n"
            "3. **Seleccionar el reactivo óptimo:** Permite comparar la eficiencia entre reactivos monopróticos ($NaOH, HCl$) y dipróticos ($Ca(OH)_2, H_2SO_4$)."
        )

# ---------------------------------------------------------
# SECCIÓN 3: DE LA ESCUELA A LA INDUSTRIA (ESCALAMIENTO)
# ---------------------------------------------------------
with tab3:
    st.header("3. De la Escuela a la Industria: Escalamiento Dimensional")
    st.write(
        "En las prácticas universitarias calculamos molaridad ($\\text{mol/L}$) y volúmenes de bureta ($\\text{mL}$). "
        "En una Planta de Tratamiento de Aguas Residuales (PTAR), esas mismas ecuaciones se transforman en **flujos continuos** "
        "(balances de materia en estado estacionario)."
    )

    col_e1, col_e2 = st.columns(2)
    with col_e1:
        st.subheader("Paso 1: Conversión de Caudal Volumétrico")
        st.latex(r"Q_{\text{L/h}} = \dot{V}_{\text{m}^3/\text{h}} \times 1000\,\frac{\text{L}}{\text{m}^3}")
        
        st.subheader("Paso 2: Flujo Molar de Carga Iónica")
        st.latex(r"\Delta C = \left| C_{\text{net, in}} - C_{\text{net, out}} \right| \quad \left[\frac{\text{eq}}{\text{L}}\right]")
        st.latex(r"\dot{n}_{\text{eq}} = \Delta C \times Q_{\text{L/h}} \quad \left[\frac{\text{eq}}{\text{h}}\right]")

    with col_e2:
        st.subheader("Paso 3: Estequiometría y Flujo Másico (kg/h)")
        st.latex(r"\dot{m}_{\text{reactivo}} \left[\frac{\text{kg}}{\text{h}}\right] = \frac{\dot{n}_{\text{eq}} \left[\frac{\text{eq}}{\text{h}}\right]}{\nu_{\text{eq}} \left[\frac{\text{eq}}{\text{mol}}\right]} \times PM \left[\frac{\text{g}}{\text{mol}}\right] \times \frac{1\,\text{kg}}{1000\,\text{g}}")
        st.info(
            "**Importancia del Factor de Valencia ($\\nu_{\\text{eq}}$):**\n"
            "- El **$NaOH$** aporta $1\\text{ mol } OH^-$ por mol ($PM = 39.99\\text{ g/mol}$).\n"
            "- El **$Ca(OH)_2$** (cal hidratada) aporta **$2\\text{ moles } OH^-$** por mol ($PM = 74.09\\text{ g/mol}$), "
            "por lo que su peso equivalente es $37.05\\text{ g/eq}$, logrando neutralizar con menor masa."
        )

    st.markdown("---")
    st.subheader("Tabla Comparativa de Reactivos Industriales Utilizados en ChemPH")
    df_reactivos_info = pd.DataFrame({
        "Reactivo": ["Hidróxido de Sodio (NaOH)", "Hidróxido de Calcio (Ca(OH)2)", "Ácido Sulfúrico (H2SO4)", "Ácido Clorhídrico (HCl)"],
        "Tipo": ["Base Fuerte (Álcali)", "Base Fuerte (Cal hidratada)", "Ácido Fuerte Diprótico", "Ácido Fuerte Monoprótico"],
        "Peso Molecular (g/mol)": [39.99, 74.09, 98.07, 36.46],
        "Valencia (eq/mol)": [1, 2, 2, 1],
        "Peso Equivalente (g/eq)": [39.99, 37.05, 49.04, 36.46],
        "Aplicación Típica en PTAR": [
            "Control fino y rápido en sistemas automatizados",
            "Neutralización de altos caudales ácidos a bajo costo",
            "Neutralización de efluentes alcalinos (lavados CIP)",
            "Ajuste de pH sin formación de sulfatos insolubles"
        ]
    })
    st.dataframe(df_reactivos_info, use_container_width=True)

# ---------------------------------------------------------
# SECCIÓN 4: CASO INDUSTRIAL EN CHIHUAHUA
# ---------------------------------------------------------
with tab4:
    st.header("4. Contexto Industrial y Caso Práctico en Chihuahua")
    
    st.write(
        "El estado de **Chihuahua** es una región semidesértica con alta actividad manufacturera donde el tratamiento y reúso del agua "
        "es estratégico para la sostenibilidad industrial y urbana."
    )

    col_ch1, col_ch2 = st.columns(2)
    with col_ch1:
        st.subheader("Empresas y Organismos en Chihuahua")
        st.markdown(
            "- **JMAS Chihuahua (Junta Municipal de Agua y Saneamiento):** Opera las plantas **PTAR Norte** y **PTAR Sur**, "
            "regulando las descargas industriales al alcantarillado municipal y suministrando agua tratada (línea morada) a parques industriales.\n"
            "- **Sector Metalmecánico y Aeroespacial (Complejo Industrial Chihuahua, El Saucito, Supra):** Empresas de recubrimientos, "
            "anodizado y estampado generan aguas ácidas ($\\text{pH } 2.0 - 4.0$) por decapado químico que requieren neutralización previa.\n"
            "- **Industria Alimentaria y Láctea (Grupo Bafar, Zaragoza / Alpura):** Generan efluentes alcalinos ($\\text{pH } 10.5 - 12.5$) "
            "debido al lavado sanitario CIP (*Clean-In-Place*) con sosa cáustica.\n"
            "- **Industria Cerámica y Minera (Interceramic, Grupo México):** Requieren estricto control de pH para sedimentación de sólidos y metales."
        )

    with col_ch2:
        st.subheader("Marco Normativo Aplicable en México")
        st.markdown(
            "- **NOM-002-SEMARNAT-1996:** Establece los límites máximos permisibles de contaminantes en descargas de aguas residuales "
            "a los sistemas de alcantarillado urbano o municipal (**rango de pH permitido: 5.5 a 10.0 unidades**).\n"
            "- **NOM-001-SEMARNAT-2021:** Regula las descargas en cuerpos receptores nacionales (ríos, arroyos, suelo) exigiendo un "
            "**rango estricto de pH entre 6.0 y 9.0 unidades**."
        )
        st.success(
            "**Impacto de la Ingeniería Química:** Sin neutralización, una descarga ácida corroe la red de alcantarillado de la JMAS "
            "e inhibe las bacterias de los reactores biológicos de la PTAR Sur."
        )

    st.markdown("---")
    st.subheader("📌 Ejemplo Práctico Resuelto: Planta Metalmecánica en el Complejo Industrial Chihuahua")
    st.write(
        "**Planteamiento del Problema:** Una planta de tratamientos superficiales metálicos ubicada en el Complejo Industrial Chihuahua "
        "genera un efluente continuo de **$40\\text{ m}^3/\\text{h}$** proveniente del enjuague de decapado ácido, con un **$pH_{\\text{entrada}} = 3.0$** "
        "a $25\\,^\\circ\\text{C}$. Se requiere neutralizarlo hasta **$pH_{\\text{objetivo}} = 7.0$** para cumplir la normativa y reutilizar el agua."
    )

    # Cálculo demostrativo del caso práctico
    dosis_naoh_ej = calcular_dosificacion(40.0, 3.0, 7.0, "Hidróxido de Sodio (NaOH)", 25.0)
    dosis_caoh_ej = calcular_dosificacion(40.0, 3.0, 7.0, "Hidróxido de Calcio (Ca(OH)2)", 25.0)

    c_ej1, c_ej2, c_ej3 = st.columns(3)
    c_ej1.metric("1. Caudal y Concentración", "40,000 L/h", "10⁻³ mol/L de H⁺")
    c_ej2.metric("2. Carga Ácida a Neutralizar", "40.0 eq/h", "960 eq/día (24 h)")
    c_ej3.metric("3. Ahorro por Ingeniería", f"{(dosis_naoh_ej - dosis_caoh_ej)*24:.2f} kg/día", "Usando Ca(OH)₂ vs NaOH")

    st.markdown(
        f"""
        **Desarrollo paso a paso:**
        1. **Conversión de caudal:** $Q = 40\\text{ m}^3/\\text{h} \\times 1000 = 40,000\\text{ L/h}$.
        2. **Concentración inicial de protones:** $[H^+] = 10^{{-3.0}} = 0.001\\text{ mol/L}$ (en $\\text{pH } 7.0$, $[H^+] = 10^{{-7}}\\text{ mol/L} \\approx 0$).
        3. **Moles de $H^+$ por hora:** $\\dot{{n}}_{{H^+}} = 0.001\\text{ mol/L} \\times 40,000\\text{ L/h} = 40\\text{ mol/h}$.
        4. **Comparación de dosificación por selección de reactivo:**
           - Con **Hidróxido de Sodio ($NaOH$, $PM=39.99$, $eq=1$):** se requieren **{dosis_naoh_ej:.2f} kg/h** ({dosis_naoh_ej*24:.2f} kg/día).
           - Con **Hidróxido de Calcio ($Ca(OH)_2$, $PM=74.09$, $eq=2$):** se requieren **{dosis_caoh_ej:.2f} kg/h** ({dosis_caoh_ej*24:.2f} kg/día).
        
        *Nota: Puedes probar estos mismos valores ($40\\text{ m}^3/\\text{h}$, $\\text{pH } 3.0 \\to 7.0$) en la pestaña **5️⃣ Simulador ChemPH** para visualizar la curva sigmoidal y descargar el reporte.*
        """
    )

# ---------------------------------------------------------
# SECCIÓN 5: SIMULADOR INTERACTIVO CHEMPH (ORIGINAL MEJORADO)
# ---------------------------------------------------------
with tab5:
    st.header("5. Simulador Interactivo ChemPH (Control de Proceso)")
    
    dosis_kgh = calcular_dosificacion(caudal, ph_entrada, ph_salida, reactivo_sel, temp_efluente)
    h_in, oh_in = calcular_concentraciones(ph_entrada, temp_efluente)
    h_out, oh_out = calcular_concentraciones(ph_salida, temp_efluente)
    factor_cambio = 10**abs(ph_salida - ph_entrada)

    # MÉTRICAS CLAVE
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Caudal Operativo", f"{caudal} m³/h", f"{caudal*1000:,.0f} L/h")
    col2.metric("pH Entrada → Objetivo", f"{ph_entrada} → {ph_salida}", f"ΔpH = {ph_salida - ph_entrada:+.1f}")
    col3.metric("Reactivo Requerido", f"{dosis_kgh:.2f} kg/h", f"{dosis_kgh*24:.1f} kg/día")
    col4.metric("pH Neutro a T Operativa", f"{ph_neutro_T:.2f}", f"T = {temp_efluente} °C")

    st.markdown("---")

    sub_graficas, sub_tabla = st.tabs(["📊 Gráficas Funcionales del Proceso", "📋 Registros de Operación (24 Horas - Pandas)"])

    with sub_graficas:
        col_g1, col_g2 = st.columns(2)

        # GRÁFICA 1: PLOTLY (CURVA SIGMOIDAL REAL DE TITULACIÓN)
        with col_g1:
            st.subheader("📈 Curva de Valoración Industrial (Plotly)")
            dosis_eje, ph_curva, dosis_req = generar_curva_titulacion(
                caudal, ph_entrada, ph_salida, reactivo_sel, temp_efluente
            )

            fig_plotly = go.Figure()
            fig_plotly.add_trace(go.Scatter(
                x=dosis_eje, y=ph_curva, mode='lines',
                name='Curva de Titulación (Equilibrio Kw)',
                line=dict(color='#0275d8', width=3)
            ))
            fig_plotly.add_hline(y=ph_salida, line_dash="dash", line_color="green", annotation_text=f"pH Norma ({ph_salida})")
            fig_plotly.add_vline(x=dosis_req, line_dash="dash", line_color="red", annotation_text=f"Dosis: {dosis_req:.2f} kg/h")
            fig_plotly.update_layout(
                xaxis_title=f"Flujo Másico de {reactivo_sel} (kg/h)",
                yaxis_title="pH Resultante en Tanque",
                yaxis=dict(range=[0, 14]),
                height=380
            )
            st.plotly_chart(fig_plotly, use_container_width=True)

            # Explicación dinámica de lo que cambia en la Gráfica 1
            st.info(
                f"**¿Qué muestra y qué cambia en esta gráfica?**\n"
                f"- Muestra la **respuesta logarítmica real (sigmoidal)** del efluente al dosificar **{reactivo_sel}**.\n"
                f"- Al aumentar el caudal ({caudal} m³/h) o alejar el pH de entrada ({ph_entrada}) del objetivo ({ph_salida}), "
                f"la línea vertical roja se desplaza a la derecha exigiendo **{dosis_req:.2f} kg/h**.\n"
                f"- Observa el **salto brusco cerca de pH {ph_neutro_T:.1f}** (punto de equivalencia): un exceso mínimo de reactivo "
                f"dispara el pH fuera de norma."
            )

        # GRÁFICA 2: MATPLOTLIB (COMPARACIÓN DE EQUILIBRIO IÓNICO ENTRADA VS SALIDA)
        with col_g2:
            st.subheader("⚖️ Cambio de Concentración Iónica (Matplotlib)")
            fig_mat, ax = plt.subplots(figsize=(5.5, 4.1))
            etiquetas = ['[H⁺] Entrada', '[H⁺] Salida', '[OH⁻] Entrada', '[OH⁻] Salida']
            valores = [h_in, h_out, oh_in, oh_out]
            colores = ['#d9534f', '#f0ad4e', '#0275d8', '#5bc0de']

            barras = ax.bar(etiquetas, valores, color=colores)
            ax.set_yscale('log')
            ax.set_ylim(1e-15, 10)
            ax.set_ylabel('Concentración Molar (mol/L) [Escala Log]')
            ax.set_title(f'Desplazamiento Iónico a {temp_efluente} °C (Kw = {kw_actual:.2e})')
            ax.grid(True, which="both", ls="--", alpha=0.5)
            plt.xticks(rotation=15)
            st.pyplot(fig_mat)
            plt.close(fig_mat)

            # Explicación dinámica de lo que cambia en la Gráfica 2
            st.info(
                f"**¿Qué muestra y qué cambia en esta gráfica?**\n"
                f"- Compara en escala logarítmica la molaridad de **$[H^+]$** y **$[OH^-]$** antes y después del reactor.\n"
                f"- Para pasar de **pH {ph_entrada}** a **pH {ph_salida}**, la concentración iónica se modifica en un factor de "
                f"**{factor_cambio:,.1f} veces** ($[H^+]$ pasa de `{h_in:.2e}` a `{h_out:.2e}` mol/L).\n"
                f"- Al modificar la **temperatura ({temp_efluente} °C)**, el producto $[H^+][OH^-] = K_w$ cambia ligeramente."
            )

    with sub_tabla:
        st.subheader("📋 Simulación de Turno Operativo (24 Horas)")
        st.caption("Simulación estocástica (NumPy + Pandas) considerando fluctuaciones normales de caudal y pH en una planta real:")

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
            file_name="bitacora_neutralizacion_PTAR_Chihuahua.csv",
            mime="text/csv"
        )

# ---------------------------------------------------------
# SECCIÓN 6: BIBLIOGRAFÍA Y REFERENCIAS
# ---------------------------------------------------------
with tab6:
    st.header("6. Bibliografía y Referencias Técnicas")
    st.write("Fuentes académicas, normativas y técnicas que respaldan el desarrollo químico, matemático e industrial de ChemPH:")

    st.subheader("📘 Fundamentos de Química Inorgánica y Equilibrio Ácido-Base")
    st.markdown(
        "1. **Housecroft, C. E., & Sharpe, A. G.** (2018). *Química Inorgánica* (4.ª ed.). Pearson Educación. (Capítulo de ácidos, bases y equilibrios en disolución acuosa).\n"
        "2. **Chang, R., & Goldsby, K. A.** (2017). *Química* (12.ª ed.). McGraw-Hill Education. (Equilibrios ácido-base, autoionización del agua $K_w$ y curvas de valoración).\n"
        "3. **Skoog, D. A., West, D. M., Holler, F. J., & Crouch, S. R.** (2015). *Fundamentos de Química Analítica* (9.ª ed.). Cengage Learning."
    )

    st.subheader("⚙️ Ingeniería Química y Balances de Materia")
    st.markdown(
        "4. **Felder, R. M., & Rousseau, R. W.** (2016). *Principios Elementales de los Procesos Químicos* (4.ª ed.). Limusa Wiley. (Balances de materia en sistemas reactivos y flujos continuos).\n"
        "5. **Himmelblau, D. M., & Riggs, J. B.** (2012). *Principios Básicos y Cálculos en Ingeniería Química* (8.ª ed.). Pearson."
    )

    st.subheader("💧 Tratamiento de Aguas Residuales y Normatividad Mexicana")
    st.markdown(
        "6. **Metcalf & Eddy, Inc.** (2014). *Wastewater Engineering: Treatment and Resource Recovery* (5th ed.). McGraw-Hill. (Procesos químicos unitarios: neutralización de efluentes industriales).\n"
        "7. **SEMARNAT.** (2022). *Norma Oficial Mexicana NOM-001-SEMARNAT-2021, Que establece los límites permisibles de contaminantes en las descargas de aguas residuales en cuerpos receptores propiedad de la nación*. Diario Oficial de la Federación.\n"
        "8. **SEMARNAT.** (1998). *Norma Oficial Mexicana NOM-002-SEMARNAT-1996, Que establece los límites máximos permisibles de contaminantes en las descargas de aguas residuales a los sistemas de alcantarillado urbano o municipal*. Diario Oficial de la Federación."
    )

    st.subheader("🏭 Contexto Industrial y Hídrico en Chihuahua")
    st.markdown(
        "9. **Junta Municipal de Agua y Saneamiento de Chihuahua (JMAS).** *Lineamientos Técnicos para el Control de Descargas Industriales y Operación de Plantas Tratadoras de Aguas Residuales (PTAR Norte y PTAR Sur)*.\n"
        "10. **Secretaría de Innovación y Desarrollo Económico (SIDE) – Gobierno del Estado de Chihuahua.** *Diagnóstico del Sector Industrial, Manufacturero y Maquilador en el Municipio de Chihuahua*."
    )
