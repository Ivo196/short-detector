import time
import requests
from app.config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from app.data_loader import load_latest_data, update_data
from app.analysis import analyze_trend

def send_message(text, chat_id=None):
    if not TELEGRAM_TOKEN:
        print("Telegram configuration missing.")
        return

    target_chat_id = chat_id if chat_id else TELEGRAM_CHAT_ID

    if not target_chat_id:
        print("No chat_id provided and TELEGRAM_CHAT_ID not set.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        # Use HTML parsing for robust formatting
        response = requests.post(url, data={"chat_id": target_chat_id, "text": text, "parse_mode": "HTML"})
        if response.status_code != 200:
            print(f"Error sending message: {response.status_code} - {response.text}")
            # If HTML parsing fails (often error 400), try sending as plain text
            if response.status_code == 400:
                print("Retrying as plain text...")
                retry_resp = requests.post(url, data={"chat_id": target_chat_id, "text": text})
                if retry_resp.status_code != 200:
                    print(f"Retry failed: {retry_resp.status_code} - {retry_resp.text}")
                else:
                    print("Retry success.")
    except Exception as e:
        print(f"Error sending message exception: {e}")

def run_bot():
    if not TELEGRAM_TOKEN:
        print("Error: TELEGRAM_TOKEN not found.")
        return

    print(f"🤖 Bot activo. Token: {TELEGRAM_TOKEN[:5]}...")
    print("Escríbele /analisis, /short o /update.")

    last_update_id = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?offset={last_update_id + 1}"
            response = requests.get(url)
            
            if response.status_code != 200:
                print(f"Error getting updates: {response.text}")
                time.sleep(5)
                continue
            
            updates = response.json()

            for update in updates.get("result", []):
                last_update_id = update["update_id"]
                message = update.get("message", {})
                texto_usuario = message.get("text", "").lower()

                chat_id = message.get("chat", {}).get("id")
                
                if texto_usuario == "/update":
                    send_message("🔄 Actualizando datos de mercado...", chat_id)
                    try:
                        update_data()
                        send_message("✅ Datos actualizados correctamente.", chat_id)
                    except Exception as e:
                        send_message(f"❌ Error actualizando datos: {e}", chat_id)

                elif texto_usuario in ["/analisis", "/short", "hola"]:
                    send_message("⏳ Actualizando datos y calculando indicadores...", chat_id)
                    try:
                        # 1. Update Data
                        print("Updating data...")
                        update_data()
                        
                        # 2. Analyze
                        send_message("📊 Analizando indicadores de Ethereum...", chat_id)
                        print("Starting analysis flow...")
                        data = load_latest_data()
                        print("Data loaded. Starting analysis...")
                        resultado = analyze_trend(data)
                        print("Analysis complete. Sending result...")
                        send_message(resultado, chat_id)
                        print("Result sent.")
                    except Exception as e:
                        error_msg = f"❌ Error interno: {e}"
                        print(error_msg)
                        send_message(error_msg, chat_id)
            
            time.sleep(2)
        except KeyboardInterrupt:
            print("Bot apagado.")
            break
        except Exception as e:
            print(f"Error en el bucle: {e}")
            time.sleep(5)
