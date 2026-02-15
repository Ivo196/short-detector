import time
import requests
from app.config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from app.data_loader import load_latest_data, update_data
from app.analysis import analyze_trend

def send_message(text):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram configuration missing.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"})
    except Exception as e:
        print(f"Error sending message: {e}")

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

                if texto_usuario == "/update":
                    send_message("🔄 Actualizando datos de mercado...")
                    try:
                        update_data()
                        send_message("✅ Datos actualizados correctamente.")
                    except Exception as e:
                        send_message(f"❌ Error actualizando datos: {e}")

                elif texto_usuario in ["/analisis", "/short", "hola"]:
                    send_message("⏳ Actualizando datos y calculando indicadores...")
                    try:
                        # 1. Update Data
                        print("Updating data...")
                        update_data()
                        
                        # 2. Analyze
                        send_message("📊 Analizando indicadores de Ethereum (incluyendo EMAs)...")
                        print("Starting analysis flow...")
                        data = load_latest_data()
                        print("Data loaded. Starting analysis...")
                        resultado = analyze_trend(data)
                        print("Analysis complete. Sending result...")
                        send_message(resultado)
                        print("Result sent.")
                    except Exception as e:
                        error_msg = f"❌ Error interno: {e}"
                        print(error_msg)
                        send_message(error_msg)
            
            time.sleep(2)
        except KeyboardInterrupt:
            print("Bot apagado.")
            break
        except Exception as e:
            print(f"Error en el bucle: {e}")
            time.sleep(5)
