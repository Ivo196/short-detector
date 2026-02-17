from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def analyze_trend(data_string):
    """
    Analiza datos técnicos de Ethereum y genera un reporte HTML detallado.
    """
    prompt = f"""
    Eres un Agente de Trading Pro de Ethereum. Tu objetivo es realizar un análisis técnico profundo basado en los siguientes datos de los últimos 7 días:

    TAREA:
    Genera un reporte técnico en HTML para Telegram. Debes NOMBRAR cada indicador y EXPLICAR el porqué de tu interpretación basándote en los valores actuales.
    
    PASO 1: Usa la herramienta de búsqueda web para encontrar las 5 noticias más relevantes de Ethereum de HOY.
    PASO 2: Analiza estos datos técnicos de los últimos 7 días:

    {data_string}

    ESTRUCTURA DEL REPORTE:

    1. 💎 <b>ESTADO ACTUAL (Métricas Clave)</b>
    Usa una etiqueta <pre> para mostrar: Precio, RSI, MACD_Line, MACD_Hist, ATR y ADX. 
    (Alinea los valores para que parezca una terminal financiera).

    2. 📉 <b>ANÁLISIS TÉCNICO DETALLADO</b>
    • <b>Tendencia y Fuerza (ADX + EMAs):</b> Analiza la relación entre EMA_20, 50 y 200. Usa el ADX para decir si la tendencia tiene fuerza o es lateral.
    • <b>Momentum (RSI + MACD):</b> Explica el valor del RSI. ¿Está subiendo desde sobreventa o bajando desde sobrecompra? Usa el MACD_Hist para confirmar si el momentum está acelerando o frenando.
    • <b>Volatilidad (Bollinger + ATR):</b> Comenta la posición del precio respecto a BB_High, BB_Mid y BB_Low. Explica qué nos dice el ATR sobre la volatilidad actual del mercado.

    3. 🚨 <b>VEREDICTO: [LONG 🟢 | SHORT 🔴 | WAIT 🟡]</b>
    Justifica tu decisión uniendo al menos tres indicadores de los anteriores. Por qué este es el momento (o por qué no lo es).

    4. 📰 <b>NOTICIAS DEL DÍA</b>: No me des las noticas, solo un mini resumen de que se habla en general.


    REGLAS DE FORMATO:
    - NO uses Markdown.
    - Usa etiquetas HTML: <b>, <i>, <code>, <pre>.
    - Sé técnico, directo y usa emojis financieros.
    - Longitud total: máximo 2200 caracteres.
    - Máximo 6 bullets en todo el reporte.
    - NOTICIAS: 2 bullets de 1 línea cada uno. Sin URLs, sin nombres de medios, sin “Fuentes”.
    - No incluyas secciones adicionales.
    """

    try:
        response = client.responses.create(
            model="gpt-5-nano-2025-08-07",
            reasoning={"effort": "low"},  # evita “minimal reasoning”
            tools=[{"type": "web_search"}],
            tool_choice="required",          
            include=["web_search_call.action.sources"],
            input=[
                {"role": "system", "content": "Eres un analista financiero senior."},
                {"role": "user", "content": prompt},
            ],
            max_output_tokens=550
        )
        return response.output_text
    except Exception as e:
        return f"❌ <b>Error técnico:</b> <code>{e}</code>"