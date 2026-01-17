@st.cache_data(ttl=3600)
def get_fmp_data(ticker: str):
    general = st.secrets.get("general", {})
    api_key = general.get("FMP_API_KEY")
    if not api_key:
        st.error("⚠️ API Key가 설정되지 않았습니다. Secrets를 확인해주세요.")
        return None

    try:
        url_ratios = f"https://financialmodelingprep.com/api/v3/ratios-ttm/{ticker}?apikey={api_key}"
        resp_ratios = requests.get(url_ratios, timeout=10)
        if resp_ratios.status_code != 200:
            return None
        r_ratios = resp_ratios.json()

        url_price = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={api_key}"
        resp_price = requests.get(url_price, timeout=10)
        if resp_price.status_code != 200:
            return None
        r_price = resp_price.json()

        # 응답이 리스트인지/비어있는지 확인
        if not isinstance(r_ratios, list) or not r_ratios:
            return None
        if not isinstance(r_price, list) or not r_price:
            return None

        return {"ratios": r_ratios[0], "price": r_price[0]}
    except Exception:
        return None


# 사용부에서도 None 방어 (예: 숫자 변환)
def to_float(x, default=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default

ticker = st.text_input("ENTER TICKER (e.g., AAPL, TSLA, NVDA)", value="AAPL").strip().upper()

# ...
roe = to_float(ratios.get('returnOnEquityTTM')) * 100
margin = to_float(ratios.get('netProfitMarginTTM')) * 100
debt = to_float(ratios.get('debtEquityRatioTTM')) * 100
pe = to_float(ratios.get('priceEarningsRatioTTM'), default=-1)
