import streamlit as st
import yfinance as yf
import time
import requests

# ---------------------------------------------------------
# 1. Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Teen Stock Compass Pro",
    page_icon="🧭",
    layout="wide"
)

# ---------------------------------------------------------
# 2. Custom CSS for Dark Mode Card Design
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
# 3. Data Fetching Function (Anti-Blocking Mode)
# ---------------------------------------------------------
@st.cache_data(ttl=900)
def get_financial_data(ticker_symbol):
    try:
        # [핵심 수정] 가짜 신분증(User-Agent) 만들기
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # 야후에 신분증 제시하며 데이터 요청
        stock = yf.Ticker(ticker_symbol, session=session)
        
        # 데이터가 실제로 있는지 확인하기 위해 기본 정보 호출
        info = stock.info
        return info
    except Exception as e:
        return None

# ---------------------------------------------------------
# 4. Helper Function to Create Cards
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
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">{icon} {title}</div>
            <div class="metric-value {color_class}">
                {value}{unit}
            </div>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("What does this mean?"):
            st.write(description)

# ---------------------------------------------------------
# 5. Main Application Logic
# ---------------------------------------------------------
st.title("🧭 Teen Stock Compass: Pro Dashboard")
st.markdown("Analyze company health like a Wall Street pro using **5 Key Metrics**.")
st.divider()

ticker = st.text_input("ENTER TICKER SYMBOL (e.g., AAPL, NVDA, KO)", value="AAPL").upper()

if ticker:
    with st.spinner(f"Analyzing {ticker}... Please wait..."):
        info = get_financial_data(ticker)

        # 데이터가 없거나, 텅 빈 껍데기만 왔을 경우 방어
        if not info or 'regularMarketPrice' not in info and 'currentPrice' not in info:
            st.warning(f"⚠️ Yahoo Finance is currently limiting data for '{ticker}'. Please try again in 5 minutes or try a different ticker.")
        else:
            # 가격 정보 안전하게 가져오기
            price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
            
            # 지표 추출
            roe = info.get('returnOnEquity', 0)
            roe = roe * 100 if roe is not None else 0
            
            margin = info.get('profitMargins', 0)
            margin = margin * 100 if margin is not None else 0
            
            growth = info.get('revenueGrowth', 0)
            growth = growth * 100 if growth is not None else 0
            
            debt = info.get('debtToEquity', 0)
            debt = debt if debt is not None else 0
            
            pe = info.get('trailingPE', 0)
            pe = pe if pe is not None else 0

            # 화면 출력
            st.subheader(f"📊 Analysis Result: {ticker}")
            st.caption(f"Current Price: ${price:,.2f}")

            # Row 1
            c1, c2, c3 = st.columns(3)

            roe_status = "good" if roe >= 15 else ("okay" if roe >= 10 else "bad")
            create_card(c1, "ROE (Efficiency)", f"{roe:.1f}", "%", roe_status,
                        "**Return on Equity:** How efficiently the company uses money. Over 15% is excellent.")

            margin_status = "good" if margin >= 20 else ("okay" if margin >= 10 else "bad")
            create_card(c2, "Net Margin (Profit)", f"{margin:.1f}", "%", margin_status,
                        "**Net Profit Margin:** The percentage of revenue that becomes pure profit.")

            growth_status = "good" if growth >= 10 else ("okay" if growth > 0 else "bad")
            create_card(c3, "Growth (YoY)", f"{growth:.1f}", "%", growth_status,
                        "**Revenue Growth:** Is the company getting bigger? Positive is good.")

            # Row 2
            c4, c5 = st.columns(2)

            debt_status = "good" if debt < 100 else ("okay" if debt < 200 else "bad")
            create_card(c4, "Debt Ratio (Safety)", f"{debt:.1f}", "%", debt_status,
                        "**Debt-to-Equity:** Lower is safer. Over 200% is risky.")

            if pe <= 0: pe_status = "bad"; pe_disp = "Loss"
            elif pe > 50: pe_status = "okay"; pe_disp = f"{pe:.1f}x"
            else: pe_status = "good"; pe_disp = f"{pe:.1f}x"
            
            create_card(c5, "P/E Ratio (Valuation)", pe_disp, "", pe_status,
                        "**Price-to-Earnings:** Shows if the stock is cheap or expensive. Lower is often better.")

# ---------------------------------------------------------
# 6. Footer
# ---------------------------------------------------------
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>Built by <b>Daniel Park</b></div>", unsafe_allow_html=True)
