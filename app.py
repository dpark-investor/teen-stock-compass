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
    
    # 아이콘이 따로 지정되지 않았을 때의 기본값 (귀여운 버전)
    if custom_icon:
        icon = custom_icon
    else:
        if status == "good": icon = "🔥"    # 좋으면 불꽃!
        elif status == "okay": icon = "🐣"  # 보통이면 병아리
        else: icon = "☔"                   # 나쁘면 우산
    
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
            roe = to_float(overview.get('ReturnOnEquityTT
