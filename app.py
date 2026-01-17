import streamlit as st
import pandas as pd
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
# 3. 데이터 가져오기 (Source: Finviz)
# ---------------------------------------------------------
@st.cache_data(ttl=300) # 5분 캐시
def get_finviz_data(ticker):
    try:
        url = f"https://finviz.com/quote.ashx?t={ticker}"
        # 사람인 척 위장하는 헤더 (필수)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        
        response = requests.get(url, headers=headers)
        
        # 티커가 없거나 페이지가 없으면 
        if response.status_code != 200:
            return None

        # 판다스로 표(Table) 긁어오기
        tables = pd.read_html(response.text)
        
        # Finviz의 재무 데이터는 보통 5번째나 6번째 표에 있음
        # 표를 순회하며 우리가 원하는 데이터가 있는 표를 찾음
        df = tables[-2] # 뒤에서 두번째 표가 주로 재무제표임
        
        # 보기 쉽게 컬럼 이름을 0, 1로 변경
        df.columns = ['Key', 'Value'] * (len(df.columns) // 2)
        
        # 모든 데이터를 하나의 딕셔너리로 변환
        data_dict = {}
        for i in range(0, len(df.columns), 2):
            subset = df.iloc[:, i:i+2]
            subset.columns = ['Key', 'Value']
            for _, row in subset.iterrows():
                data_dict[row['Key']] = row['Value']
        
        return data_dict
        
    except Exception as e:
        return None

# 숫자 뒤의 %, B, M 등을 떼고 숫자로 바꾸는 함수
def parse_value(value_str):
    if not isinstance(value_str, str): return 0
    try:
        if value_str == '-': return 0
        value_str = value_str.replace('%', '').replace(',', '')
        if 'B' in value_str: return float(value_str.replace('B', '')) * 1000000000
        if 'M' in value_str: return float(value_str.replace('M', '')) * 1000000
        return float(value_str)
    except:
        return 0

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
        with st.expander("Meaning"):
            st.write(description)

# ---------------------------------------------------------
# 5. 메인 로직
# ---------------------------------------------------------
st.title("🧭 Teen Stock Compass: Pro Dashboard")
st.markdown("Analyze financial health using real-time data from **Finviz**.")
st.divider()

ticker = st.text_input("ENTER TICKER (e.g., AAPL, NVDA, TSLA)", value="AAPL").upper()

if ticker:
    with st.spinner(f"Fetching data for {ticker} from Finviz..."):
        data = get_finviz_data(ticker)

        if not data:
            st.error(f"⚠️ Could not find data for '{ticker}'. Please check the symbol.")
        else:
            # --- Finviz 데이터 파싱 ---
            
            # 1. 가격
            price_str = data.get('Price', '0')
            price = parse_value(price_str)
            
            # 2. ROE
            roe_str = data.get('ROE', '0')
            roe = parse_value(roe_str)
            
            # 3. Profit Margin
            margin_str = data.get('Profit Margin', '0')
            margin = parse_value(margin_str)
            
            # 4. Sales Q/Q (Growth)
            growth_str = data.get('Sales Q/Q', '0')
            growth = parse_value(growth_str)
            
            # 5. Debt/Eq
            debt_str = data.get('Debt/Eq', '0')
            # Finviz는 1.5 이렇게 줌 (퍼센트 아님). 그래서 100을 곱해야 함
            debt = parse_value(debt_str) * 100 
            
            # 6. P/E
            pe_str = data.get('P/E', '0')
            pe = parse_value(pe_str)

            # --- 결과 출력 ---
            st.subheader(f"📊 Analysis Result: {ticker}")
            st.caption(f"Current Price: ${price:,.2f}")

            # Row 1
            c1, c2, c3 = st.columns(3)
            
            roe_status = "good" if roe >= 15 else ("okay" if roe >= 10 else "bad")
            create_card(c1, "ROE (Efficiency)", f"{roe:.1f}", "%", roe_status,
                        "**Return on Equity:** How efficiently the company uses money. >15% is excellent.")

            margin_status = "good" if margin >= 20 else ("okay" if margin >= 10 else "bad")
            create_card(c2, "Net Margin (Profit)", f"{margin:.1f}", "%", margin_status,
                        "**Net Profit Margin:** Pure profit percentage.")

            growth_status = "good" if growth >= 10 else ("okay" if growth > 0 else "bad")
            create_card(c3, "Growth (YoY)", f"{growth:.1f}", "%", growth_status,
                        "**Sales Growth (Q/Q):** Is the company expanding?")

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
