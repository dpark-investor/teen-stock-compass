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
# 3. 유틸 함수 (안전한 숫자 변환)
# ---------------------------------------------------------
def to_float(x, default=0.0) -> float:
    try:
        if x is None:
            return default
        return float(x)
    except (TypeError, ValueError):
        return default

# ---------------------------------------------------------
# 4. 데이터 가져오기 (보안 강화 버전)
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def get_fmp_data(ticker: str):
    # Secrets 구조가 다를 수 있으니 안전하게 접근
    general = st.secrets.get("general", {})
    api_key = general.get("FMP_API_KEY")

    # 혹시 secrets.toml을 general 없이 쓴 경우도 지원
    if not api_key:
        api_key = st.secrets.get("FMP_API_KEY")

    if not api_key:
        # 캐시 함수 내부에서 st.error를 띄워도 되지만,
        # 배포 환경에 따라 메시지가 애매할 수 있어 None만 반환하고
        # 호출부에서 에러 처리하는 편이 더 깔끔합니다.
        return {"error": "missing_api_key"}

    try:
        # Ratio (TTM)
        url_ratios = f"https://financialmodelingprep.com/api/v3/ratios-ttm/{ticker}?apikey={api_key}"
        resp_ratios = requests.get(url_ratios, timeout=10)
        if resp_ratios.status_code != 200:
            return None
        r_ratios = resp_ratios.json()

        # Price Quote
        url_price = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={api_key}"
        resp_price = requests.get(url_price, timeout=10)
        if resp_price.status_code != 200:
            return None
        r_price = resp_price.json()

        # 응답 형태 방어 (리스트/비어있음/에러 메시지)
        if not isinstance(r_ratios, list) or not r_ratios:
            return None
        if not isinstance(r_price, list) or not r_price:
            return None

        # 가끔 {"Error Message": "..."} 같은 형태가 섞일 때 방어
        if isinstance(r_ratios[0], dict) and ("Error Message" in r_ratios[0] or "error" in r_ratios[0]):
            return None
        if isinstance(r_price[0], dict) and ("Error Message" in r_price[0] or "error" in r_price[0]):
            return None

        return {"ratios": r_ratios[0], "price": r_price[0]}

    except Exception:
        return None

# ---------------------------------------------------------
# 5. 카드 생성 함수
# ---------------------------------------------------------
def create_card(col, title, value, unit, status, description):
    if status == "good":
        color_class = "good"
        icon = "🟢"
    elif status == "okay":
        color_class = "okay"
        icon = "🟡"
    else:
        color_class = "bad"
        icon = "🔴"

    with col:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-title">{icon} {title}</div>
            <div class="metric-value {color_class}">
                {value}{unit}
            </
