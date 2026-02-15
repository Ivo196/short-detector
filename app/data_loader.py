import pandas as pd
import os
import yfinance as yf
import ta

DATA_DIR = "data/raw_data"
RAW_FILE = f"{DATA_DIR}/ethereum_1d_raw.csv"
INDICATORS_FILE = f"{DATA_DIR}/ethereum_1d_indicators_raw.csv"
TICKER = "ETH-USD"
INTERVAL = "1d"

def update_data():
    """
    Downloads new data, calculates indicators (including EMAs), and saves to CSV.
    """
    print(f"Downloading data for {TICKER}...")
    try:
        # 1. Download Data
        df_raw = yf.download(TICKER, period="max", interval=INTERVAL, multi_level_index=False)
        if df_raw.empty:
            raise Exception("No data downloaded")
        
        # Ensure data dir exists
        os.makedirs(DATA_DIR, exist_ok=True)
        df_raw.to_csv(RAW_FILE)
        print(f"Raw data saved to {RAW_FILE}")

        # 2. Calculate Indicators
        df = df_raw.copy()
        
        # RSI
        df['RSI'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()
        
        # Bollinger Bands
        bb = ta.volatility.BollingerBands(close=df['Close'], window=20, window_dev=2)
        df['BB_High'] = bb.bollinger_hband()
        df['BB_Low'] = bb.bollinger_lband()
        df['BB_Mid'] = bb.bollinger_mavg()
        
        # MACD
        macd = ta.trend.MACD(close=df['Close'])
        df['MACD_Line'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Hist'] = macd.macd_diff()
        
        # ATR
        df['ATR'] = ta.volatility.AverageTrueRange(high=df['High'], low=df['Low'], close=df['Close'], window=14).average_true_range()

        # EMAs (20, 50, 200) - NEW
        df['EMA_20'] = ta.trend.EMAIndicator(close=df['Close'], window=20).ema_indicator()
        df['EMA_50'] = ta.trend.EMAIndicator(close=df['Close'], window=50).ema_indicator()
        df['EMA_200'] = ta.trend.EMAIndicator(close=df['Close'], window=200).ema_indicator()

        # Clean NaN
        df_final = df.dropna()
        
        df_final.to_csv(INDICATORS_FILE)
        print(f"Indicators saved to {INDICATORS_FILE}")
        return True
    except Exception as e:
        print(f"Error updating data: {e}")
        raise e

def load_latest_data(filepath=INDICATORS_FILE, days=7):
    """
    Loads validation data from CSV and returns the last 'days' rows formatted as markdown.
    """
    if not os.path.exists(filepath):
        # Fallback for Docker if path is different or relative to root
        # In Docker we expect it at /app/data/raw_data/...
        if os.path.exists(f"/app/{filepath}"):
             filepath = f"/app/{filepath}"
        else:
             # Try to update if not found? Or just raise
             pass
    
    try:
        print(f"Loading data from {filepath}...")
        df = pd.read_csv(filepath, index_col=0, parse_dates=True)
        # Select the last 'days'
        last_days = df.tail(days)
        print(f"Data loaded successfully. Shape: {last_days.shape}")
        # Convert to markdown
        return last_days.to_markdown()
    except Exception as e:
        print(f"Error in load_latest_data: {e}")
        raise Exception(f"Error loading data: {e}")

