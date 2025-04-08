import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(page_title="Stock Volume Tracker", layout="wide")

st.title("📊 Stock Rotation & Volume Tracker")

# Entrada de usuario
tickers = st.text_input("Escribe los tickers separados por comas (ej: NAOV, TOP, SIDU)", "NAOV, TOP, SIDU")
ticker_list = [t.strip().upper() for t in tickers.split(",")]

# Hora actual NY
ny_tz = pytz.timezone("America/New_York")
now_ny = datetime.now(ny_tz)
market_open_time = now_ny.replace(hour=9, minute=30, second=0, microsecond=0)
minutes_since_open = (now_ny - market_open_time).total_seconds() / 60
minutes_since_open = max(0, round(minutes_since_open))

st.markdown(f"🕒 Tiempo desde apertura: **{minutes_since_open} minutos**")

# Datos
data = []

for ticker in ticker_list:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        df = stock.history(period="1d", interval="1m")

        if df.empty:
            continue

        last_price = df["Close"].iloc[-1]
        open_price = df["Open"].iloc[0]
        volume = df["Volume"].sum()
        change = ((last_price - open_price) / open_price) * 100

        shares_float = info.get("floatShares", None)
        if shares_float:
            rotation = volume / shares_float
        else:
            rotation = None

        data.append({
            "Ticker": ticker,
            "Precio actual": round(last_price, 3),
            "Apertura": round(open_price, 3),
            "% Cambio": round(change, 2),
            "Volumen": f"{volume:,}",
            "Float": f"{shares_float:,}" if shares_float else "N/A",
            "Rotación del Float": round(rotation, 2) if rotation else "N/A"
        })

    except Exception as e:
        st.error(f"Error con {ticker}: {e}")

# Mostrar tabla
if data:
    df_display = pd.DataFrame(data)
    st.dataframe(df_display, use_container_width=True)
else:
    st.warning("No se encontraron datos.")
