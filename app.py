import streamlit as st
import requests
import time

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
# 3. 데이터 가져오기 (Direct JSON API)
# ---------------------------------------------------------
@st.cache_data(ttl=60) # 1분 캐시
def get_data_from_api(ticker):
    # 야후 파이낸스 내부 API 주소 (뒷문)
    url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=summaryDetail,financialData,defaultKeyStatistics,price"
    
    # 브라우저인 척 위장하는 헤더
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        
        # 데이터가 없거나 차단당했을 경우
        if response.status_code != 200:
            return None
            
        # JSON 데이터 열기
        data = response.json()
        result = data['quoteSummary']['result'][0]
        
        return result
        
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
st.markdown("Analyze financial health using **Direct API Connection**.")
st.divider()

ticker = st.text_input("ENTER TICKER (e.g., AAPL, NVDA, TSLA)", value="AAPL").upper()

if ticker:
    with st.spinner(f"Connecting to Server for {ticker}..."):
        raw_data = get_data_from_api(ticker)

        if not raw_data:
            st.error(f"⚠️ Connection Failed for '{ticker}'. The free data server is busy. Please wait 1 minute and try again.")
        else:
            # --- 데이터 추출 (복잡한 JSON 구조 파해치기) ---
            try:
                # 1. 가격
                price = raw_data['price']['regularMarketPrice']['raw']
                
                # 2. ROE
                roe = raw_data['financialData'].get('returnOnEquity', {}).get('raw', 0) * 100
                
                # 3. Profit Margin
                margin = raw_data['defaultKeyStatistics'].get('profitMargins', {}).get('raw', 0) * 100
                # 만약 위에서 못 찾으면 financialData에서 찾기
                if margin == 0:
                    margin = raw_data['financialData'].get('profitMargins', {}).get('raw', 0) * 100
                
                # 4. Revenue Growth
                growth = raw_data['financialData'].get('revenueGrowth', {}).get('raw', 0) * 100
                
                # 5. Debt to Equity
                debt = raw_data['financialData'].get('debtToEquity', {}).get('raw', 0)
                
                # 6. PER
                pe = raw_data['summaryDetail'].get('trailingPE', {}).get('raw', 0)

                # --- 결과 출력 ---
                st.subheader(f"📊 Analysis Result: {ticker}")
                st.caption(f"Current Price: ${price:,.2f}")

                # Row 1
                c1, c2, c3 = st.columns(3)
                
                roe_status = "good" if roe >= 15 else ("okay" if roe >= 10 else "bad")
                create_card(c1, "ROE (Efficiency)", f"{roe:.1f}", "%", roe_status,
                            "**Return on Equity:** How efficiently the company uses money. >15% is excellent.")

                margin_status = "good" if margin >= 20 else ("okay" if margin >= 10 else "bad")
                create_card(c2, "Net Margin (Profit)", f"{margin:.1f}", "%", margin_status,
                            "**Net Profit Margin:** Pure profit percentage.")

                growth_status = "good" if growth >= 10 else ("okay" if growth > 0 else "bad")
                create_card(c3, "Growth (YoY)", f"{growth:.1f}", "%", growth_status,
                            "**Revenue Growth:** Is the company expanding?")

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
            
            except Exception as e:
                st.error("Data received but incomplete. Try a different company.")

# ---------------------------------------------------------
# 6. Footer
# ---------------------------------------------------------
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>Built by <b>Daniel Park</b></div>", unsafe_allow_html=True)
