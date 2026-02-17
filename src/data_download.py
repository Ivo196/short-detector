import os
import yfinance as yf

# ============================================================
# data_download.py — Descarga de datos crudos de Ethereum
# ============================================================

# --- Constantes ---
DATA_DIR = "data/raw_data"
RAW_FILE = f"{DATA_DIR}/ethereum_1d_raw.csv"
TICKER = "ETH-USD"
INTERVAL = "1d"


def download_raw_data():
    """
    Descarga datos históricos de Ethereum desde Yahoo Finance
    y los guarda en un archivo CSV.

    Returns:
        pd.DataFrame: DataFrame con los datos crudos descargados.
    """
    # 1. Crear directorio si no existe
    os.makedirs(DATA_DIR, exist_ok=True)

    # 2. Descargar datos con yfinance
    print(f"Downloading data for {TICKER}...")
    df_raw = yf.download(TICKER, period="max", interval=INTERVAL, multi_level_index=False)

    if df_raw.empty:
        raise Exception("No data downloaded from Yahoo Finance")

    # 3. Guardar CSV crudo
    df_raw.to_csv(RAW_FILE)
    print(f"Raw data saved to {RAW_FILE}")

    return df_raw
