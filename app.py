import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. APP CONFIGURATION & PREMIUM FINTECH THEME ---
st.set_page_config(
    page_title="FortressFIRE Dashboard",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium SaaS Layout CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
        font-family: 'Inter', sans-serif;
        background-color: #f8fafc !important;
    }
    
    h1 { color: #0f172a; font-weight: 700; letter-spacing: -0.03em; font-size: 28px; margin-bottom: 2px; }
    h2, h3 { color: #1e293b; font-weight: 600; letter-spacing: -0.01em; }
    
    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        padding: 24px !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.02), 0 2px 4px -2px rgba(15, 23, 42, 0.02), 0 0 0 1px rgba(15, 23, 42, 0.04) !important;
    }
    
    .portfolio-container {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.02), 0 0 0 1px rgba(15, 23, 42, 0.04);
        margin-bottom: 24px;
    }
    
    .stDataFrame div { border-radius: 12px; }
    .stProgress > div > div > div > div { background-color: #10b981; }
    hr { border-top: 1px solid #e2e8f0 !important; }
    </style>
    """, unsafe_allow_html=True)

# Top Bar Header
cols_top = st.columns([8, 4])
with cols_top[0]:
    st.markdown("<h1>Dashboard</h1>", unsafe_allow_html=True)
    st.caption("Your finances at a glance  •  Live Portfolio Analytics")
with cols_top[1]:
    st.markdown(f"<div style='text-align: right; color: #64748b; font-size: 13px; padding-top: 12px;'>Live Rate: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>", unsafe_allow_html=True)

st.markdown("<hr style='margin-top: 10px; margin-bottom: 25px;'>", unsafe_allow_html=True)

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
st.sidebar.markdown("<h3 style='margin-top:0;'>⚙️ Control Center</h3>", unsafe_allow_html=True)
st.sidebar.markdown("---")

st.sidebar.subheader("💰 Liquidity & Saving")
cash_thb = st.sidebar.number_input("เงินสด / เงินฝากธนาคาร (บาท)", value=200000, step=10000)
monthly_invest = st.sidebar.slider("เงินออมลงทุนเพิ่มต่อเดือน (บาท)", 0, 150000, 30000, step=1000)

st.sidebar.subheader("🎯 FIRE Blueprint")
desired_monthly_spend = st.sidebar.number_input("ค่าใช้จ่ายหลังเกษียณ (บาท/เดือน)", value=50000, step=5000)
safe_withdrawal_rate = st.sidebar.slider("Safe Withdrawal Rate (%)", 3.0, 5.0, 4.0, step=0.1) / 100

st.sidebar.subheader("📊 Market Assumptions")
expected_annual_return = st.sidebar.slider("คาดการณ์ผลตอบแทนพอร์ตต่อปี (%)", 1, 15, 8, step=1) / 100
inflation_rate = st.sidebar.slider("อัตราเงินเฟ้อเฉลี่ยต่อปี (%)", 1, 8, 3, step=1) / 100

# --- 4. 🔑 SESSION STATE INITIALIZATION (กลไกจำค่าอินพุต) ---
# กำหนดค่าเริ่มต้นให้กับกล่องรับข้อมูลระบบ (ทำครั้งเดียวตอนเปิดหน้าเว็บครั้งแรก)
num_assets = 6
default_values = [
    ("VOO", 15.452381924, 420.551283941),   
    ("SCHD", 55.129402811, 75.238491024),
    ("PTT.BK", 1500.0, 34.0),
    ("CPALL.BK", 800.0, 60.0),
    ("KTB.BK", 2000.0, 16.0),
    ("", 0.0, 0.0)
]

for i in range(num_assets):
    def_sym, def_qty, def_cost = default_values[i]
    if f"sym_{i}" not in st.session_state:
        st.session_state[f"sym_{i}"] = def_sym
    if f"qty_{i}" not in st.session_state:
        st.session_state[f"qty_{i}"] = float(def_qty)
    if f"cost_{i}" not in st.session_state:
        st.session_state[f"cost_{i}"] = float(def_cost)

# --- 5. MAIN CONTENT: ASSET MANAGEMENT CARD ---
st.markdown("<div class='portfolio-container'>", unsafe_allow_html=True)
st.subheader("Your Holdings")
st.caption("ระบุรายชื่อหุ้นหรือ ETF เพื่อแทร็กข้อมูล (ระบบจะล็อกและบันทึกค่าสิ่งที่คุณกรอกไว้ในความทรงจำอัตโนมัติ)")

input_assets = []
cols_header = st.columns([2, 3, 3, 2])
cols_header[0].markdown("<small style='color: #64748b; font-weight:600;'>SYMBOL</small>", unsafe_allow_html=True)
cols_header[1].markdown("<small style='color: #64748b; font-weight:600;'>VALUE (Qty)</small>", unsafe_allow_html=True)
cols_header[2].markdown("<small style='color: #64748b; font-weight:600;'>AVG COST</small>", unsafe_allow_html=True)
cols_header[3].markdown("<small style='color: #64748b; font-weight:600;'>MARKET</small>", unsafe_allow_html=True)

for i in range(num_assets):
    cols = st.columns([2, 3, 3, 2])
    with cols[0]:
        # ใช้พารามิเตอร์ key เพื่อผูกมัดค่าไว้กับ st.session_state โดยตรง
        sym = cols[0].text_input(f"Asset {i+1}", key=f"sym_{i}", label_visibility="collapsed").upper().strip()
    with cols[1]:
        qty = cols[1].number_input(f"Qty {i+1}", min_value=0.0, step=0.000000001, format="%.9f", key=f"qty_{i}", label_visibility="collapsed")
    with cols[2]:
        cost = cols[2].number_input(f"Cost {i+1}", min_value=0.0, step=0.000000001, format="%.9f", key=f"cost_{i}", label_visibility="collapsed")
    with cols[3]:
        if sym:
            market_type = "🇹🇭 THB" if ".BK" in sym else "🇺🇸 USD"
            cols[3].markdown(f"<div style='padding-top: 6px; color:#475569; font-size: 14px; font-weight:500;'>{market_type}</div>", unsafe_allow_html=True)
            input_assets.append({"symbol": sym, "qty": qty, "cost": cost, "is_th": ".BK" in sym})
        else:
            cols[3].write("")
st.markdown("</div>", unsafe_allow_html=True)

# --- 6. CALCULATION LOGIC ---
portfolio_details = []
total_stock_value_thb = 0.0
total_cost_thb = 0.0

if input_assets:
    for item in input_assets:
        if item["qty"] <= 0.0:
            continue
            
        ticker = yf.Ticker(item["symbol"])
        try:
            df_asset = ticker.history(period="1d")
            if not df_asset.empty:
                live_price = float(df_asset['Close'].iloc[-1])
            else:
                live_price = float(ticker.fast_info['last_price'])
        except:
            live_price = float(item["cost"])

        qty_float = float(item["qty"])
        cost_float = float(item["cost"])

        if item["is_th"]:
            current_val = live_price * qty_float
            cost_val = cost_float * qty_float
        else:
            current_val = (live_price * qty_float) * float(usd_thb)
            cost_val = (cost_float * qty_float) * float(usd_thb)

        p_l = current_val - cost_val
        p_l_pct = (p_l / cost_val) * 100 if cost_val > 0 else 0

        total_stock_value_thb += current_val
        total_cost_thb += cost_val

        portfolio_details.append({
            "SYMBOL": item["symbol"],
            "HOLDINGS (Qty)": f"{qty_float:.9f}",
            "AVG COST": f"{cost_float:.9f}",
            "LIVE PRICE": f"{live_price:,.2f}",
            "VALUE (THB)": round(current_val, 2),
            "P&L (THB)": round(p_l, 2),
            "CHANGE": f"{p_l_pct:+.2f}%"
        })

net_worth = float(total_stock_value_thb + cash_thb)
fire_target = float((desired_monthly_spend * 12) / safe_withdrawal_rate)

# --- 7. UI DISPLAY: FINANCIAL METRICS ---
st.subheader("Financial Overview")

m1, m2, m3, m4 = st.columns(4)
m1.metric("NET WORTH", f"฿{net_worth:,.0f}")
m2.metric("FIRE TARGET", f"฿{fire_target:,.0f}")

total_pl = total_stock_value_thb - total_cost_thb
total_pl_pct = (total_pl / total_cost_thb) * 100 if total_cost_thb > 0 else 0
m3.metric("ALL TIME P&L", f"฿{total_pl:,.0f}", f"{total_pl_pct:+.2f}%")
m4.metric("FX RATE (USD/THB)", f"{usd_thb:.2f}")

# Progress bar
st.markdown("<br>", unsafe_allow_html=True)
progress = min(net_worth / fire_target, 1.0)
st.markdown(f"<div style='font-size: 14px; font-weight:600; color:#334155; margin-bottom:6px;'>🛡️ Progress to Freedom: {progress*100:.2f}%</div>", unsafe_allow_html=True)
st.progress(progress)

# ตารางผลลัพธ์พอร์ต
if portfolio_details:
    st.markdown("<br>", unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(portfolio_details), use_container_width=True, hide_index=True)

# --- 8. FUTURE PROJECTION (SIMULATION) ---
st.markdown("<br><hr>", unsafe_allow_html=True)
st.subheader("Growth Projection")
st.caption("การเติบโตแบบจำลองพอร์ตโฟลิโอสะสมระยะยาว (หลังหักอัตราเงินเฟ้อแล้ว)")

real_annual_return = ((1 + expected_annual_return) / (1 + inflation_rate)) - 1
monthly_rate = (1 + real_annual_return)**(1/12) - 1

history = []
balance = net_worth
months = 0
reached_fire = False
target_month = 0

for year in range(0, 41): 
    history.append({"Year": year, "Portfolio Value": balance})
    for m in range(12):
        if balance >= fire_target and not reached_fire:
            reached_fire = True
            target_month = months
        balance = (balance + float(monthly_invest)) * (1 + monthly_rate)
        months += 1

df_history = pd.DataFrame(history)

# กราฟสไตล์ FinTech
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_history['Year'], 
    y=df_history['Portfolio Value'], 
    name='Net Worth',
    line=dict(color='#0f172a', width=3.5),
    hovertemplate="Year %{x}: ฿%{y:,.0f}<extra></extra>"
))
fig.add_hline(y=fire_target, line_dash="dash", line_color="#10b981", line_width=1.5, annotation_text="FIRE Target", annotation_position="top left")
fig.update_layout(
    xaxis_title="Years",
    yaxis_title="Amount (THB)",
    hovermode="x unified",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=20, b=10),
    xaxis=dict(showgrid=True, gridcolor='#f1f5f9', tickmode='linear', tick0=0, dtick=5),
    yaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig, use_container_width=True)

if reached_fire:
    years_needed = target_month // 12
    months_needed = target_month % 12
    st.success(f"🎉 **Milestone Achieved:** คุณจะบรรลุเป้าหมายเกษียณในอีก **{years_needed} ปี {months_needed} เดือน** (ประมาณปี ค.ศ. {datetime.now().year + years_needed})")
else:
    st.warning("⚠️ **Optimization Recommended:** ด้วยอัตราการออมปัจจุบัน พอร์ตอาจใช้เวลามากกว่า 40 ปีในการโตไปถึงเป้าหมาย แนะนำให้ลองปรับสมมติฐานหรือเงินออมเพื่อเร่งเวลาเพิ่มขึ้นครับ")
