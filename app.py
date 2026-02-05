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
# 3. 데이터 엔진 (MacGyver 버전: 원재료로 직접 계산 🛠️)
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def get_fmp_data(ticker):
    # [진단] 비밀 금고 확인
    if "FMP_API_KEY" not in st.secrets:
        st.error("🚨 Secrets(비밀금고)에 'FMP_API_KEY'가 없습니다.")
        return None
    
    api_key = st.secrets["FMP_API_KEY"]

    try:
        # 1. 주가 정보 (Quote Endpoint는 아직 무료!)
        url_quote = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={api_key}"
        res_quote = requests.get(url_quote).json()
        
        if not res_quote:
            st.warning(f"⚠️ '{ticker}' 주가 정보를 찾을 수 없습니다.")
            return None
        
        # 2. 손익계산서 (Income Statement) - 원본 데이터 가져오기
        # limit=2를 하는 이유: 작년 매출과 비교해서 성장률(Growth)을 구하려고
        url_income = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?period=annual&limit=2&apikey={api_key}"
        res_income = requests.get(url_income).json()

        # 3. 대차대조표 (Balance Sheet) - 자본총계 가져오기 (ROE 계산용)
        url_balance = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}?period=annual&limit=1&apikey={api_key}"
        res_balance = requests.get(url_balance).json()

        if not res_income or not res_balance:
             st.warning(f"⚠️ '{ticker}'의 재무제표가 아직 업데이트되지 않았습니다.")
             return None

        # --- [직접 계산기 돌리기] ---
        # 필요한 숫자들 추출
        price = res_quote[0].get('price', 0)
        name = res_quote[0].get('name', ticker)
        
        # 최신(올해) 데이터
        this_year = res_income[0]
        revenue = this_year.get('revenue', 0)
        net_income = this_year.get('netIncome', 0)
        eps = this_year.get('eps', 0)
        
        # 작년 데이터 (성장률 계산용)
        last_year_rev = res_income[1].get('revenue', 1) if len(res_income) > 1 else revenue

        # 자본 (ROE 계산용)
        equity = res_balance[0].get('totalStockholdersEquity', 1)

        # 1. ROE (자기자본이익률) = 순이익 / 자본
        roe = (net_income / equity) * 100 if equity != 0 else 0

        # 2. Net Margin (순이익률) = 순이익 / 매출
        margin = (net_income / revenue) * 100 if revenue != 0 else 0

        # 3. Growth (성장률) = (올해매출 - 작년매출) / 작년매출
        growth = ((revenue - last_year_rev) / last_year_rev) * 100

        # 4. P/E (주가수익비율) = 주가 / EPS
        pe = price / eps if eps > 0 else 0
        
        # 5. P/B (주가순자산비율) = 주가 / (자본/주식수) -> 약식으로 시총/자본
        market_cap = res_quote[0].get('marketCap', 0)
        pb = market_cap / equity if equity != 0 else 0

        # 데이터 포장해서 내보내기
        data = {
            "name": name,
            "price": price,
            "roe": roe,
            "margin": margin,
            "growth": growth,
            "pe": pe,
            "eps": eps,
            "pb": pb
        }
        return data

    except Exception as e:
        st.error(f"🚨 계산 중 오류 발생: {e}") 
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
st.markdown("Analysis powered by **FMP (Raw Data Calculation)**.")
st.divider()

ticker = st.text_input("ENTER TICKER (e.g., AAPL, NVDA, TSLA)", value="AAPL").strip().upper()

if ticker:
    with st.spinner(f"Analyzing {ticker} Financials..."):
        data = get_fmp_data(ticker)

        if data:
            # 결과 헤더
            st.subheader(f"📊 Analysis Result: {data['name']}")
            st.caption(f"Current Price: ${data['price']:,.2f}")

            # [10대 맞춤형 아이콘 & 설명]
            c1, c2, c3 = st.columns(3)
            
            # 1. ROE
            roe = data['roe']
            roe_status = "good" if roe >= 15 else ("okay" if roe >= 10 else "bad")
            roe_icon = "🏆" if roe_status == "good" else ("🤔" if roe_status == "okay" else "💤")
            create_card(c1, "ROE (Score)", f"{roe:.1f}", "%", roe_status, 
                        "**The Report Card.** Over 15% is an A+!", roe_icon)

            # 2. Margin
            margin = data['margin']
            margin_status = "good" if margin >= 20 else ("okay" if margin >= 10 else "bad")
            margin_icon = "💰" if margin_status == "good" else ("🪙" if margin_status == "okay" else "💸")
            create_card(c2, "Net Margin", f"{margin:.1f}", "%", margin_status, 
                        "**Pure Cash.** How much they keep.", margin_icon)

            # 3. Growth
            growth = data['growth']
            growth_status = "good" if growth >= 10 else ("okay" if growth > 0 else "bad")
            growth_icon = "🚀" if growth_status == "good" else ("🚶" if growth_status == "okay" else "🐌")
            create_card(c3, "Growth (YoY)", f"{growth:.1f}", "%", growth_status, 
                        "**Rocket Speed.** Is it getting bigger?", growth_icon)

            c4, c5, c6 = st.columns(3)
            
            # 4. P/E
            pe = data['pe']
            if pe <= 0: pe_status = "bad"; pe_disp = "Loss"
            elif pe > 50: pe_status = "okay"; pe_disp = f"{pe:.1f}x"
            else: pe_status = "good"; pe_disp = f"{pe:.1f}x"
            pe_icon = "🏷️" if pe_status == "good" else "💎" 
            create_card(c4, "P/E Ratio", pe_disp, "", pe_status, 
                        "**Price Tag.** Lower is usually better.", pe_icon)
            
            # 5. EPS
            eps = data['eps']
            eps_status = "good" if eps > 0 else "bad"
            eps_icon = "🍕" if eps_status == "good" else "🦴"
            create_card(c5, "EPS", f"${eps:.2f}", "", eps_status, 
                        "**Your Slice.** Profit per share.", eps_icon)

            # 6. P/B
            pb = data['pb']
            pb_status = "good" if pb < 3 else "okay"
            pb_icon = "🎁" if pb_status == "good" else "📦"
            create_card(c6, "P/B Ratio", f"{pb:.1f}", "x", pb_status, 
                        "**Bargain Hunt.** Close to 1.0 is cheap.", pb_icon)
            
# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>Built by <b>Daniel Park</b> | Powered by WEMAKEMOVES AI</div>", unsafe_allow_html=True)
