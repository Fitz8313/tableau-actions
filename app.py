
import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import ta

st.set_page_config(page_title="Tableau de Bord Actions", layout="wide")

# Initialisation
if "tickers" not in st.session_state:
    st.session_state.tickers = ["AAPL", "MSFT", "TSLA"]

st.title("📊 Tableau de Bord - Suivi d'Actions")

# --- Barre latérale pour gérer les tickers
st.sidebar.header("⚙️ Paramètres")
st.sidebar.subheader("Ajouter une action")
new_ticker = st.sidebar.text_input("Symbole (ex: GOOGL, NVDA)", "")
if st.sidebar.button("Ajouter") and new_ticker.upper() not in st.session_state.tickers:
    st.session_state.tickers.append(new_ticker.upper())

# Supprimer des tickers
remove_ticker = st.sidebar.selectbox("Supprimer une action", st.session_state.tickers)
if st.sidebar.button("Supprimer"):
    st.session_state.tickers.remove(remove_ticker)

# --- Boucle sur les tickers
for ticker in st.session_state.tickers:
    st.header(f"📈 Analyse : {ticker}")
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="6mo")
        data['SMA20'] = data['Close'].rolling(window=20).mean()
        data['RSI'] = ta.momentum.RSIIndicator(close=data['Close']).rsi()

        # Affichage du graphique de prix
        fig, ax = plt.subplots()
        ax.plot(data['Close'], label="Cours de clôture")
        ax.plot(data['SMA20'], label="SMA 20", linestyle="--")
        ax.set_title(f"{ticker} - Cours")
        ax.legend()
        st.pyplot(fig)

        # RSI
        st.subheader("📍 RSI")
        fig2, ax2 = plt.subplots()
        ax2.plot(data['RSI'], label='RSI', color='orange')
        ax2.axhline(70, color='red', linestyle='--')
        ax2.axhline(30, color='green', linestyle='--')
        ax2.set_title("RSI")
        ax2.legend()
        st.pyplot(fig2)

        # Signal
        last_rsi = data['RSI'].dropna().iloc[-1]
        if last_rsi < 30:
            st.success("🔔 Signal d'achat (RSI < 30)")
        elif last_rsi > 70:
            st.error("🔔 Signal de vente (RSI > 70)")
        else:
            st.info("RSI neutre")

        # Fondamentaux
        st.subheader("📊 Données économiques")
        try:
            fundamentals = stock.financials.T
            st.dataframe(fundamentals.style.format("{:,.0f}"))
        except:
            st.warning("Données financières non disponibles.")

        st.markdown("---")

    except Exception as e:
        st.error(f"Erreur pour {ticker} : {e}")
