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
# 3. 데이터 가져오기 (Source: Financial Modeling Prep)
# ---------------------------------------------------------
# FMP는 하루 250회 무료입니다. 재무제표 데이터가 매우 정확합니다.
@st.cache_data(ttl=3600) # 1시간 동안 저장 (데이터 절약)
def get_fmp_data(ticker):
    api_key = st.secrets["general"]["FMP_API_KEY"]
    
    try:
        # 1. 핵심 재무 비율 (ROE, Margin, PER, Debt 등 다 있음)
        url_ratios = f"https://financialmodelingprep.com/api/v3/ratios-ttm/{ticker}?apikey="7HHpAIcOk53R1j3dNxcPHYjDIbmfmhaR"
        r_ratios = requests.get(url_ratios).json()
        
        # 2. 실시간 주가
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

            # --- 데이터 추출 (FMP는 이름이 아주 직관적입니다) ---
            
            # 1. Price
            price = price_info.get('price', 0)
            
            # 2. ROE
            roe = ratios.get('returnOnEquityTTM', 0) * 100
            
            # 3. Net Profit Margin
            margin = ratios.get('netProfitMarginTTM', 0) * 100
            
            # 4. Revenue Growth (이건 ratios에 없어서 계산하거나, 여기선 FMP 특성상 PER로 대체하거나 추가 호출 필요. 
            # 일단 안정성을 위해 가장 중요한 'Current Ratio(유동비율)'이나 다른 걸 보여주기도 하지만, 
            # 여기서는 'Gross Profit Margin' 등 있는 데이터로 대체하거나 0으로 둠)
            # *팁: 성장률은 별도 호출이 필요해서, 무료 한도를 아끼기 위해 '자산회전율' 등으로 대체하거나 생략 가능.
            # 여기선 일단 0으로 둡니다. (추가 호출 시 한도 2배 소모됨)
            growth = 0 
            
            # 5. Debt to Equity
            debt = ratios.get('debtEquityRatioTTM', 0) * 100
            
            # 6. PER
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

            # 성장률 대신 배당수익률(Dividend Yield)이나 유동비율을 보여주는 게 FMP 무료버전 효율상 좋습니다.
            # 여기선 일단 UI 유지를 위해 칸만 둡니다.
            create_card(c3, "Growth Data", "N/A", "", "okay",
                        "Growth data requires premium tier in this version.")

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
