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
    /* เปลี่ยนฟอนต์และพื้นหลังหลัก */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [data-testid="stSidebar"] {
        font-family: 'Inter', sans-serif;
    }
    .main { background-color: #fcfcfd; }
    
    /* ปรับแต่งกล่อง Metric ให้มินิมอล มีเงาบางๆ */
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
    
    /* ปรับแต่งหัวข้อ */
    h1 { color: #0f172a; font-weight: 700; letter-spacing: -0.02em; }
    h2, h3 { color: #334155; font-weight: 600; }
    
    /* ปรับแต่งเส้นคั่น */
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
desired_monthly_spend = st.sidebar.number_input("ค่าใช้จ่ายหลังเกษียณ (บาท/เดือน)", value=50000, step=5000)
safe_withdrawal_rate = st.sidebar.slider("Safe Withdrawal Rate (%)", 3.0, 5.0, 4.0, step=0.1) / 100

st.sidebar.subheader("📊 สมมติฐานตลาด")
expected_annual_return = st.sidebar.slider("คาดการณ์ผลตอบแทนพอร์ตต่อปี (%)", 1, 15, 8, step=1) / 100
inflation_rate = st.sidebar.slider("อัตราเงินเฟ้อเฉลี่ยต่อปี (%)", 1, 8, 3, step=1) / 100

# --- 4. MAIN CONTENT: ASSET MANAGEMENT ---
st.header("📦 Live Portfolio")
st.caption("ระบุรายชื่อหุ้นหรือ ETF เพื่อดึงราคารอบปัจจุบัน (หุ้นไทยต่อท้ายด้วย .BK เช่น PTT.BK | รองรับการใส่จำนวนหุ้นเป็นทศนิยม)")

# รายการสินทรัพย์เริ่มต้น (Default Assets)
default_assets = [
    ("VOO", 15.4520, 420.0),   # ตัวอย่างเศษหุ้นสหรัฐฯ มีทศนิยม
    ("SCHD", 55.0, 75.0),
    ("PTT.BK", 1500.0, 34.0),
    ("CPALL.BK", 800.0, 60.0),
    ("KTB.BK", 2000.0, 16.0),
    ("", 0.0, 0.0)
]

input_assets = []
cols_header = st.columns([2, 2, 2, 2])
cols_header[0].markdown("**ชื่อย่อสินทรัพย์ (Symbol)**")
cols_header[1].markdown("**จำนวนที่ถือ (Qty)**")
cols_header[2].markdown("**ราคาต้นทุนเฉลี่ย (Avg Cost)**")
cols_header[3].markdown("**ตลาด / สกุลเงิน**")

for i, (def_sym, def_qty, def_cost) in enumerate(default_assets):
    cols = st.columns([2, 2, 2, 2])
    with cols[0]:
        sym = cols[0].text_input(f"Asset {i+1}", value=def_sym, key=f"sym_{i}").upper().strip()
    with cols[1]:
        # ปรับฟังก์ชันให้รองรับ float (ทศนิยม) และระบุค่าสเต็ปการขยับละเอียดขึ้น
        qty = cols[1].number_input(f"Qty {i+1}", value=float(def_qty), min_value=0.0, step=0.0001, format="%.4f", key=f"qty_{i}")
    with cols[2]:
        cost = cols[2].number_input(f"Cost {i+1}", value=float(def_cost), min_value=0.0, step=0.01, key=f"cost_{i}")
    with cols[3]:
        if sym:
            market_type = "🇹🇭 ไทย (THB)" if ".BK" in sym else "🇺🇸 อเมริกา (USD)"
            cols[3].markdown(f"<br><span style='color:#64748b; font-size: 14px;'>{market_type}</span>", unsafe_allow_html=True)
            input_assets.append({"symbol": sym, "qty": qty, "cost": cost, "is_th": ".BK" in sym})
        else:
            cols[3].write("")

# --- 5. CALCULATION LOGIC ---
portfolio_details = []
total_stock_value_thb = 0
total_cost_thb = 0

if input_assets:
    with st.spinner("🏰 กำลังอัปเดตมูลค่าป้อมปราการ..."):
        for item in input_assets:
            if item["qty"] <= 0:
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
                st.error(f"⚠️ ไม่สามารถดึงราคา {item['symbol']} ได้")

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
                "สินทรัพย์": item["symbol"],
                "จำนวนหุ้น": qty_float, # แสดงผลทศนิยมตรงๆ ในตาราง
                "ต้นทุนเฉลี่ย": f"{cost_float:,.2f}",
                "ราคาปัจจุบัน": f"{live_price:,.2f}",
                "มูลค่ารวม (บาท)": round(current_val, 2),
                "กำไร/ขาดทุน (บาท)": round(p_l, 2),
                "กำไร/ขาดทุน (%)": f"{p_l_pct:+.2f}%"
            })

net_worth = float(total_stock_value_thb + cash_thb)
fire_target = float((desired_monthly_spend * 12) / safe_withdrawal_rate)

# --- 6. UI DISPLAY: FINANCIAL METRICS ---
st.markdown("---")
st.header("📊 Wealth Summary")

m1, m2, m3, m4 = st.columns(4)
m1.metric("ความมั่งคั่งสุทธิ (Net Worth)", f"{net_worth:,.0f} ฿")
m2.metric("เป้าหมาย FortressFIRE", f"{fire_target:,.0f} ฿")

total_pl = total_stock_value_thb - total_cost_thb
total_pl_pct = (total_pl / total_cost_thb) * 100 if total_cost_thb > 0 else 0
m3.metric("ผลกำไร/ขาดทุนรวม", f"{total_pl:,.0f} ฿", f"{total_pl_pct:+.2f}%")
m4.metric("อัตราแลกเปลี่ยน", f"{usd_thb:.2f} ฿/USD")

# แถบแสดงความคืบหน้า (Minimal Progress Bar)
progress = min(net_worth / fire_target, 1.0)
st.write(f"**🛡️ ระดับการป้องกันป้อมปราการความมั่งคั่ง: {progress*100:.2f}%**")
st.progress(progress)

# แสดงตารางสินทรัพย์แบบคลีน
if portfolio_details:
    st.subheader("📋 บัญชีสรุปสินทรัพย์")
    st.dataframe(pd.DataFrame(portfolio_details), use_container_width=True, hide_index=True)

# --- 7. FUTURE PROJECTION (SIMULATION) ---
st.markdown("---")
st.header("⏳ เส้นทางการเติบโตในอนาคต")

real_annual_return = ((1 + expected_annual_return) / (1 + inflation_rate)) - 1
monthly_rate = (1 + real_annual_return)**(1/12) - 1

history = []
balance = net_worth
months = 0
reached_fire = False
target_month = 0

for year in range(0, 41): 
    history.append({"Year": year, "Balance": balance})
    for m in range(12):
        if balance >= fire_target and not reached_fire:
            reached_fire = True
            target_month = months
        balance = (balance + float(monthly_invest)) * (1 + monthly_rate)
        months += 1

df_history = pd.DataFrame(history)

# กราฟสไตล์มินิมอล โทนสีเข้ม-สะอาดตา
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_history['Year'], 
    y=df_history['Balance'], 
    name='มูลค่าพอร์ตจริงหลังหักเงินเฟ้อ',
    line=dict(color='#0f172a', width=3) # สี Slate Dark แบบพรีเมียม
))
fig.add_hline(y=fire_target, line_dash="dash", line_color="#ef4444", line_width=1.5, annotation_text="FIRE Target")
fig.update_layout(
    xaxis_title="จำนวนปีข้างหน้า",
    yaxis_title="มูลค่าเงิน (บาท)",
    hovermode="x unified",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=20, r=20, t=40, b=20),
    xaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
    yaxis=dict(showgrid=True, gridcolor='#f1f5f9')
)
st.plotly_chart(fig, use_container_width=True)

if reached_fire:
    years_needed = target_month // 12
    months_needed = target_month % 12
    st.success(f"🎉 **ความสำเร็จของ FortressFIRE:** คุณจะบรรลุเป้าหมายเกษียณในอีก **{years_needed} ปี {months_needed} เดือน** (ประมาณปี ค.ศ. {datetime.now().year + years_needed})")
else:
    st.warning("⚠️ **คำแนะนำจาก Fortress:** ด้วยระดับการออมปัจจุบัน พอร์ตอาจต้องใช้เวลามากกว่า 40 ปีในการบรรลุเป้าหมาย แนะนำปรับสัดส่วนเพื่อขยับประสิทธิภาพพอร์ต")
