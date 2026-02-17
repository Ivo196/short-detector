import sys
import os

# Add the src/ directory to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

try:
    # 1. Config
    from config import TELEGRAM_TOKEN, OPENAI_API_KEY
    print("Config loaded successfully.")
    if not TELEGRAM_TOKEN:
        print("Warning: TELEGRAM_TOKEN is missing or empty.")
    if not OPENAI_API_KEY:
        print("Warning: OPENAI_API_KEY is missing or empty.")

    # 2. Data Download
    from data_download import download_raw_data
    print("DataDownload module imported successfully.")

    # 3. Indicators
    from indicators import calculate_indicators, update_indicators
    print("Indicators module imported successfully.")

    # 4. Data Formatter
    from data_formatter import load_and_format_data
    print("DataFormatter module imported successfully.")

    # 5. Analysis
    from analysis import analyze_trend
    print("Analysis module imported successfully.")

    # 6. Telegram Bot
    from telegram_bot import run_bot
    print("TelegramBot module imported successfully.")

    print("All imports successful.")
except Exception as e:
    print(f"Import failed: {e}")
    sys.exit(1)
