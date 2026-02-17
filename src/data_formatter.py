import os
import pandas as pd

from indicators import INDICATORS_FILE

# ============================================================
# data_formatter.py — Formateo de datos para el prompt del LLM
# ============================================================


def load_and_format_data(days=7):
    """
    Lee el CSV de indicadores y devuelve los últimos N días
    formateados como tabla Markdown para enviar al LLM.

    Args:
        days: Número de días recientes a incluir (default: 7).

    Returns:
        str: Tabla en formato Markdown con los indicadores.
    """
    filepath = INDICATORS_FILE

    # 1. Verificar que el archivo existe (compatible con Docker)
    if not os.path.exists(filepath):
        docker_path = f"/app/{filepath}"
        if os.path.exists(docker_path):
            filepath = docker_path
        else:
            raise FileNotFoundError(
                f"Indicators file not found at '{INDICATORS_FILE}'. "
                "Run /analisis first to download and calculate data."
            )

    # 2. Leer CSV
    print(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath, index_col=0, parse_dates=True)

    # 3. Tomar los últimos N días
    last_days = df.tail(days)
    print(f"Data loaded successfully. Shape: {last_days.shape}")

    # 4. Convertir a tabla Markdown
    return last_days.to_markdown()
