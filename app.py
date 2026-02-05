import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="WEMAKEMOVES Finance", layout="wide")

# ---------------------------------------------------------
# 진단 기능을 포함한 데이터 함수 🕵️‍♂️
# ---------------------------------------------------------
def get_fmp_data(ticker):
    # 1. 키 확인
    if "FMP_API_KEY" not in st.secrets:
        st.error("🚨 Secrets에 FMP_API_KEY가 없습니다.")
        return None
    api_key = st.secrets["FMP_API_KEY"]

    try:
        # 2. 재무제표 요청 (여기서 문제가 생기는 중)
        url_income = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?period=annual&limit=2&apikey={api_key}"
        res_income = requests.get(url_income).json()

        # [진단] 데이터가 리스트([])가 아니라 딕셔너리({})로 왔다면 에러 메시지임!
        if isinstance(res_income, dict):
            st.error(f"🚫 FMP에서 거절했습니다. 원문: {res_income}")
            return None
            
        if not res_income:
            st.warning(f"⚠️ 데이터가 비어있습니다. (티커: {ticker})")
            return None
            
        # 3. 주가 정보 요청
        url_quote = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={api_key}"
        res_quote = requests.get(url_quote).json()
        
        if isinstance(res_quote, dict): # 여기도 진단
             st.error(f"🚫 주가 정보 거절됨: {res_quote}")
             return None

        # 4. 데이터 정상일 때만 계산
        this_year = res_income[0]
        revenue = this_year.get('revenue', 0)
        net_income = this_year.get('netIncome', 0)
        price = res_quote[0].get('price', 0)
        
        # 간단 데이터 반환
        return {"name": ticker, "price": price, "revenue": revenue, "net_income": net_income}

    except Exception as e:
        st.error(f"🚨 시스템 에러 상세: {e}")
        return None

# ---------------------------------------------------------
# 메인 화면
# ---------------------------------------------------------
st.title("🧭 WEMAKEMOVES Diagnosis Mode")
ticker = st.text_input("Ticker", "AAPL").upper()

if st.button("진단 시작"):
    data = get_fmp_data(ticker)
    if data:
        st.success(f"✅ 성공! 매출: ${data['revenue']:,.0f}")
        st.metric("Price", f"${data['price']}")
