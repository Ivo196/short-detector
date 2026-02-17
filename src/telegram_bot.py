import time
import requests

from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from data_download import download_raw_data
from indicators import update_indicators
from data_formatter import load_and_format_data
from analysis import analyze_trend

# ============================================================
# telegram_bot.py — Bot de Telegram para análisis de Ethereum
# ============================================================


def send_message(text, chat_id=None):
    """
    Envía un mensaje por Telegram al chat indicado.

    Args:
        text: Texto del mensaje (soporta HTML).
        chat_id: ID del chat destino. Si no se pasa, usa TELEGRAM_CHAT_ID.
    """
    if not TELEGRAM_TOKEN:
        print("Telegram configuration missing.")
        return

    target_chat_id = chat_id or TELEGRAM_CHAT_ID
    if not target_chat_id:
        print("No chat_id provided and TELEGRAM_CHAT_ID not set.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    try:
        # 1. Intentar enviar con formato HTML
        response = requests.post(url, data={"chat_id": target_chat_id, "text": text, "parse_mode": "HTML"})

        if response.status_code != 200:
            print(f"Error sending message: {response.status_code} - {response.text}")

            # 2. Si falla el HTML (error 400), reintentar como texto plano
            if response.status_code == 400:
                print("Retrying as plain text...")
                retry_resp = requests.post(url, data={"chat_id": target_chat_id, "text": text})
                if retry_resp.status_code != 200:
                    print(f"Retry failed: {retry_resp.status_code} - {retry_resp.text}")
                else:
                    print("Retry success.")
    except Exception as e:
        print(f"Error sending message exception: {e}")


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
            send_message("📊 Analizando indicadores de Ethereum...", chat_id)
            print("Starting analysis flow...")
            data = load_and_format_data()

            # 4. Enviar al LLM y obtener análisis
            print("Data loaded. Starting analysis...")
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

    print(f"🤖 Bot activo. Token: {TELEGRAM_TOKEN[:5]}...")
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
