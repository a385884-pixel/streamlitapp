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
    caudal_L_h = caudal_m3h * 1000.0

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
st.sidebar.title("⤷ El pH en la Ing. Química")
st.sidebar.markdown("### ⋆ Objetivo de la Aplicación")
st.sidebar.info(
    """Mostrar cómo los conceptos teóricos del **pH** aprendidos en el laboratorio universitario 
    se transforman en herramientas de **Ingeniería Química** para controlar y neutralizar 
    descargas de aguas residuales en la industria de Chihuahua."""
)

st.sidebar.markdown("### 📑 Contenido por Pestaña")
st.sidebar.markdown(
    """
    **❶ Introducción y Contexto Industrial:**  
    Qué es el pH, qué es la Ingeniería Química, su relación industrial, normas oficiales y contexto en Chihuahua.

    **❷ Principios de la Simulación:**  
    Cómo funciona químicamente la neutralización y en qué principios fisicoquímicos se basa el simulador.

    **❸ Fórmulas y Funcionalidad:**  
    Explicación detallada de cada ecuación, gráficas conceptuales de comportamiento y bibliografía.

    **❹ Ejemplo de un Simulador Industrial:**  
    Ejemplo industrial práctico, panel interactivo en tiempo real, interpretación de la curva de valoración y bitácora de 24 h.
    """
)
st.sidebar.markdown("---")
st.sidebar.caption("Desarrollado en Python (Streamlit, NumPy, Pandas, Matplotlib y Plotly).")

# =========================================================
# 5. ENCABEZADO Y ESTRUCTURA DE 4 PESTAÑAS
# =========================================================
st.title(" El pH en la Ingeniería Química: Del Laboratorio al Control Industrial")
st.caption("Simulador de Neutralización de Efluentes y Escalamiento de Procesos (PTAR Chihuahua)")

tab1, tab2, tab3, tab4 = st.tabs([
    "❶ Introducción y Contexto Industrial",
    "❷ Principios de la Simulación",
    "❸ Fórmulas y Para que se emplean",
    "❹ Ejemplo de un Simulador Industrial"
])

# ---------------------------------------------------------
# PESTAÑA 1: INTRODUCCIÓN, NORMAS E INDUSTRIA EN CHIHUAHUA
# ---------------------------------------------------------
with tab1:
    st.header("1. Introducción: El pH, la Ingeniería Química y la Industria")

    st.info(
        """**Propósito de esta aplicación:** Demostrar cómo lo que se ensaña en las materias escolares 
        (como Química Inorgánica y balances básicos ) puede escalar y transformarse en ingeniería real 
        como una herramienta para resolver problemas ambientales y operativos de control de pH en plantas industriales."""
    )

    col_i1, col_i2 = st.columns(2)
    with col_i1:
        st.subheader("¿Qué es el pH?")
        st.write(
            """El **pH** (*potencial de hidrógeno*) es una medida que indica el grado de acidez o alcalinidad 
            de una disolución acuosa en una escala que va de **0 a 14** (siendo $7.0$ el punto neutro a $25\\,^\\circ\\text{C}$). 
            Químicamente mide la concentración de iones hidrógeno ($H^+$) presentes en el agua."""
        )
        st.write(
            """Al tratarse de una **escala logarítmica**, cada unidad de cambio representa un factor de **10 veces** 
            en la concentración iónica: un agua residual con $\\text{pH } 3$ es **10,000 veces más ácida** que una con $\\text{pH } 7$."""
        )

    with col_i2:
        st.subheader("¿Qué es la Ingeniería Química y cómo se relaciona con el pH?")
        st.write(
            """La **Ingeniería Química** es la disciplina que diseña, opera y controla procesos industriales 
            donde la materia sufre cambios físicos o químicos, llevando reacciones de laboratorio a escalas de 
            **miles de litros por hora** con seguridad y rentabilidad."""
        )
        st.write(
            """Su relación con el **pH** es directa: en la industria, un pH fuera de control corroe tuberías metálicas, 
            destruye los microorganismos de las plantas tratadoras, impide la precipitación de metales pesados y 
            genera multas ambientales por descargas contaminantes."""
        )

    st.markdown("---")
    st.subheader("Normatividad Oficial Mexicana Aplicable")
    col_n1, col_n2 = st.columns(2)
    with col_n1:
        st.warning(
            """**NOM-002-SEMARNAT-1996 (Descargas al Alcantarillado):**

            Establece los límites máximos permisibles de contaminantes en las descargas de aguas residuales 
            a los sistemas de alcantarillado urbano o municipal. Exige mantener el **pH entre 5.5 y 10.0 unidades** 
            para evitar la corrosión de la red pública."""
        )
    with col_n2:
        st.success(
            """**NOM-001-SEMARNAT-2021 (Cuerpos Receptores Nacionales):**

            Regula las descargas de aguas residuales en ríos, arroyos, embalses o suelo. 
            Exige un control más estricto, manteniendo el **pH dentro del rango de 6.0 a 9.0 unidades** 
            para proteger la vida acuática y el entorno."""
        )

    st.markdown("---")
    st.subheader("Conexión con la Industria y Gestión Hídrica en Chihuahua")
    st.write(
        """En una ciudad con clima semidesértico y fuerte vocación manufacturera como **Chihuahua**, el tratamiento 
        y control de pH en el agua industrial es indispensable para permitir su saneamiento y reúso:"""
    )
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown(
            """- **JMAS Chihuahua (Junta Municipal de Agua y Saneamiento):** Opera las plantas **PTAR Norte** y **PTAR Sur**, 
            supervisando el cumplimiento normativo de las descargas industriales al alcantarillado y distribuyendo agua tratada (línea morada) 
            a parques industriales y áreas verdes.
            - **Sector Metalmecánico y Aeroespacial (Complejo Industrial Chihuahua, El Saucito, Supra):** Plantas de maquinado, 
            anodizado y recubrimientos metálicos generan efluentes ácidos ($\\text{pH } 2.0 - 4.0$) por decapado químico que requieren 
            dosificación de bases antes de verterse."""
        )
    with col_c2:
        st.markdown(
            """- **Industria Alimentaria y Láctea (Grupo Bafar, Zaragoza / Alpura):** Sus ciclos de limpieza y desinfección 
            CIP (*Clean-In-Place*) emplean sosa cáustica, generando aguas residuales alcalinas ($\\text{pH } 10.5 - 12.5$) que deben 
            neutralizarse con ácidos.
            - **Del Laboratorio a la Planta:** Mientras en la escuela titulamos $50\\text{ mL}$ en un matraz, en estas empresas 
            de Chihuahua se neutralizan flujos continuos de $20$ a $150\\text{ m}^3/\\text{h}$ mediante tanques agitados y bombas automatizadas."""
        )

# ---------------------------------------------------------
# PESTAÑA 2: PRINCIPIOS DE LA SIMULACIÓN
# ---------------------------------------------------------
with tab2:
    st.header("2. Principios de la Simulación")
    st.write(
        """El simulador no realiza una simple regla de tres lineal; modela el comportamiento fisicoquímico real 
        de un reactor continuo de neutralización aplicando cuatro principios de la Ingeniería Química:"""
    )

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.subheader("1. Reacción Química de Neutralización")
        st.write(
            """Cuando un efluente ácido (exceso de $H^+$) reacciona con una base (aporte de $OH^-$), o viceversa, 
            ambos iones se combinan formando agua líquida y desplazando el pH hacia la neutralidad:"""
        )
        st.latex(r"H^+_{(ac)} + OH^-_{(ac)} \longrightarrow H_2O_{(l)} \quad (\Delta H^\circ = -57.3\text{ kJ/mol})")
        st.write(
            """Como esta reacción libera calor (es **exotérmica**), cuando los pH de entrada son extremos ($pH < 2.5$ o $pH > 11.5$), 
            el simulador emite una alerta recomendando neutralizar en **dos etapas** para proteger los equipos."""
        )

        st.subheader("2. Efecto de la Temperatura en el Equilibrio ($K_w$)")
        st.write(
            """En el laboratorio solemos asumir que el pH neutro siempre es $7.0$, pero eso solo ocurre a $25\\,^\\circ\\text{C}$. 
            En procesos industriales el agua residual puede salir fría ($10\\,^\\circ\\text{C}$) o caliente ($45\\,^\\circ\\text{C}$), 
            modificando la constante de autoionización del agua ($K_w$) y desplazando el pH neutro real."""
        )

    with col_p2:
        st.subheader("3. Curva Sigmoidal de Valoración")
        st.write(
            """Al agregar reactivo neutralizante, el pH no cambia de manera uniforme: al inicio varía lentamente, 
            pero al acercarse al **punto de equivalencia** (cerca de $pH = 7$) sufre un **salto vertical brusco**. 
            El simulador resuelve el equilibrio iónico completo en 140 puntos para dibujar esa curva real y mostrar 
            por qué se requiere precisión en la dosificación."""
        )

        st.subheader("4. Selección Estequiométrica del Reactivo")
        st.write(
            """El sistema detecta automáticamente si el agua es ácida o básica y habilita únicamente los reactivos 
            compatibles, tomando en cuenta su **peso molecular ($PM$)** y su **valencia equivalente ($\\nu_{\\text{eq}}$)**:"""
        )
        st.markdown(
            """- **Reactivos monopróticos ($1\\text{ eq/mol}$):** $NaOH$ y $HCl$.
            - **Reactivos dipróticos ($2\\text{ eq/mol}$):** $Ca(OH)_2$ y $H_2SO_4$ (aportan el doble de iones por cada mol)."""
        )

    st.markdown("---")
    st.subheader("¿Cómo procesa los datos el algoritmo del simulador?")
    c_flujo1, c_flujo2, c_flujo3, c_flujo4 = st.columns(4)
    with c_flujo1:
        st.info("""**Paso 1: Entradas**\n\nRecibe el caudal ($\\text{m}^3/\\text{h}$), el $pH_{\\text{entrada}}$, el $pH_{\\text{norma}}$ y la temperatura ($^\\circ\\text{C}$).""")
    with c_flujo2:
        st.info("""**Paso 2: Diagnóstico**\n\nEvalúa si el agua es ácida o básica, calcula $K_w(T)$ y filtra los reactivos neutralizantes.""")
    with c_flujo3:
        st.info("""**Paso 3: Balance Másico**\n\nCalcula los equivalentes por hora necesarios y los convierte a $\\text{kg/h}$ y $\\text{kg/día}$ de reactivo.""")
    with c_flujo4:
        st.info("""**Paso 4: Simulación 24 h**\n\nGenera la curva sigmoidal de valoración y simula variaciones reales de planta en un turno.""")

# ---------------------------------------------------------
# PESTAÑA 3: FÓRMULAS, GRÁFICAS CONCEPTUALES Y BIBLIOGRAFÍA
# ---------------------------------------------------------
with tab3:
    st.header("3. Fórmulas Utilizadas: Qué Calculan, Gráficas y Para Qué Sirven")
    st.write(
        """A continuación se explican las ecuaciones programadas en el sistema, acompañadas de gráficas 
        que ilustran el comportamiento matemático y físico de cada etapa del cálculo:"""
    )

    # BLOQUE A: ECUACIONES DE EQUILIBRIO IÓNICO + GRÁFICA LOGARÍTMICA
    st.subheader("A. Ecuaciones de Equilibrio Ácido-Base (Escala de Laboratorio)")
    col_eq_txt, col_eq_graf = st.columns([1.2, 1])

    with col_eq_txt:
        st.markdown("**1. Concentración Molar de Iones Hidrógeno ($[H^+]$):**")
        st.latex(r"[H^+] = 10^{-\text{pH}}")
        st.markdown(
            """- **¿Qué calcula?** La concentración real de iones $H^+$ activos en $\\text{mol/L}$.
            - **¿Para qué sirve?** Convierte la lectura logarítmica del sensor de pH en una cantidad química medible."""
        )

        st.markdown("**2. Producto Iónico del Agua ($K_w$) y Concentración de $[OH^-]$:**")
        st.latex(r"\text{p}K_w = 14.0 - 0.033(T - 25) \quad \Longrightarrow \quad [OH^-] = \frac{10^{-\text{p}K_w}}{[H^+]}")
        st.markdown(
            """- **¿Qué calcula?** Corrige la constante del agua según la temperatura $T$ ($^\\circ\\text{C}$) y obtiene la molaridad de iones hidroxilo $[OH^-]$.
            - **¿Para qué sirve?** Permite cuantificar la alcalinidad en aguas básicas y determinar el pH neutro exacto ($\\text{p}K_w / 2$) cuando el agua sale caliente."""
        )

    with col_eq_graf:
        ph_eje = np.linspace(0, 14, 200)
        h_eje = 10**(-ph_eje)
        oh_eje = 10**(-(14.0 - ph_eje))

        fig_teoria1, ax1 = plt.subplots(figsize=(5.2, 3.8))
        ax1.plot(ph_eje, h_eje, label='[H⁺] (Acidez)', color='#d9534f', linewidth=2.5)
        ax1.plot(ph_eje, oh_eje, label='[OH⁻] (Alcalinidad)', color='#0275d8', linewidth=2.5)
        ax1.axvline(7.0, color='green', linestyle='--', alpha=0.8, label='Punto Neutro (pH 7)')
        ax1.set_yscale('log')
        ax1.set_ylim(1e-15, 10)
        ax1.set_xlim(0, 14)
        ax1.set_xlabel('Escala de pH')
        ax1.set_ylabel('Concentración Molar (mol/L) [Escala Log]')
        ax1.set_title('Comportamiento Exponencial de [H⁺] y [OH⁻]')
        ax1.grid(True, which='both', linestyle='--', alpha=0.4)
        ax1.legend(loc='center right', fontsize=8.5)
        plt.tight_layout()
        st.pyplot(fig_teoria1)

        buf_t1 = io.BytesIO()
        fig_teoria1.savefig(buf_t1, format="png", dpi=200)
        buf_t1.seek(0)
        plt.close(fig_teoria1)

        st.info(
            """**¿Para qué sirve esta gráfica?** Muestra por qué la neutralización no es lineal: al pasar de pH 2 a pH 3 
            se elimina el **90 %** de la carga ácida, mientras que entre pH 6 y pH 8 las concentraciones son tan bajas ($10^{-7}\\text{ mol/L}$) 
            que cualquier gota extra cambia bruscamente el pH."""
        )
        st.download_button(
            label="📥 Descargar Gráfica de Equilibrio Iónico (PNG)",
            data=buf_t1,
            file_name="grafica_teorica_equilibrio_ph.png",
            mime="image/png"
        )

    st.markdown("---")

    # BLOQUE B: ECUACIONES DE ESCALAMIENTO INDUSTRIAL + GRÁFICA DE CAUDAL VS DOSIS
    st.subheader("B. Ecuaciones de Escalamiento Industrial (Flujos Continuos)")
    col_ind_txt, col_ind_graf = st.columns([1.2, 1])

    with col_ind_txt:
        st.markdown("**3. Escalamiento de Caudal Volumétrico ($Q_{\\text{L/h}}$):**")
        st.latex(r"Q_{\text{L/h}} = \dot{V}_{\text{m}^3/\text{h}} \times 1000\,\frac{\text{L}}{\text{m}^3}")
        st.markdown(
            """- **¿Qué calcula?** Convierte el flujo de tubería ($\\text{m}^3/\\text{h}$) a litros por hora ($\\text{L/h}$).
            - **¿Para qué sirve?** Homologa el volumen industrial con las unidades químicas de molaridad ($\\text{mol/L}$)."""
        )

        st.markdown("**4. Flujo de Equivalentes Químicos ($\\dot{n}_{\\text{eq}}$):**")
        st.latex(r"\dot{n}_{\text{eq}} = \left| C_{\text{net, entrada}} - C_{\text{net, objetivo}} \right| \times Q_{\text{L/h}}")
        st.markdown(
            """- **¿Qué calcula?** Los equivalentes por hora ($\\text{eq/h}$) de ácido o base que deben neutralizarse.
            - **¿Para qué sirve?** Determina la demanda química total del flujo continuo."""
        )

        st.markdown("**5. Dosificación Másica de Reactivo ($\\dot{m}_{\\text{reactivo}}$):**")
        st.latex(r"\dot{m}_{\text{reactivo}} \left[\frac{\text{kg}}{\text{h}}\right] = \frac{\dot{n}_{\text{eq}}}{\nu_{\text{eq}}} \times \frac{PM}{1000}")
        st.markdown(
            """- **¿Qué calcula?** Los **kilogramos por hora ($\\text{kg/h}$)** de reactivo comercial necesarios.
            - **¿Para qué sirve?** Permite dimensionar bombas dosificadoras y comparar el ahorro entre reactivos monopróticos ($\\nu=1$) y dipróticos ($\\nu=2$)."""
        )

    with col_ind_graf:
        caudales_eje = np.linspace(5, 150, 50)
        dosis_naoh_eje = [calcular_dosificacion(q, 3.0, 7.0, "Hidróxido de Sodio (NaOH)", 25.0) for q in caudales_eje]
        dosis_caoh_eje = [calcular_dosificacion(q, 3.0, 7.0, "Hidróxido de Calcio (Ca(OH)2)", 25.0) for q in caudales_eje]

        fig_teoria2, ax2 = plt.subplots(figsize=(5.2, 3.8))
        ax2.plot(caudales_eje, dosis_naoh_eje, label='NaOH (PM=39.99, ν=1)', color='#d9534f', linewidth=2.5)
        ax2.plot(caudales_eje, dosis_caoh_eje, label='Ca(OH)₂ (PM=74.09, ν=2)', color='#28a745', linewidth=2.5)
        ax2.set_xlabel('Caudal del Efluente Industrial (m³/h)')
        ax2.set_ylabel('Consumo de Reactivo (kg/h)')
        ax2.set_title('Escalamiento Industrial (Ejemplo: pH 3.0 → 7.0)')
        ax2.grid(True, linestyle='--', alpha=0.4)
        ax2.legend(loc='upper left', fontsize=8.5)
        plt.tight_layout()
        st.pyplot(fig_teoria2)

        buf_t2 = io.BytesIO()
        fig_teoria2.savefig(buf_t2, format="png", dpi=200)
        buf_t2.seek(0)
        plt.close(fig_teoria2)

        st.info(
            """**¿Para qué sirve esta gráfica?** Demuestra cómo los cálculos escolares escalan proporcionalmente con el caudal 
            de la planta ($\\text{m}^3/\\text{h}$) y evidencia que el **Hidróxido de Calcio ($Ca(OH)_2$)** requiere menor masa que el $NaOH$ 
            al aportar 2 moles de $OH^-$ por cada mol disuelto."""
        )
        st.download_button(
            label="📥 Descargar Gráfica de Escalamiento (PNG)",
            data=buf_t2,
            file_name="grafica_teorica_escalamiento_caudal.png",
            mime="image/png"
        )

    st.markdown("---")
    st.subheader("📚 Bibliografía y Fuentes de Consulta")
    st.markdown(
        """
        1. **Chang, R., & Goldsby, K. A.** (2017). *Química* (12.ª ed.). McGraw-Hill Education. (Equilibrios ácido-base, autoionización del agua y curvas de valoración).
        2. **Housecroft, C. E., & Sharpe, A. G.** (2018). *Química Inorgánica* (4.ª ed.). Pearson Educación. (Química de disoluciones acuosas y fuerza de ácidos y bases).
        3. **Felder, R. M., & Rousseau, R. W.** (2016). *Principios Elementales de los Procesos Químicos* (4.ª ed.). Limusa Wiley. (Balances de materia en sistemas continuos).
        4. **Metcalf & Eddy, Inc.** (2014). *Wastewater Engineering: Treatment and Resource Recovery* (5th ed.). McGraw-Hill. (Neutralización química de aguas residuales industriales).
        5. **SEMARNAT.** (1998). *Norma Oficial Mexicana NOM-002-SEMARNAT-1996* (Límites máximos permisibles en descargas al alcantarillado urbano o municipal). Diario Oficial de la Federación.
        6. **SEMARNAT.** (2022). *Norma Oficial Mexicana NOM-001-SEMARNAT-2021* (Límites permisibles en descargas de aguas residuales en cuerpos receptores). Diario Oficial de la Federación.
        7. **Junta Municipal de Agua y Saneamiento de Chihuahua (JMAS).** *Lineamientos Técnicos para Control de Descargas Industriales y Operación de PTAR Norte y PTAR Sur, Chihuahua, Chih.*
        """
    )

# ---------------------------------------------------------
# PESTAÑA 4: SIMULADOR INDUSTRIAL Y EJEMPLO PRÁCTICO
# ---------------------------------------------------------
with tab4:
    st.header("4. Simulador Industrial de Neutralización")

    # EJEMPLO PRÁCTICO INDUSTRIAL RESUELTO
    with st.expander("📌 Ejemplo Práctico Industrial (Planta Metalmecánica en Chihuahua) — Haz clic para ver el cálculo", expanded=True):
        st.write(
            """**Planteamiento:** Una planta de recubrimientos metálicos en el **Complejo Industrial Chihuahua** genera un efluente 
            continuo de **$40\\text{ m}^3/\\text{h}$** con **$pH_{\\text{entrada}} = 3.0$** a **$25\\,^\\circ\\text{C}$** proveniente de baños de decapado ácido. 
            Se requiere neutralizarlo hasta **$pH_{\\text{objetivo}} = 7.0$** para cumplir la norma ambiental."""
        )
        dosis_ej_naoh = calcular_dosificacion(40.0, 3.0, 7.0, "Hidróxido de Sodio (NaOH)", 25.0)
        dosis_ej_caoh = calcular_dosificacion(40.0, 3.0, 7.0, "Hidróxido de Calcio (Ca(OH)2)", 25.0)
        ahorro_diario = (dosis_ej_naoh - dosis_ej_caoh) * 24.0

        st.markdown("**Aplicación paso a paso de las fórmulas:**")
        st.markdown(
            """1. **Escalamiento de caudal:** $Q = 40\\text{ m}^3/\\text{h} \\times 1000 = 40,000\\text{ L/h}$.
            2. **Concentración inicial de protones:** $[H^+] = 10^{-3.0} = 0.001\\text{ mol/L}$ (en $pH = 7.0$, $[H^+] = 10^{-7}\\text{ mol/L}$).
            3. **Flujo de equivalentes a neutralizar:** $\\dot{n}_{\\text{eq}} = 0.001\\text{ eq/L} \\times 40,000\\text{ L/h} = 40.0\\text{ eq/h}$.
            4. **Cálculo de dosificación másica y decisión de ingeniería:**"""
        )
        st.write(
            f"""- Con **Hidróxido de Sodio ($NaOH$, $PM=39.99$, $\\nu=1$):** se requieren **{dosis_ej_naoh:.2f} kg/h** (**{dosis_ej_naoh*24:.1f} kg/día**).
            - Con **Hidróxido de Calcio ($Ca(OH)_2$, $PM=74.09$, $\\nu=2$):** se requieren **{dosis_ej_caoh:.2f} kg/h** (**{dosis_ej_caoh*24:.1f} kg/día**), 
            logrando un ahorro de **{ahorro_diario:.1f} kg/día** de insumo químico."""
        )

    st.markdown("---")
    st.subheader("🎛️ Panel de Control de Operación")
    st.caption("Modifica los parámetros de la planta para simular la dosificación y analizar la curva de valoración:")

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
            st.error(f"""**{tipo_efluente}** | ⚠️ **pH Extremo:** Se recomienda neutralización en 2 etapas en serie para evitar calentamiento excesivo y corrosión.""")
        elif temp_efluente >= 35.0:
            st.warning(f"""**{tipo_efluente}** | 🌡️ **Temperatura Alta ({temp_efluente} °C):** El pH neutro real se desplaza a **{ph_neutro_T:.2f}**.""")
        else:
            st.success(f"""**{tipo_efluente}** | ✅ **Operación Estable:** Tiempo de residencia hidráulico recomendado de 15 a 20 min con agitación continua.""")

    # CÁLCULOS EN TIEMPO REAL
    dosis_kgh = calcular_dosificacion(caudal, ph_entrada, ph_salida, reactivo_sel, temp_efluente)
    factor_cambio = 10**abs(ph_salida - ph_entrada)

    # MÉTRICAS CLAVE
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Caudal Operativo", f"{caudal} m³/h", f"{caudal*1000:,.0f} L/h")
    m2.metric("Cambio de pH", f"{ph_entrada} → {ph_salida}", f"ΔpH = {ph_salida - ph_entrada:+.1f}")
    m3.metric("Reactivo Requerido", f"{dosis_kgh:.2f} kg/h", f"{dosis_kgh*24:.1f} kg/día")
    m4.metric("pH Neutro a T (°C)", f"{ph_neutro_T:.2f}", f"Kw = {kw_actual:.2e}")

    st.markdown("---")

    # GRÁFICA PRINCIPAL DE SIMULACIÓN (LIMPIA Y A ANCHO COMPLETO)
    st.subheader("📈 Curva Dinámica de Valoración Industrial (Plotly)")
    dosis_eje, ph_curva, dosis_req = generar_curva_titulacion(
        caudal, ph_entrada, ph_salida, reactivo_sel, temp_efluente
    )

    fig_plotly = go.Figure()

    # Franja verde de cumplimiento normativo NOM-001 (pH 6.0 - 9.0)
    fig_plotly.add_hrect(
        y0=6.0, y1=9.0,
        fillcolor="rgba(40, 167, 69, 0.12)", line_width=0,
        annotation_text="Zona Permitida NOM-001 (pH 6.0 - 9.0)",
        annotation_position="top right"
    )

    fig_plotly.add_trace(go.Scatter(
        x=dosis_eje, y=ph_curva, mode='lines',
        name='Trayectoria de pH en Reactor',
        line=dict(color='#0275d8', width=3.5)
    ))

    # Punto exacto de operación
    fig_plotly.add_trace(go.Scatter(
        x=[dosis_req], y=[ph_salida], mode='markers',
        name='Punto de Operación Objetivo',
        marker=dict(color='red', size=11, symbol='diamond')
    ))

    fig_plotly.add_hline(y=ph_salida, line_dash="dash", line_color="green", annotation_text=f"pH Objetivo ({ph_salida})")
    fig_plotly.add_vline(x=dosis_req, line_dash="dash", line_color="red", annotation_text=f"Dosis Exacta: {dosis_req:.2f} kg/h")

    fig_plotly.update_layout(
        xaxis_title=f"Flujo Másico Dosificado de {reactivo_sel} (kg/h)",
        yaxis_title="pH Resultante en el Efluente",
        yaxis=dict(range=[0, 14]),
        height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
    )
    st.plotly_chart(fig_plotly, use_container_width=True)
    st.caption("💡 Puedes descargar esta curva en formato imagen PNG haciendo clic en el ícono de cámara 📷 en la barra superior de la gráfica.")

    # INTERPRETACIÓN DETALLADA DE LA GRÁFICA
    st.subheader("📖 Interpretación de la Gráfica de Simulación")
    col_int1, col_int2, col_int3 = st.columns(3)

    with col_int1:
        st.info(
            f"""**1. ¿Qué representa esta gráfica?**

            Representa la **curva de titulación continua** del efluente de **{caudal} m³/h** a **{temp_efluente} °C**. 
            Muestra cómo evoluciona el pH dentro del tanque de mezcla desde su condición cruda (**pH {ph_entrada}**) 
            a medida que se incrementa el flujo de **{reactivo_sel}** (en kg/h)."""
        )

    with col_int2:
        st.success(
            f"""**2. ¿Qué nos indica el punto rojo?**

            El rombo rojo marca el **punto de consigna operativo**: indica que se deben inyectar exactamente 
            **{dosis_req:.2f} kg/h** ({dosis_req*24:.1f} kg/día) para lograr un cambio iónico de **{factor_cambio:,.1f} veces** 
            y situar la descarga dentro de la franja verde normativa (**pH {ph_salida}**)."""
        )

    with col_int3:
        st.warning(
            f"""**3. ¿Qué nos advierte la pendiente?**

            El tramo casi vertical alrededor de **pH {ph_neutro_T:.1f}** indica la **zona de máxima sensibilidad** (punto de equivalencia). 
            Si la bomba dosificadora sobrepasa los **{dosis_req:.2f} kg/h**, el pH saltará fuera de la franja verde, 
            exigiendo un control automático preciso."""
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
  

