import streamlit as st
import requests
import pandas as pd

# ---------------------------------------------------------
# 1. 페이지 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="WEMAKEMOVES Finance",
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
        font-size: 1.0rem;
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
# 3. 데이터 엔진 (Finnhub: 공식 API, 안정성 최고 🏆)
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def get_finnhub_data(ticker):
    # 키 확인
    if "FINNHUB_KEY" not in st.secrets:
        st.error("🚨 Secrets에 'FINNHUB_KEY'가 없습니다.")
        return None
    
    api_key = st.secrets["FINNHUB_KEY"]

    try:
        # 1. 기본 재무 지표 (Metric) - 무료로 빵빵하게 줍니다
        url_metric = f"https://finnhub.io/api/v1/stock/metric?symbol={ticker}&metric=all&token={api_key}"
        res_metric = requests.get(url_metric).json()
        
        # 2. 현재 가격 (Quote)
        url_quote = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={api_key}"
        res_quote = requests.get(url_quote).json()
        
        # 3. 회사 프로필 (이름, 산업)
        url_profile = f"https://finnhub.io/api/v1/stock/profile2?symbol={ticker}&token={api_key}"
        res_profile = requests.get(url_profile).json()

        if not res_metric.get('metric'):
            st.warning(f"⚠️ '{ticker}' 데이터를 찾을 수 없습니다.")
            return None

        # 데이터 정리
        metrics = res_metric['metric']
        
        data = {
            "name": res_profile.get('name', ticker),
            "sector": res_profile.get('finnhubIndustry', 'Unknown'),
            "price": res_quote.get('c', 0), # c = Current price
            "roe": metrics.get('roeTTM', 0),
            "margin": metrics.get('netProfitMarginTTM', 0),
            "growth": metrics.get('revenueGrowthTTMYoy', 0), # 연간 매출 성장률
            "pe": metrics.get('peTTM', 0),
            "eps": metrics.get('epsTTM', 0),
            "pb": metrics.get('pbAnnual', 0) # P/B 비율
        }
        
        return data

    except Exception as e:
        st.error(f"🚨 시스템 에러: {e}") 
        return None

# ---------------------------------------------------------
# 4. 카드 UI 생성 함수
# ---------------------------------------------------------
def create_card(col, title, value, unit, status, description, custom_icon=None):
    if status == "good": color_class = "good"
    elif status == "okay": color_class = "okay"
    else: color_class = "bad"
    
    if custom_icon:
        icon = custom_icon
    else:
        if status == "good": icon = "🔥"
        elif status == "okay": icon = "🐣"
        else: icon = "☔"
    
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">{icon} {title}</div>
            <div class="metric-value {color_class}">{value}{unit}</div>
        </div>""", unsafe_allow_html=True)
        with st.expander("What is this?"): 
            st.write(description)

# ---------------------------------------------------------
# 5. 메인 화면 로직
# ---------------------------------------------------------
st.title("🧭 WEMAKEMOVES Financials")
st.markdown("Analysis powered by **Finnhub (Institutional Grade Data)**.")
st.divider()

ticker = st.text_input("ENTER TICKER (e.g., AAPL, NVDA, TSLA)", value="AAPL").strip().upper()

if ticker:
    with st.spinner(f"Fetching {ticker} via Finnhub..."):
        data = get_finnhub_data(ticker)

        if data:
            # 결과 헤더
            st.subheader(f"📊 Analysis Result: {data['name']}")
            st.caption(f"Current Price: ${data['price']:,.2f} | Sector: {data['sector']}")

            # 데이터 추출
            roe = data['roe']
            margin = data['margin']
            growth = data['growth']
            pe = data['pe']
            eps = data['eps']
            pb = data['pb']

            # [10대 맞춤형 아이콘 & 설명]
            c1, c2, c3 = st.columns(3)
            
            # 1. ROE
            roe_status = "good" if roe >= 15 else ("okay" if roe >= 10 else "bad")
            roe_icon = "🏆" if roe_status == "good" else ("🤔" if roe_status == "okay" else "💤")
            create_card(c1, "ROE (Score)", f"{roe:.1f}", "%", roe_status, 
                        "**The Report Card.** Over 15% is an A+!", roe_icon)

            # 2. Margin
            margin_status = "good" if margin >= 20 else ("okay" if margin >= 10 else "bad")
            margin_icon = "💰" if margin_status == "good" else ("🪙" if margin_status == "okay" else "💸")
            create_card(c2, "Net Margin", f"{margin:.1f}", "%", margin_status, 
                        "**Pure Cash.** Profit percentage.", margin_icon)

            # 3. Growth
            growth_status = "good" if growth >= 10 else ("okay" if growth > 0 else "bad")
            growth_icon = "🚀" if growth_status == "good" else ("🚶" if growth_status == "okay" else "🐌")
            create_card(c3, "Growth (YoY)", f"{growth:.1f}", "%", growth_status, 
                        "**Rocket Speed.** Revenue growth rate.", growth_icon)

            c4, c5, c6 = st.columns(3)
            
            # 4. P/E
            if pe is None: pe = 0
            if pe <= 0: pe_status = "bad"; pe_disp = "Loss"
            elif pe > 50: pe_status = "okay"; pe_disp = f"{pe:.1f}x"
            else: pe_status = "good"; pe_disp = f"{pe:.1f}x"
            pe_icon = "🏷️" if pe_status == "good" else "💎" 
            create_card(c4, "P/E Ratio", pe_disp, "", pe_status, 
                        "**Price Tag.** Lower is usually cheaper.", pe_icon)
            
            # 5. EPS
            eps_status = "good" if eps > 0 else "bad"
            eps_icon = "🍕" if eps_status == "good" else "🦴"
            create_card(c5, "EPS", f"${eps:.2f}", "", eps_status, 
                        "**Your Slice.** Profit per share.", eps_icon)

            # 6. P/B
            pb_status = "good" if pb < 3 else "okay"
            pb_icon = "🎁" if pb_status == "good" else "📦"
            create_card(c6, "P/B Ratio", f"{pb:.1f}", "x", pb_status, 
                        "**Bargain Hunt.** Close to 1.0 is value.", pb_icon)
            
# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>Built by <b>Daniel Park</b> | Powered by WEMAKEMOVES AI</div>", unsafe_allow_html=True)
