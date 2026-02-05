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
# 2. 디자인 (CSS) - 그대로 유지
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
# 3. 데이터 엔진 (FMP API로 교체 완료!) 🚀
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def get_fmp_data(ticker):
    # [비밀 금고에서 키 꺼내기]
    try:
        api_key = st.secrets["FMP_API_KEY"]
    except:
        st.error("⚠️ Secrets에 'FMP_API_KEY'가 없습니다. 설정을 확인해주세요.")
        return None

    try:
        # 1. 프로필 (가격, 회사정보)
        url_profile = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={api_key}"
        res_profile = requests.get(url_profile).json()
        
        # 2. 핵심 지표 (ROE, PE, 마진 등 - TTM 기준)
        url_ratios = f"https://financialmodelingprep.com/api/v3/ratios-ttm/{ticker}?apikey={api_key}"
        res_ratios = requests.get(url_ratios).json()

        # 3. 성장성 (매출 성장)
        url_growth = f"https://financialmodelingprep.com/api/v3/financial-growth/{ticker}?limit=1&apikey={api_key}"
        res_growth = requests.get(url_growth).json()

        if not res_profile: return None

        # 데이터 합치기
        data = {
            "profile": res_profile[0],
            "ratios": res_ratios[0] if res_ratios else {},
            "growth": res_growth[0] if res_growth else {}
        }
        return data

    except Exception as e:
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
st.markdown("Analysis powered by **FMP (Financial Modeling Prep)**.")
st.divider()

ticker = st.text_input("ENTER TICKER (e.g., AAPL, NVDA, TSLA)", value="AAPL").strip().upper()

if ticker:
    with st.spinner(f"Analyzing {ticker} Financials..."):
        data = get_fmp_data(ticker)

        if not data:
            st.error(f"⚠️ Could not find data for '{ticker}'. Check the ticker symbol.")
        else:
            profile = data['profile']
            ratios = data['ratios']
            growth_data = data['growth']

            # 데이터 추출 (없으면 0 처리)
            price = profile.get('price', 0)
            roe = ratios.get('returnOnEquityTTM', 0) * 100
            margin = ratios.get('netProfitMarginTTM', 0) * 100
            growth = growth_data.get('revenueGrowth', 0) * 100
            pe = ratios.get('priceEarningsRatioTTM', 0)
            eps = ratios.get('netIncomePerShareTTM', 0) # EPS 대신 순이익/주식수
            if eps == 0: eps = profile.get('lastDiv', 0) # 혹시 없으면 배당으로 대체하거나 0 (FMP는 구조가 조금 다름)
            
            # FMP는 EPS를 profile이나 income statement에서 가져오는게 정확함. 
            # 여기서는 편의상 profile의 price / PE로 역산하거나 0으로 둠.
            if pe > 0: eps_calc = price / pe
            else: eps_calc = 0
            
            pb = ratios.get('priceToBookRatioTTM', 0)

            # 결과 헤더
            st.subheader(f"📊 Analysis Result: {profile.get('companyName', ticker)}")
            st.caption(f"Current Price: ${price:,.2f} | Sector: {profile.get('sector', '-')}")

            # [10대 맞춤형 아이콘 & 설명]
            c1, c2, c3 = st.columns(3)
            
            # 1. ROE (성적표)
            roe_status = "good" if roe >= 15 else ("okay" if roe >= 10 else "bad")
            roe_icon = "🏆" if roe_status == "good" else ("🤔" if roe_status == "okay" else "💤")
            create_card(c1, "ROE (Score)", f"{roe:.1f}", "%", roe_status, 
                        "**The Report Card.** Over 15% is an A+! Shows how smart they are with money.", roe_icon)

            # 2. Margin (순이익)
            margin_status = "good" if margin >= 20 else ("okay" if margin >= 10 else "bad")
            margin_icon = "💰" if margin_status == "good" else ("🪙" if margin_status == "okay" else "💸")
            create_card(c2, "Net Margin", f"{margin:.1f}", "%", margin_status, 
                        "**Pure Cash.** How much money they actually keep in their pocket.", margin_icon)

            # 3. Growth (성장)
            growth_status = "good" if growth >= 10 else ("okay" if growth > 0 else "bad")
            growth_icon = "🚀" if growth_status == "good" else ("🚶" if growth_status == "okay" else "🐌")
            create_card(c3, "Growth (YoY)", f"{growth:.1f}", "%", growth_status, 
                        "**Is it getting bigger?** We want to see this Rocket go UP!", growth_icon)

            c4, c5, c6 = st.columns(3)
            
            # 4. P/E (가격)
            if pe <= 0: pe_status = "bad"; pe_disp = "Loss"
            elif pe > 50: pe_status = "okay"; pe_disp = f"{pe:.1f}x"
            else: pe_status = "good"; pe_disp = f"{pe:.1f}x"
            
            pe_icon = "🏷️" if pe_status == "good" else "💎" 
            create_card(c4, "P/E Ratio", pe_disp, "", pe_status, 
                        "**Is it on Sale?** Lower number = Cheaper price tag.", pe_icon)
            
            # 5. EPS (주당 순이익) - 추정치
            eps_status = "good" if eps_calc > 0 else "bad"
            eps_icon = "🍕" if eps_status == "good" else "🦴"
            create_card(c5, "EPS (Est)", f"${eps_calc:.2f}", "", eps_status, 
                        "**Your Slice.** Approximate profit per single stock ticket.", eps_icon)

            # 6. P/B (자산가치)
            pb_status = "good" if pb < 3 else "okay"
            pb_icon = "🎁" if pb_status == "good" else "📦"
            create_card(c6, "P/B Ratio", f"{pb:.1f}", "x", pb_status, 
                        "**Bargain Hunt.** Close to 1.0 means you buy it for the raw material price.", pb_icon)
            
# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>Built by <b>Daniel Park</b> | Powered by WEMAKEMOVES AI</div>", unsafe_allow_html=True)
