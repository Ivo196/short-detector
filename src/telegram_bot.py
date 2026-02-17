import time
import requests
import html
import re

from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from data_download import download_raw_data
from indicators import update_indicators
from data_formatter import load_and_format_data
from analysis import analyze_trend

# ============================================================
# telegram_bot.py — Bot de Telegram para análisis de Ethereum
# ============================================================

MAX_LEN = 3800
_ALLOWED = {"b", "/b", "i", "/i", "code", "/code", "pre", "/pre"}

def sanitize_telegram_html(s: str) -> str:
    # Escapa TODO (esto convierte <script> en &lt;script&gt;)
    s = html.escape(s)

    # Re-habilita SOLO tags permitidos
    def unesc(m):
        tag = m.group(1).lower()
        return f"<{tag}>" if tag in _ALLOWED else m.group(0)

    s = re.sub(r"&lt;(/?b|/?i|/?code|/?pre)&gt;", unesc, s, flags=re.I)
    return s
def split_msg(text: str, max_len: int = MAX_LEN):
    parts = []
    while len(text) > max_len:
        cut = text.rfind("\n", 0, max_len)
        if cut == -1:
            cut = max_len
        parts.append(text[:cut])
        text = text[cut:].lstrip()
    if text:
        parts.append(text)
    return parts

def send_message(text, chat_id=None):
    target_chat_id = chat_id or TELEGRAM_CHAT_ID
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    safe = sanitize_telegram_html(str(text))
    chunks = split_msg(safe)

    for chunk in chunks:
        resp = requests.post(url, data={
            "chat_id": target_chat_id,
            "text": chunk,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        })

        if resp.status_code != 200:
            print(f"Error sending message: {resp.status_code} - {resp.text}")
            # fallback: texto plano (igual va en chunks)
            retry = requests.post(url, data={
                "chat_id": target_chat_id,
                "text": chunk,
                "disable_web_page_preview": True
            })
            if retry.status_code != 200:
                print(f"Retry failed: {retry.status_code} - {retry.text}")
            else:
                print("Retry success.")


def handle_update(texto_usuario, chat_id):
    """
    Procesa un comando del usuario y ejecuta la acción correspondiente.

    Args:
        texto_usuario: Texto del mensaje recibido (en minúsculas).
        chat_id: ID del chat del usuario.
    """
    if texto_usuario == "/analisis":
        # --- Comando: Análisis completo ---
        send_message("⏳ Actualizando datos y calculando indicadores...", chat_id)
        try:
            # 1. Descargar datos frescos
            print("Updating data...")
            df_raw = download_raw_data()

            # 2. Calcular indicadores
            update_indicators(df_raw)

            # 3. Formatear datos para el LLM
            send_message("📊 Calculando indicadores...", chat_id)
            print("Starting analysis flow...")
            data = load_and_format_data()

            # 4. Enviar al LLM y obtener análisis
            print("Data loaded. Starting analysis...")
            send_message("🧠 Analizando con IA...", chat_id)
            resultado = analyze_trend(data)

            # 5. Enviar resultado al usuario
            print("Analysis complete. Sending result...")
            send_message(resultado, chat_id)
            print("Result sent.")
        except Exception as e:
            error_msg = f"❌ Error interno: {e}"
            print(error_msg)
            send_message(error_msg, chat_id)


def run_bot():
    """
    Bucle principal del bot. Escucha mensajes de Telegram
    y los procesa según el comando recibido.
    """
    if not TELEGRAM_TOKEN:
        print("Error: TELEGRAM_TOKEN not found.")
        return

    print("🤖 Bot activo...")
    print("Escríbele /analisis")

    last_update_id = 0

    while True:
        try:
            # 1. Obtener updates de Telegram
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?offset={last_update_id + 1}"
            response = requests.get(url)

            if response.status_code != 200:
                print(f"Error getting updates: {response.text}")
                time.sleep(5)
                continue

            updates = response.json()

            # 2. Procesar cada update
            for update in updates.get("result", []):
                last_update_id = update["update_id"]
                message = update.get("message", {})
                texto_usuario = message.get("text", "").lower()
                chat_id = message.get("chat", {}).get("id")

                # 3. Delegar al handler de comandos
                handle_update(texto_usuario, chat_id)

            time.sleep(2)

        except KeyboardInterrupt:
            print("Bot apagado.")
            break
        except Exception as e:
            print(f"Error en el bucle: {e}")
            time.sleep(5)
