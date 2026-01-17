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
# 3. 유틸 함수 (안전한 숫자 변환 - 에러 방지용)
# ---------------------------------------------------------
def to_float(x, default=0.0) -> float:
    try:
        if x is None:
            return default
        return float(x)
    except (TypeError, ValueError):
        return default

# ---------------------------------------------------------
# 4. 데이터 가져오기 (수정됨: 키 직접 입력 방식)
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def get_fmp_data(ticker: str):
    # [수정] 비밀 금고 대신 키를 직접 넣어서 에러를 원천 차단했습니다.
    # 만약 이 키가 아직 인증이 안 되었다면 "demo" 라고 적으시면 됩니다.
    api_key = "7HHpAIcOk53R1j3dNxcPHYjDIbmfmhaR"

    try:
        # Ratio (재무 비율)
        url_ratios = f"https://financialmodelingprep.com/api/v3/ratios-ttm/{ticker}?apikey={api_key}"
        resp_ratios = requests.get(url_ratios, timeout=10)
        
        # Price Quote (주가)
        url_price = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={api_key}"
        resp_price = requests.get(url_price, timeout=10)

        # 응답 상태 확인
        if resp_ratios.status_code != 200 or resp_price.status_code != 200:
            return None

        r_ratios = resp_ratios.json()
        r_price = resp_price.json()

        # 데이터가 비어있거나 에러 메시지가 왔을 때 방어
        if not r_ratios or isinstance(r_ratios, dict) and "Error Message" in r_ratios:
             return None
        if not r_price or isinstance(r_price, dict) and "Error Message" in r_price:
             return None

        # 리스트 형태인 경우 첫 번째 요소 가져오기
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
        st.error(f"⚠️ Could not find data for '{ticker}'. (Check if Email is Verified or try 'AAPL' only)")
    else:
        ratios = data["ratios"]
        price_info = data["price"]

        # --- 데이터 추출 (안전한 변환 함수 사용) ---
        price = to_float(price_info.get("price"), default=0.0)
        roe = to_float(ratios.get("returnOnEquityTTM"), default=0.0
