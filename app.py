import streamlit as st
import requests

# ---------------------------------------------------------
# 1. 페이지 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="Teen Stock Compass Pro",
    page_icon="🧭",
    layout="wide"
)

# ---------------------------------------------------------
# 2. 디자인 (CSS)
# ---------------------------------------------------------
st.markdown(
    """
<style>
    .metric-card {
        background-color: #1E1E1E;
        border: 1px solid #333;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    }
    .metric-title {
        color: #AAAAAA;
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
    }
    .metric-value {
        color: #FFFFFF;
        font-size: 2.2rem;
        font-weight: bold;
    }
    .good { color: #29B094 !important; }
    .okay { color: #FFC107 !important; }
    .bad { color: #FF4B4B !important; }
</style>
""",
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# 3. 유틸 함수 (안전한 숫자 변환)
# ---------------------------------------------------------
def to_float(x, default=0.0) -> float:
    try:
        if x is None:
            return default
        return float(x)
    except (TypeError, ValueError):
        return default

# ---------------------------------------------------------
# 4. 데이터 가져오기 (키 내장형)
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def get_fmp_data(ticker: str):
    # [수정] 아버님의 키를 여기에 직접 넣었습니다. (괄호 에러 없음)
    api_key = "7HHpAIcOk53R1j3dNxcPHYjDIbmfmhaR"

    try:
        # Ratio (재무 비율)
        url_ratios = f"https://financialmodelingprep.com/api/v3/ratios-ttm/{ticker}?apikey={api_key}"
        resp_ratios = requests.get(url_ratios, timeout=10)
        
        # Price Quote (주가)
        url_price = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={api_key}"
        resp_price = requests.get(url_price, timeout=10)

        if resp_ratios.status_code != 200 or resp_price.status_code != 200:
            return None

        r_ratios = resp_ratios.json()
        r_price = resp_price.json()

        if not r_ratios or (isinstance(r_ratios, dict) and "Error Message" in r_ratios):
             return None
        if not r_price or (isinstance(r_price, dict) and "Error Message" in r_price):
             return None

        final_ratios = r_ratios[0] if isinstance(r_ratios, list) else r_ratios
        final_price = r_price[0] if isinstance(r_price, list) else r_price

        return {"ratios": final_ratios, "price": final_price}

    except Exception:
        return None

# ---------------------------------------------------------
# 5. 카드 생성 함수
# ---------------------------------------------------------
def create_card(col, title, value, unit, status, description):
    if status == "good": color_class = "good"; icon = "🟢"
    elif status == "okay": color_class = "okay"; icon = "🟡"
    else: color_class = "bad"; icon = "🔴"

    with col:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-title">{icon} {title}</div>
            <div class="metric-value {color_class}">
                {value}{unit}
            </div>
        </div>
        """,
            unsafe_allow_html=True
        )
        with st.expander("Meaning"):
            st.write(description)

# ---------------------------------------------------------
# 6. 메인 UI
# ---------------------------------------------------------
st.title("🧭 Teen Stock Compass: Pro Dashboard")
st.markdown("Powered by **Financial Modeling Prep (Official Data)**.")
st.divider()

ticker = st.text_input("ENTER TICKER (e.g., AAPL, TSLA, NVDA)", value="AAPL").strip().upper()

if ticker:
    with st.spinner(f"Fetching official financial data for {ticker}..."):
        data = get_fmp_data(ticker)

    if not data:
        st.error(f"⚠️ Could not find data for '{ticker}'. (Try 'AAPL' to check connection)")
    else:
        ratios = data["ratios"]
        price_info = data["price"]

        # --- [수정 완료] 괄호 닫기 완벽하게 처리됨 ---
        price = to_float(price_info.get("price"), default=0.0)
        roe = to_float(ratios.get("returnOnEquityTTM"), default=0.0) * 100
        margin = to_float(ratios.get("netProfitMarginTTM"), default=0.0) * 100
        growth = None
        debt = to_float(ratios.get("debtEquityRatioTTM"), default=0.0) * 100
        pe = to_float(ratios.get("priceEarningsRatioTTM"), default=-1.0)

        # --- 결과 출력 ---
        st.subheader(f"📊 Analysis Result: {ticker}")
        st.caption(f"Current Price: ${price:,.2f}")

        # Row 1
        c1, c2, c3 = st.columns(3)

        roe_status = "good" if roe >= 15 else ("okay" if roe >= 10 else "bad")
        create_card(c1, "ROE (Efficiency)", f"{roe:.1f}", "%", roe_status,
            "**Return on Equity:** How efficiently the company uses shareholders' money.")

        margin_status = "good" if margin >= 20 else ("okay" if margin >= 10 else "bad")
        create_card(c2, "Net Margin (Profit)", f"{margin:.1f}", "%", margin_status,
            "**Net Profit Margin:** How much pure profit the company keeps from sales.")

        create_card(c3, "Growth Data", "N/A", "", "okay",
            "Growth data requires a premium endpoint.")

        # Row 2
        c4, c5 = st.columns(2)

        debt_status = "good" if debt < 100 else ("okay" if debt < 200 else "bad")
        create_card(c4, "Debt Ratio (Safety)", f"{debt:.1f}", "%", debt_status,
            "**Debt-to-Equity:** Lower is safer. Over 200% is generally considered risky.")

        if pe <= 0: pe_status = "bad"; pe_disp = "Loss"
        elif pe > 50: pe_status = "okay"; pe_disp = f"{pe:.1f}x"
        else: pe_status = "good"; pe_disp = f"{pe:.1f}x"

        create_card(c5, "P/E Ratio (Valuation)", pe_disp, "", pe_status,
            "**Price-to-Earnings:** Lower P/E can mean cheaper, but compare within the same industry.")

# ---------------------------------------------------------
# 7. Footer
# ---------------------------------------------------------
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>Built by <b>Daniel Park</b></div>", unsafe_allow_html=True)
