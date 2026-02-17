from openai import OpenAI
from config import OPENAI_API_KEY

# ============================================================
# analysis.py — Análisis técnico de Ethereum con OpenAI
# ============================================================

# --- Validar API Key ---
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

client = OpenAI(api_key=OPENAI_API_KEY)


def analyze_trend(data_string):
    """
    Envía los datos formateados a OpenAI y devuelve un análisis
    técnico completo de Ethereum para Telegram.

    Args:
        data_string: Tabla markdown con los indicadores de los últimos días.

    Returns:
        str: Texto del análisis generado por el LLM.
    """
    # 1. Construir el prompt con los datos
    prompt = f"""
    Eres un Agente de Trading Pro de Ethereum. Analiza el siguiente set de datos técnicos:
    
    {data_string}
    
    TAREA:
    1. 💎 <b>ESTADO ACTUAL</b>: Bloque de código con Precio, RSI, MACD_Hist, ATR y EMAs (20, 50, 200).
    2. 📈 <b>ANÁLISIS TÉCNICO</b>: 
       - Comenta la posición del precio respecto a las Bandas de Bollinger (BB_High, BB_Low) y las EMAs.
       - Analiza la fuerza de la tendencia usando el MACD, el RSI y la relación entre las EMAs.
    3. 🚨 <b>VEREDICTO</b>: SHORT, WAIT o LONG con justificación técnica.
    4. 🛡️ <b>GESTIÓN DE RIESGO</b>: 
       - Sugiere un Stop Loss basado en el ATR (ej: Precio + 2*ATR para Shorts).
       - Sugiere un Take Profit usando el BB_Mid o BB_Low.
    
    Usa Emojis y etiquetas HTML permitidas por Telegram: <b>negrita</b>, <i>cursiva</i>, <code>code</code>, <pre>bloque de código</pre>.
    NO uses Markdown (nada de ** o ```).
    """

    # 2. Enviar al modelo
    try:
        print("Sending request to OpenAI...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Eres un analista financiero senior. Tu estilo es visual, técnico y directo."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        print("Received response from OpenAI.")
        return response.choices[0].message.content

    except Exception as e:
        print(f"Error in analyze_trend: {e}")
        return f"❌ Error al procesar datos con OpenAI: {e}"
