import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. APP CONFIGURATION & MINIMALIST THEME ---
st.set_page_config(
    page_title="FortressFIRE Dashboard",
    page_icon="🏰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Elegant Minimalist UI using CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [data-testid="stSidebar"] {
        font-family: 'Inter', sans-serif;
    }
    .main { background-color: #fcfcfd; }
    
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 20px 24px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.02);
        border: 1px solid #f1f5f9;
        transition: all 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
    }
    
    h1 { color: #0f172a; font-weight: 700; letter-spacing: -0.02em; }
    h2, h3 { color: #334155; font-weight: 600; }
    hr { border-top: 1px solid #f1f5f9; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏰 FortressFIRE")
st.caption(f"Minimalist Wealth & Protection Dashboard  •  Live Rate: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.markdown("---")

# --- 2. LIVE DATA CACHING WITH SAFETY ---
@st.cache_data(ttl=1800)
def get_usd_thb_rate():
    try:
        ticker = yf.Ticker("THB=X")
        df = ticker.history(period="1d")
        if not df.empty:
            return float(df['Close'].iloc[-1])
        return float(ticker.fast_info['last_price'])
    except:
        return 36.50

usd_thb = get_usd_thb_rate()

# --- 3. SIDEBAR: CONTROL CENTER ---
st.sidebar.header("🛡️ Control Center")
st.sidebar.markdown("---")

st.sidebar.subheader("💰 สินทรัพย์สภาพคล่อง")
cash_thb = st.sidebar.number_input("เงินสด / เงินฝากธนาคาร (บาท)", value=200000, step=10000)

st.sidebar.subheader("📈 แผนออมรายเดือน")
monthly_invest = st.sidebar.slider("เงินออมลงทุนเพิ่มต่อเดือน (บาท)", 0, 150000, 30000, step=1000)

st.sidebar.subheader("🎯 เป้าหมายชีวิต (FIRE)")
desired_monthly_spend = st.sidebar.number_input("ค่าใช้จ่ายหลังเกษียณ (บาท/เดือน)", value=50000, step
                                                
