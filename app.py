import streamlit as st
import requests
import pandas as pd

# 1. FMP 키 가져오기 (비밀금고에서)
api_key = st.secrets["FMP_API_KEY"]
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
# 3. 유틸 함수
# ---------------------------------------------------------
def to_float(x, default=0.0):
    try:
        if x is None or x == "None" or x == "-": return default
        return float(x)
    except: return default

# ---------------------------------------------------------
# 4. 데이터 가져오기 (Alpha Vantage)
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def get_stock_data(ticker):
    # [★중요] 아까 받으신 Alpha Vantage 키를 여기에 넣어주세요!
    api_key = "6I5WFN8TPZ79RKC3"  
    
    try:
        # Overview
        url_overview = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={api_key}"
        data_overview = requests.get(url_overview).json()
        
        # Price
        url_price = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={api_key}"
        data_price = requests.get(url_price).json()

        if not data_overview: return None
        if "Note" in data_overview or "Information" in data_overview:
            return "LIMIT"
            
        return {"overview": data_overview, "price": data_price}
        
    except Exception:
        return None

# ---------------------------------------------------------
# 5. 카드 UI 생성 함수 (아이콘 커스텀 기능 추가)
# ---------------------------------------------------------
def create_card(col, title, value, unit, status, description, custom_icon=None):
    # 상태에 따른 색상 설정
    if status == "good": color_class = "good"
    elif status == "okay": color_class = "okay"
    else: color_class = "bad"
    
    # 아이콘이 따로 지정되지 않았을 때의 기본값
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
# 6. 메인 화면 로직
# ---------------------------------------------------------
st.title("🧭 Teen Stock Compass: Pro Dashboard")
st.markdown("Analysis powered by **Alpha Vantage**.")
st.divider()

ticker = st.text_input("ENTER TICKER (e.g., META, NVDA, TSLA)", value="META").strip().upper()

if ticker:
    with st.spinner(f"Analyzing {ticker} for you..."):
        data = get_stock_data(ticker)

        if data == "LIMIT":
             st.error("⚠️ Daily Limit Reached. (Free Key: 25 searches/day)")
        elif not data:
            st.error(f"⚠️ Could not find data for '{ticker}'.")
        else:
            overview = data['overview']
            price_data = data['price'].get('Global Quote', {})

            # 데이터 변환
            price = to_float(price_data.get('05. price'), 0)
            
            # [수정된 부분] 오타 없이 완벽하게 수정했습니다.
            roe = to_float(overview.get('ReturnOnEquityTTM'), 0) * 100
            
            margin = to_float(overview.get('ProfitMargin'), 0) * 100
            growth = to_float(overview.get('QuarterlyRevenueGrowthYOY'), 0) * 100
            pe = to_float(overview.get('TrailingPE'), 0)
            eps = to_float(overview.get('EPS'), 0)
            pb = to_float(overview.get('PriceToBookRatio'), 0)

            # 결과 출력
            st.subheader(f"📊 Analysis Result: {ticker}")
            st.caption(f"Current Price: ${price:,.2f}")

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
            create_card(c2, "Net Margin (Profit)", f"{margin:.1f}", "%", margin_status, 
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
            
            # 5. EPS (주당 순이익)
            eps_status = "good" if eps > 0 else "bad"
            eps_icon = "🍕" if eps_status == "good" else "🦴"
            create_card(c5, "EPS", f"${eps}", "", eps_status, 
                        "**Your Slice.** Profit per single stock ticket. Must be positive!", eps_icon)

            # 6. P/B (자산가치)
            pb_status = "good" if pb < 3 else "okay"
            pb_icon = "🎁" if pb_status == "good" else "📦"
            create_card(c6, "P/B Ratio", f"{pb:.1f}", "x", pb_status, 
                        "**Bargain Hunt.** Close to 1.0 means you buy it for the raw material price.", pb_icon)
            
# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>Built by <b>Daniel Park</b></div>", unsafe_allow_html=True)
