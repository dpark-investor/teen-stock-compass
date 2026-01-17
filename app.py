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
# 2. 디자인 (CSS) - 다크모드 카드 디자인
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
# 3. 데이터 가져오기 (FMP 정식 API 사용)
# ---------------------------------------------------------
@st.cache_data(ttl=3600) 
def get_fmp_data(ticker):
    # [핵심] 키를 코드에 직접 넣어서 연결 오류를 원천 차단했습니다.
    api_key = "7HHpAIcOk53R1j3dNxcPHYjDIbmfmhaR"
    
    try:
        # 1. 재무 비율 데이터 요청
        url_ratios = f"https://financialmodelingprep.com/api/v3/ratios-ttm/{ticker}?apikey={api_key}"
        response_ratios = requests.get(url_ratios)
        r_ratios = response_ratios.json()
        
        # 2. 실시간 주가 데이터 요청
        url_price = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={api_key}"
        response_price = requests.get(url_price)
        r_price = response_price.json()

        # 데이터가 비어있거나 에러 메시지가 왔을 경우 처리
        if not r_ratios or not r_price:
            return None
        
        # 간혹 API가 빈 리스트 []를 줄 때가 있어 체크
        if isinstance(r_ratios, list) and len(r_ratios) > 0:
            ratio_data = r_ratios[0]
        else:
            return None

        if isinstance(r_price, list) and len(r_price) > 0:
            price_data = r_price[0]
        else:
            return None
            
        return {"ratios": ratio_data, "price": price_data}
        
    except Exception as e:
        return None

# ---------------------------------------------------------
# 4. 카드 생성 헬퍼 함수
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
# 5. 메인 화면 로직
# ---------------------------------------------------------
st.title("🧭 Teen Stock Compass: Pro Dashboard")
st.markdown("Professional Grade Analysis powered by **FMP Official Data**.")
st.divider()

# 사용자 입력 (기본값 AAPL)
ticker = st.text_input("ENTER TICKER (e.g., AAPL, TSLA, NVDA)", value="AAPL").upper()

if ticker:
    with st.spinner(f"Fetching official data for {ticker}..."):
        data = get_fmp_data(ticker)

        if not data:
            st.error(f"⚠️ Could not find data for '{ticker}'. Please check the symbol.")
        else:
            ratios = data['ratios']
            price_info = data['price']

            # --- 데이터 추출 및 안전한 변환 ---
            try:
                # 1. 주가
                price = price_info.get('price', 0)
                
                # 2. ROE (자기자본이익률)
                roe = ratios.get('returnOnEquityTTM')
                roe = roe * 100 if roe is not None else 0
                
                # 3. 순이익률
                margin = ratios.get('netProfitMarginTTM')
                margin = margin * 100 if margin is not None else 0
                
                # 4. 부채비율
                debt = ratios.get('debtEquityRatioTTM')
                debt = debt * 100 if debt is not None else 0
                
                # 5. PER (주가수익비율)
                pe = ratios.get('priceEarningsRatioTTM')
                pe = pe if pe is not None else 0

                # --- 화면 출력 ---
                st.subheader(f"📊 Analysis Result: {ticker}")
                st.caption(f"Current Price: ${price:,.2f}")

                # 첫 번째 줄 (효율성, 수익성, 성장성 안내)
                c1, c2, c3 = st.columns(3)
                
                roe_status = "good" if roe >= 15 else ("okay" if roe >= 10 else "bad")
                create_card(c1, "ROE (Efficiency)", f"{roe:.1f}", "%", roe_status,
                            "**Return on Equity:** How efficiently the company uses money. >15% is excellent.")

                margin_status = "good" if margin >= 20 else ("okay" if margin >= 10 else "bad")
                create_card(c2, "Net Margin (Profit)", f"{margin:.1f}", "%", margin_status,
                            "**Net Profit Margin:** Pure profit percentage.")

                create_card(c3, "Growth Data", "N/A", "", "okay",
                            "Growth metrics require Premium Plan. (Check ROE instead)")

                # 두 번째 줄 (안전성, 저평가 여부)
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
                st.error("Data was received but an error occurred while displaying it.")

# ---------------------------------------------------------
# 6. 푸터
# ---------------------------------------------------------
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>Built by <b>Daniel Park</b></div>", unsafe_allow_html=True)
