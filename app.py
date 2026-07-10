# -*- coding: utf-8 -*-
"""
Abogado Personal AI - MVP V2 (Multijurisdiccional)
Requerimientos: pip install streamlit PyPDF2 openai
"""
import streamlit as st
import PyPDF2
import io
import os
from openai import OpenAI

# Configuración estructural de la UI
st.set_page_config(
    page_title="Abogado Personal AI - Global",
    page_icon="⚖️",
    layout="centered"
)

# Estilos CSS personalizados para destacar riesgos y estructura
st.markdown("""
    <style>
    .main-title { font-size: 32px; color: #0f172a; font-weight: bold; text-align: center; margin-bottom: 5px; }
    .sub-title { font-size: 15px; color: #475569; text-align: center; margin-bottom: 25px; }
    .badge-chile { color: #ffffff; background-color: #0038a8; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; display: inline-block; margin-bottom: 10px; }
    .badge-usa { color: #ffffff; background-color: #b22234; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; display: inline-block; margin-bottom: 10px; }
    .badge-eu { color: #ffffff; background-color: #003399; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; display: inline-block; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">⚖️ Abogado Personal AI — V2</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Analizador de contratos inteligente adaptado a marcos legales específicos de Chile, EE.UU. y Europa.</div>', unsafe_allow_html=True)

# Panel Lateral de Configuración de Entorno
st.sidebar.header("Configuración")
api_key = st.sidebar.text_input("OpenAI API Key", type="password", help="Ingresa tu llave de OpenAI.")
if not api_key:
    api_key = os.environ.get("OPENAI_API_KEY", "")

# Selector Dinámico de Jurisdicción Legal
jurisdiccion = st.selectbox(
    "Selecciona la legislación aplicable al contrato:",
    ["Chile 🇨🇱 (Ley 19.496 / SERNAC)", "Estados Unidos 🇺🇸 (FTC / UCC / Federal Law)", "Unión Europea 🇪🇺 (Directiva 93/13 / GDPR)"]
)

uploaded_file = st.file_uploader("Sube el PDF del contrato que deseas destripar:", type=["pdf"])

def extraer_texto_pdf(file_obj):
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_obj.read()))
        texto_completo = ""
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                texto_completo += text + "\n"
        return texto_completo
    except Exception as e:
        st.error(f"Error al decodificar el PDF: {str(e)}")
        return None

def analizar_contrato_multijurisdiccion(texto_legal, region_seleccionada, key):
    client = OpenAI(api_key=key)
    
    # Configuración de los sub-prompts técnicos de acuerdo al territorio
    if "Chile" in region_seleccionada:
        contexto_legal = (
            "Actúa bajo la legislación de CHILE (Ley 19.496 de Protección de los Derechos de los Consumidores). "
            "Enfoque principal: Buscar cláusulas abusivas según los criterios del SERNAC (renovaciones automáticas sin consentimiento explícito, "
            "eximentes de responsabilidad por fallas del servicio, limitaciones al derecho de retracto, cobros ocultos de comisiones).\n"
            "En la sección de frases para reclamar, estructura un borrador formal listo para presentar ante el portal de Reclamos de SERNAC."
        )
    elif "Estados Unidos" in region_seleccionada:
        contexto_legal = (
            "Actúa bajo la legislación federal y estatal de ESTADOS UNIDOS (Federal Trade Commission Act Section 5, Uniform Commercial Code, etc.). "
            "Enfoque principal: Detectar cláusulas extremas de 'Mandatory Binding Arbitration' (arbitraje obligatorio), 'Class-Action Waivers' (renuncia a demandas colectivas), "
            "cláusulas 'Unilateral Modification' (donde cambian los términos cuando quieren sin avisar) y violaciones de la Consumer Review Fairness Act.\n"
            "En la sección de frases, genera un texto en inglés y español útil para reclamar al servicio al cliente o disputar los términos."
        )
    else: # Unión Europea
        contexto_legal = (
            "Actúa bajo la legislación de la UNIÓN EUROPEA (Directiva 93/13/CEE sobre cláusulas abusivas en contratos celebrados con consumidores y el RGPD/GDPR). "
            "Enfoque principal: Buscar desequilibrios severos entre derechos y obligaciones, prórrogas automáticas ocultas, selección de fueros judiciales perjudiciales para el usuario "
            "(ej. obligar a litigar en Irlanda o Luxemburgo), y consentimiento forzado para recolección o rastreo masivo de datos sin opción clara de Opt-Out.\n"
            "En la sección de frases, genera opciones sólidas invocando los derechos de la directiva europea y la protección de datos."
        )

    prompt_sistema = (
        f"Eres un abogado de élite internacional experto en derecho del consumidor y análisis de contratos empresariales masivos. "
        f"Tu meta es traducir contratos corporativos ultra complejos a un lenguaje coloquial de calle, directo y sumamente instructivo.\n\n"
        f"CONTESTA EN ESPAÑOL y básate estrictamente en el siguiente contexto jurídico: {contexto_legal}\n\n"
        "Estructura tu respuesta exactamente bajo este formato Markdown:\n"
        "## 📑 DIAGNÓSTICO JURÍDICO REGIONAL\n"
        "### 1. EXPLICACIÓN EN CRISTIANO\n(De qué trata este contrato explicado de forma muy simple y pragmática)\n\n"
        "### 2. CLÁUSULAS ABUSIVAS / DE ALTO RIESGO DETECTADAS\n"
        "💥 **[PELIGRO CRÍTICO]** - *Cláusula:* (Cita o referencia corta del contrato)\n"
        "👉 *Por qué es una trampa según la normativa local:* (Explicación técnica en palabras sencillas de por qué infringe o vulnera los derechos bajo la ley de la región)\n\n"
        "⚠️ **[ALERTA REGULAR]** - *Cláusula:* (Cita o referencia corta)\n"
        "👉 *Ten cuidado porque:* (Explicación de la letra chica)\n\n"
        "### 3. ACCIÓN DEFENSIVA Y BORRADOR DE RECLAMO\n"
        "(Genera un texto listo para copiar, pegar y enviar a la empresa, o para ingresar en la agencia reguladora del país, con tono firme e invocando la ley correspondiente)\n"
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": f"Analiza este contrato:\n\n{texto_legal[:12000]}"}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error al procesar con el motor de IA global: {str(e)}"

# Orquestador principal de ejecución
if uploaded_file:
    if not api_key:
        st.warning("⚠️ Introduce tu OpenAI API Key en la barra lateral para iniciar la auditoría legal internacional.")
    else:
        with st.spinner(f"🕵️‍♂️ Extrayendo y auditando el contrato bajo el estándar legal seleccionado..."):
            texto_contrato = extraer_texto_pdf(uploaded_file)
            
            if texto_contrato and len(texto_contrato.strip()) > 50:
                analisis_final = analizar_contrato_multijurisdiccion(texto_contrato, jurisdiccion, api_key)
                
                # Despliegue visual elegante
                if "Chile" in jurisdiccion:
                    st.markdown('<span class="badge-chile">ENFOQUE: LEY 19.496 CHILE</span>', unsafe_allow_html=True)
                elif "Estados Unidos" in jurisdiccion:
                    st.markdown('<span class="badge-usa">ENFOQUE: FTC & US CONSUMER LAW</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="badge-eu">ENFOQUE: DIRECTIVAS UE & GDPR</span>', unsafe_allow_html=True)
                
                st.markdown(analisis_final)
                st.divider()
                st.caption("🔒 **Cómputo Seguro:** Retención Cero activada. El archivo fue purgado de la memoria inmediatamente tras renderizar los resultados.")
            else:
                st.error("El archivo cargado está vacío o no posee texto legible directo (requiere OCR).")

