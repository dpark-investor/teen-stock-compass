import streamlit as st
from yahooquery import Ticker
import pandas as pd
import plotly.graph_objects as go
import time

# ---------------------------------------------------------
# 1. 페이지 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="Teen Stock Compass Pro",
    page_icon="🧭",
    layout="wide"
)

# ---------------------------------------------------------
# 2. 디자인 (다크모드 & 카드)
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
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. 데이터 가져오기 (YahooQuery 엔진 사용)
# ---------------------------------------------------------
@st.cache_data(ttl=300) # 5분간 데이터 캐시 (서버 부하 감소)
def get_financial_data(ticker_symbol):
    try:
        # YahooQuery 엔진 시동
        stock = Ticker(ticker_symbol)
        
        # 데이터 4종류를 한 번에 가져옴 (속도 최적화)
        summary_detail = stock.summary_detail[ticker_symbol]
        financial_data = stock.financial_data[ticker_symbol]
        key_stats = stock.key_stats[ticker_symbol]
        price_data = stock.price[ticker_symbol]

        # 데이터가 '문자열(에러메시지)'로 오면 데이터 없는 것
        if isinstance(summary_detail, str):
            return None

        # 모든 데이터를 하나의 딕셔너리로 통합
        data = {}
        data.update(summary_detail)
        data.update(financial_data)
        data.update(key_stats)
        data.update(price_data)
        
        return data
        
    except Exception as e:
        return None

# ---------------------------------------------------------
# 4. 카드 생성 함수
# ---------------------------------------------------------
def create_card(col, title, value, unit, status, description):
    if status == "good": color_class = "good"; icon = "🟢"
    elif status == "okay": color_class = "okay"; icon = "🟡"
    else: color_class = "bad"; icon = "🔴"
    
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">{icon} {title}</div>
            <div class="metric-value {color_class}">
                {value}{unit}
            </div>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("Meanings"):
            st.write(description)

# ---------------------------------------------------------
# 5. 메인 로직
# ---------------------------------------------------------
st.title("🧭 Teen Stock Compass: Real-Time Pro")
st.markdown("Professional Grade Analysis powered by **YahooQuery Engine**.")
st.divider()

ticker = st.text_input("ENTER TICKER (e.g., AAPL, TSLA, AMZN)", value="AAPL").upper()

if ticker:
    with st.spinner(f"Connecting to live market data for {ticker}..."):
        data = get_financial_data(ticker)

        if not data or 'regularMarketPrice' not in data:
            st.error(f"⚠️ Could not retrieve data for '{ticker}'. Check the symbol or try again.")
        else:
            # --- 데이터 추출 (더 안전하고 정확함) ---
            
            # 가격
            price = data.get('regularMarketPrice', 0)
            
            # 1. ROE (자기자본이익률)
            roe = data.get('returnOnEquity', 0)
            roe = roe * 100 if roe else 0
            
            # 2. Net Margin (순이익률)
            margin = data.get('profitMargins', 0)
            margin = margin * 100 if margin else 0
            
            # 3. Growth (성장률)
            growth = data.get('revenueGrowth', 0)
            growth = growth * 100 if growth else 0
            
            # 4. Debt (부채비율)
            debt = data.get('debtToEquity', 0)
            # 데이터가 없을 경우 0으로 처리
            debt = debt if debt else 0
            
            # 5. PER (주가수익비율)
            pe = data.get('trailingPE', 0)
            pe = pe if pe else 0

            # --- 결과 출력 ---
            st.subheader(f"📊 Live Analysis: {ticker}")
            st.caption(f"Real-Time Price: ${price:,.2f}")

            # Row 1
            c1, c2, c3 = st.columns(3)
            
            roe_status = "good" if roe >= 15 else ("okay" if roe >= 10 else "bad")
            create_card(c1, "ROE (Efficiency)", f"{roe:.1f}", "%", roe_status,
                        "**Return on Equity:** How efficiently the company uses money. >15% is great.")

            margin_status = "good" if margin >= 20 else ("okay" if margin >= 10 else "bad")
            create_card(c2, "Net Margin (Profit)", f"{margin:.1f}", "%", margin_status,
                        "**Net Profit Margin:** Pure profit percentage out of revenue.")

            growth_status = "good" if growth >= 10 else ("okay" if growth > 0 else "bad")
            create_card(c3, "Growth (YoY)", f"{growth:.1f}", "%", growth_status,
                        "**Revenue Growth:** Is the company expanding? Positive is good.")

            # Row 2
            c4, c5 = st.columns(2)
            
            debt_status = "good" if debt < 100 else ("okay" if debt < 200 else "bad")
            create_card(c4, "Debt Ratio (Safety)", f"{debt:.1f}", "%", debt_status,
                        "**Debt-to-Equity:** Lower is safer. Over 200% is risky.")

            if pe <= 0: pe_status = "bad"; pe_disp = "Loss"
            elif pe > 50: pe_status = "okay"; pe_disp = f"{pe:.1f}x"
            else: pe_status = "good"; pe_disp = f"{pe:.1f}x"
            create_card(c5, "P/E Ratio (Valuation)", pe_disp, "", pe_status,
                        "**Price-to-Earnings:** Lower P/E often means undervalued.")

# ---------------------------------------------------------
# 6. Footer
# ---------------------------------------------------------
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>Built by <b>Daniel Park</b></div>", unsafe_allow_html=True)
