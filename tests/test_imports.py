import sys
import os

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from app.config import TELEGRAM_TOKEN, OPENAI_API_KEY
    print("Config loaded successfully.")
    if not TELEGRAM_TOKEN:
        print("Warning: TELEGRAM_TOKEN is missing or empty.")
    if not OPENAI_API_KEY:
        print("Warning: OPENAI_API_KEY is missing or empty.")

    from app.data_loader import load_latest_data
    print("DataLoader module imported successfully.")

    from app.analysis import analyze_trend
    print("Analysis module imported successfully.")

    from app.telegram_bot import run_bot
    print("TelegramBot module imported successfully.")

    print("All imports successful.")
except Exception as e:
    print(f"Import failed: {e}")
    sys.exit(1)
