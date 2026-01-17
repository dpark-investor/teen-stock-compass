import streamlit as st
import requests

# 1. 페이지 설정
st.set_page_config(page_title="Teen Stock Compass Pro", page_icon="🧭", layout="wide")

# 2. 디자인
st.markdown("""
<style>
    .metric-card { background-color: #1E1E1E; border: 1px solid #333; border-radius: 15px; padding: 20px; margin-bottom: 15px; }
    .metric-value { color: #FFFFFF; font-size: 2.2rem; font-weight: bold; }
    .good { color: #29B094 !important; }
    .okay { color: #FFC107 !important; }
    .bad { color: #FF4B4B !important; }
</style>
""", unsafe_allow_html=True)

# 3. 데이터 가져오기 (Alpha Vantage: 인증 없음)
@st.cache_data(ttl=3600)
def get_stock_data(ticker):
    # [★여기에 키를 넣으세요] 
    api_key = "6I5WFN8TPZ79RKC3"
    
    try:
        url_overview = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={api_key}"
        data_overview = requests.get(url_overview).json()
        
        url_price = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={api_key}"
        data_price = requests.get(url_price).json()

        if not data_overview: return None
        return {"overview": data_overview, "price": data_price}
    except: return None

# 4. 카드 UI
def create_card(col, title, value, unit, status, description):
    color = "good" if status=="good" else ("okay" if status=="okay" else "bad")
    with col:
        st.markdown(f"""<div class="metric-card"><div style="color:#AAA;">{title}</div><div class="metric-value {color}">{value}{unit}</div></div>""", unsafe_allow_html=True)
        with st.expander("Meaning"): st.write(description)

# 5. 메인 화면
st.title("🧭 Teen Stock Compass: Pro")
ticker = st.text_input("ENTER TICKER (META, TSLA, NVDA)", value="META").upper()

if ticker:
    with st.spinner(f"Searching {ticker}..."):
        data = get_stock_data(ticker)
        
        if not data:
            st.error("⚠️ 데이터 로딩 실패. 키를 정확히 입력했는지 확인해주세요.")
        elif "Note" in data.get('overview', {}):
            st.error("⚠️ 하루 조회 한도(25회) 초과! 내일 다시 시도하세요.")
        else:
            # 데이터 표시
            ov = data['overview']
            pr = data['price'].get('Global Quote', {})
            
            price = float(pr.get('05. price', 0))
            roe = float(ov.get('ReturnOnEquityTTM', 0)) * 100
            pe = float(ov.get('TrailingPE', 0))
            
            st.subheader(f"Analysis: {ticker}")
            st.caption(f"Price: ${price:,.2f}")
            
            c1, c2 = st.columns(2)
            create_card(c1, "ROE", f"{roe:.1f}", "%", "good" if roe>15 else "okay", "Return on Equity")
            create_card(c2, "P/E Ratio", f"{pe:.1f}", "x", "good" if 0<pe<30 else "okay", "P/E Ratio")
