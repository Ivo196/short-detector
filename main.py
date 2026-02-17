import sys
import os

# ============================================================
# main.py — Punto de entrada del bot
# ============================================================

# Agregar la carpeta src/ al path para que los imports funcionen
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from telegram_bot import run_bot

if __name__ == "__main__":
    run_bot()
