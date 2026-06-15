import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. APP CONFIGURATION & THEME ---
st.set_page_config(
    page_title="FortressFIRE Dashboard",
    page_icon="🏰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Minimalist & Secure Theme using CSS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e9ecef; }
    h1 { color: #1e293b; font-weight: 700; }
    h2, h3 { color: #334155; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏰 FortressFIRE: Wealth & Protection Dashboard")
st.caption(f"ระบบจำลองแผนเกษียณและอัปเดตพอร์ตเรียลไทม์ • อัปเดตล่าสุด: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
st.markdown("---")

# --- 2. LIVE DATA CACHING ---
@st.cache_data(ttl=1800) # อัปเดตทุก 30 นาที
def get_usd_thb_rate():
    try:
        return yf.Ticker("THB=X").fast_info['last_price']
    except:
        return 36.50

usd_thb = get_usd_thb_rate()

# --- 3. SIDEBAR: CONTROL CENTER ---
st.sidebar.header("🛡️ ป้อมควบคุม FortressFIRE")
st.sidebar.markdown("---")

st.sidebar.subheader("💰 สินทรัพย์สภาพคล่อง")
cash_thb = st.sidebar.number_input("เงินสด / เงินฝากธนาคาร (บาท)", value=200000, step=10000)

st.sidebar.subheader("📈 แผนออมรายเดือน")
monthly_invest = st.sidebar.slider("เงินออมลงทุนเพิ่มต่อเดือน (บาท)", 0, 150000, 30000, step=500)

st.sidebar.subheader("🎯 เป้าหมายการใช้ชีวิต")
desired_monthly_spend = st.sidebar.number_input("ค่าใช้จ่ายหลังเกษียณ (บาท/เดือน)", value=50000, step=5000)
safe_withdrawal_rate = st.sidebar.slider("Safe Withdrawal Rate (%)", 3.0, 5.0, 4.0, step=0.1) / 100

st.sidebar.subheader("📊 สมมติฐานตลาด")
expected_annual_return = st.sidebar.slider("คาดการณ์ผลตอบแทนพอร์ตต่อปี (%)", 1, 15, 8, step=1) / 100
inflation_rate = st.sidebar.slider("อัตราเงินเฟ้อเฉลี่ยต่อปี (%)", 1, 8, 3, step=1) / 100

# --- 4. MAIN CONTENT: ASSET MANAGEMENT ---
st.header("📦 ระบบจัดการพอร์ตสินทรัพย์ (Live Portfolio)")
st.caption("ระบุรายชื่อหุ้น/ETF เพื่อดึงราคาตลาดปัจจุบัน (หุ้นไทยให้ลงท้ายด้วย .BK เช่น PTT.BK | หุ้น/ETF อเมริกาใช้ชื่อย่อได้เลย เช่น VOO, SCHD)")

# จัดเตรียมช่อง Input สำหรับสินทรัพย์ 4 ตัวแรกเป็นตัวอย่าง
input_assets = []
default_assets = [("VOO", 15, 420.0), ("SCHD", 40, 75.0), ("PTT.BK", 1500, 34.0), ("", 0, 0.0)]

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
        qty = cols[1].number_input(f"Qty {i+1}", value=def_qty, min_value=0, key=f"qty_{i}")
    with cols[2]:
        cost = cols[2].number_input(f"Cost {i+1}", value=def_cost, min_value=0.0, key=f"cost_{i}")
    with cols[3]:
        if sym:
            market_type = "🇹🇭 ไทย (THB)" if ".BK" in sym else "🇺🇸 อเมริกา (USD)"
            cols[3].markdown(f"<br><span style='color:gray;'>{market_type}</span>", unsafe_allow_html=True)
            input_assets.append({"symbol": sym, "qty": qty, "cost": cost, "is_th": ".BK" in sym})
        else:
            cols[3].write("")

# --- 5. CALCULATION LOGIC (PORTFOLIO & TAXES) ---
portfolio_details = []
total_stock_value_thb = 0
total_cost_thb = 0

if input_assets:
    with st.spinner("🏰 กำลังเชื่อมต่อฐานข้อมูลราคาเรียลไทม์..."):
        for item in input_assets:
            if item["qty"] <= 0:
                continue
                
            ticker = yf.Ticker(item["symbol"])
            try:
                live_price = ticker.fast_info['last_price']
            except:
                live_price = item["cost"]
                st.error(f"ไม่สามารถดึงข้อมูลของ: {item['symbol']} ได้ กรุณาตรวจสอบชื่อย่อ")

            # แยกคำนวณมูลค่าตามตลาดและค่าเงิน
            if item["is_th"]:
                current_val = live_price * item["qty"]
                cost_val = item["cost"] * item["qty"]
            else:
                current_val = (live_price * item["qty"]) * usd_thb
                cost_val = (item["cost"] * item["qty"]) * usd_thb

            p_l = current_val - cost_val
            p_l_pct = (p_l / cost_val) * 100 if cost_val > 0 else 0

            total_stock_value_thb += current_val
            total_cost_thb += cost_val

            portfolio_details.append({
                "สินทรัพย์": item["symbol"],
                "จำนวน": item["qty"],
                "ต้นทุนเฉลี่ย": f"{item['cost']:,.2f}",
                "ราคาปัจจุบัน": f"{live_price:,.2f}",
                "มูลค่ารวม (บาท)": round(current_val, 2),
                "กำไร/ขาดทุน (บาท)": round(p_l, 2),
                "กำไร/ขาดทุน (%)": f"{p_l_pct:+.2f}%"
            })

# สรุปความมั่งคั่งสุทธิปัจจุบัน
net_worth = total_stock_value_thb + cash_thb
# คำนวณเป้าหมายอิงจาก Safe Withdrawal Rate ที่เลือก (เช่น 4% Rule คือ คูณ 25 | ถ้า 3.3% คือ คูณ 30)
fire_target = (desired_monthly_spend * 12) / safe_withdrawal_rate

# --- 6. UI DISPLAY: FINANCIAL METRICS ---
st.markdown("---")
st.header("📊 ภาพรวมป้อมปราการความมั่งคั่ง (Wealth Summary)")

m1, m2, m3, m4 = st.columns(4)
m1.metric("ความมั่งคั่งสุทธิ (Net Worth)", f"{net_worth:,.0f} ฿")
m2.metric("เป้าหมาย FortressFIRE", f"{fire_target:,.0f} ฿")

total_pl = total_stock_value_thb - total_cost_thb
total_pl_pct = (total_pl / total_cost_thb) * 100 if total_cost_thb > 0 else 0
m3.metric("ผลกำไร/ขาดทุนพอร์ตรวม", f"{total_pl:,.0f} ฿", f"{total_pl_pct:+.2f}%")
m4.metric("เรทอัตราแลกเปลี่ยนปัจจุบัน", f"{usd_thb:.2f} ฿/USD")

# แถบแสดงความคืบหน้า (Progress Bar)
progress = min(net_worth / fire_target, 1.0)
st.write(f"**🛡️ ระดับการป้องกันและขยายตัวของป้อมปราการ: {progress*100:.2f}% ของเป้าหมาย**")
st.progress(progress)

# แสดงตารางแสดงรายละเอียดพอร์ต
if portfolio_details:
    st.subheader("📋 บัญชีสรุปสินทรัพย์ในพอร์ต")
    st.dataframe(pd.DataFrame(portfolio_details), use_container_width=True, hide_index=True)

# --- 7. FUTURE PROJECTION (SIMULATION) ---
st.markdown("---")
st.header("⏳ การจำลองการเติบโตและการเดินทางสู่เป้าหมาย")

# คำนวณ Real Return (หักเงินเฟ้อ) แบบทบต้นรายเดือนเพื่อความแม่นยำ
real_annual_return = ((1 + expected_annual_return) / (1 + inflation_rate)) - 1
monthly_rate = (1 + real_annual_return)**(1/12) - 1

history = []
balance = net_worth
months = 0
reached_fire = False
target_month = 0

for year in range(0, 41): # จำลองล่วงหน้า 40 ปี
    history.append({"Year": year, "Balance": balance})
    
    # วนลูป 12 เดือนภายในปีนั้นๆ เพื่อคิดดอกเบี้ยทบต้นรายเดือนและการออมเพิ่ม
    for m in range(12):
        if balance >= fire_target and not reached_fire:
            reached_fire = True
            target_month = months
        balance = (balance + monthly_invest) * (1 + monthly_rate)
        months += 1

df_history = pd.DataFrame(history)

# วาดกราฟ Interactive ด้วย Plotly
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_history['Year'], 
    y=df_history['Balance'], 
    name='พอร์ตสะสม (Real Value)',
    line=dict(color='#0f172a', width=3.5) # สี Slate Dark สไตล์ป้อมปราการ มินิมอล
))
fig.add_hline(y=fire_target, line_dash="dash", line_color="#ef4444", line_width=2, annotation_text="FIRE Target Zone")
fig.update_layout(
    title="เส้นทางการเติบโตของสินทรัพย์ (คำนวณหักเงินเฟ้อแล้ว)",
    xaxis_title="จำนวนปีข้างหน้า",
    yaxis_title="มูลค่าเงิน (บาท)",
    hovermode="x unified",
    plot_bgcolor="white"
)
st.plotly_chart(fig, use_container_width=True)

# สรุปผลลัพธ์ของเป้าหมาย
if reached_fire:
    years_needed = target_month // 12
    months_needed = target_month % 12
    st.success(f"🎉 **ความสำเร็จของ FortressFIRE:** คุณจะบรรลุอิสรภาพทางการเงินในอีก **{years_needed} ปี {months_needed} เดือน** (ประมาณปี ค.ศ. {datetime.now().year + years_needed})")
else:
    st.warning("⚠️ **คำแนะนำจาก Fortress:** เงินออมหรือผลตอบแทนปัจจุบันอาจต้องใช้เวลามากกว่า 40 ปีในการสร้างฐานป้อมปราการ ลองพิจารณาปรับเพิ่มยอดออมรายเดือนหรือปรับสัดส่วนสินทรัพย์เพื่อเพิ่มผลตอบแทน")
