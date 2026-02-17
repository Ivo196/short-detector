import ta

from data_download import DATA_DIR

# ============================================================
# indicators.py — Cálculo de indicadores técnicos
# ============================================================

# --- Constantes ---
INDICATORS_FILE = f"{DATA_DIR}/ethereum_1d_indicators_raw.csv"


def calculate_indicators(df):
    """
    Recibe un DataFrame con datos OHLCV crudos y le agrega
    todos los indicadores técnicos.

    Args:
        df: DataFrame con columnas 'Close', 'High', 'Low' como mínimo.

    Returns:
        pd.DataFrame: DataFrame con indicadores técnicos añadidos (sin NaN).
    """
    df = df.copy()

    # 1. RSI (Relative Strength Index)
    df['RSI'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()

    # 2. Bollinger Bands
    bb = ta.volatility.BollingerBands(close=df['Close'], window=20, window_dev=2)
    df['BB_High'] = bb.bollinger_hband()
    df['BB_Low'] = bb.bollinger_lband()
    df['BB_Mid'] = bb.bollinger_mavg()

    # 3. MACD (Moving Average Convergence Divergence)
    macd = ta.trend.MACD(close=df['Close'])
    df['MACD_Line'] = macd.macd()
    df['MACD_Signal'] = macd.macd_signal()
    df['MACD_Hist'] = macd.macd_diff()

    # 4. ATR (Average True Range)
    df['ATR'] = ta.volatility.AverageTrueRange(
        high=df['High'], low=df['Low'], close=df['Close'], window=14
    ).average_true_range()

    # 5. ADX (Average Directional Index)
    adx = ta.trend.ADXIndicator(high=df['High'], low=df['Low'], close=df['Close'])
    df['ADX'] = adx.adx()
    df['ADX+'] = adx.adx_pos() #+DI
    df['ADX-'] = adx.adx_neg() #-DI

    # 6. EMAs (Exponential Moving Averages)
    df['EMA_20'] = ta.trend.EMAIndicator(close=df['Close'], window=20).ema_indicator()
    df['EMA_50'] = ta.trend.EMAIndicator(close=df['Close'], window=50).ema_indicator()
    df['EMA_200'] = ta.trend.EMAIndicator(close=df['Close'], window=200).ema_indicator()

    # 7. Limpiar filas con NaN (los primeros días no tienen suficiente historia)
    df_clean = df.dropna()

    return df_clean


def update_indicators(df_raw):
    """
    Calcula indicadores sobre los datos crudos y guarda el resultado en CSV.

    Args:
        df_raw: DataFrame con datos OHLCV crudos.
    """
    # 1. Calcular indicadores
    print("Calculating technical indicators...")
    df_indicators = calculate_indicators(df_raw)

    # 2. Guardar en CSV
    df_indicators.to_csv(INDICATORS_FILE)
    print(f"Indicators saved to {INDICATORS_FILE}")

    return df_indicators
