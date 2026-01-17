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
st.markdown("""
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
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. 데이터 가져오기 (보안 강화 버전)
# ---------------------------------------------------------
@st.cache_data(ttl=3600) 
def get_fmp_data(ticker):
    # [보안 모드] 비밀 금고에서 키를 안전하게 꺼내옵니다.
    # 만약 secrets 설정이 안 되어 있으면 에러를 방지하기 위해 None을 반환
    if "FMP_API_KEY" in st.secrets["general"]:
        api_key = st.secrets["general"]["FMP_API_KEY"]
    else:
        st.error("⚠️ API Key가 설정되지 않았습니다. Secrets를 확인해주세요.")
        return None
    
    try:
        # 키를 변수에 담아서 넣기 때문에 따옴표 충돌이 발생하지 않습니다.
        url_ratios = f"https://financialmodelingprep.com/api/v3/ratios-ttm/{ticker}?apikey={api_key}"
        r_ratios = requests.get(url_ratios).json()
        
        url_price = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={api_key}"
        r_price = requests.get(url_price).json()

        if not r_ratios or not r_price:
            return None
            
        return {"ratios": r_ratios[0], "price": r_price[0]}
        
    except Exception:
        return None

# ---------------------------------------------------------
# 4. 카드 생성 함수
# ---------------------------------------------------------
def create_card(col, title, value, unit, status, description):
    if status == "good": color_class = "good"; icon = "🟢"
    elif status == "okay": color_class = "okay"; icon = "🟡"
    else: color_class = "bad"; icon = "🔴"
    
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">{icon} {title}</div>
            <div class="metric-value {color_class}">
                {value}{unit}
            </div>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("Meaning"):
            st.write(description)

# ---------------------------------------------------------
# 5. 메인 로직
# ---------------------------------------------------------
st.title("🧭 Teen Stock Compass: Pro Dashboard")
st.markdown("Powered by **Financial Modeling Prep (Official Data)**.")
st.divider()

ticker = st.text_input("ENTER TICKER (e.g., AAPL, TSLA, NVDA)", value="AAPL").upper()

if ticker:
    with st.spinner(f"Fetching official financial data for {ticker}..."):
        data = get_fmp_data(ticker)

        if not data:
            st.error("⚠️ Invalid Ticker or Daily Limit Reached. Please check the symbol.")
        else:
            ratios = data['ratios']
            price_info = data['price']

            # --- 데이터 추출 ---
            price = price_info.get('price', 0)
            roe = ratios.get('returnOnEquityTTM', 0) * 100
            margin = ratios.get('netProfitMarginTTM', 0) * 100
            growth = 0 
            debt = ratios.get('debtEquityRatioTTM', 0) * 100
            pe = ratios.get('priceEarningsRatioTTM', 0)

            # --- 결과 출력 ---
            st.subheader(f"📊 Analysis Result: {ticker}")
            st.caption(f"Current Price: ${price:,.2f}")

            # Row 1
            c1, c2, c3 = st.columns(3)
            roe_status = "good" if roe >= 15 else ("okay" if roe >= 10 else "bad")
            create_card(c1, "ROE (Efficiency)", f"{roe:.1f}", "%", roe_status,
                        "**Return on Equity:** How efficiently the company uses money.")

            margin_status = "good" if margin >= 20 else ("okay" if margin >= 10 else "bad")
            create_card(c2, "Net Margin (Profit)", f"{margin:.1f}", "%", margin_status,
                        "**Net Profit Margin:** Pure profit percentage.")

            create_card(c3, "Growth Data", "N/A", "", "okay", "Growth data requires premium tier.")

            # Row 2
            c4, c5 = st.columns(2)
            debt_status = "good" if debt < 100 else ("okay" if debt < 200 else "bad")
            create_card(c4, "Debt Ratio (Safety)", f"{debt:.1f}", "%", debt_status,
                        "**Debt-to-Equity:** Lower is safer. Over 200% is risky.")

            if pe <= 0: pe_status = "bad"; pe_disp = "Loss"
            elif pe > 50: pe_status = "okay"; pe_disp = f"{pe:.1f}x"
            else: pe_status = "good"; pe_disp = f"{pe:.1f}x"
            create_card(c5, "P/E Ratio (Valuation)", pe_disp, "", pe_status,
                        "**Price-to-Earnings:** Lower P/E often means undervalued.")

# ---------------------------------------------------------
# 6. Footer
# ---------------------------------------------------------
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>Built by <b>Daniel Park</b></div>", unsafe_allow_html=True)
