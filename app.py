import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# ১. ওয়েবসাইটের সেটিংস
st.set_page_config(page_title="Trading Simulator", layout="wide")
st.title("📈 অফলাইন ট্রেডিং সিমুলেটর")

# ২. অ্যাকাউন্ট ব্যালেন্স ও পোর্টফোলিও হিসাব (সেশন স্টেট)
if "balance" not in st.session_state:
    st.session_state.balance = 100000.0  # শুরুতে ১ লাখ টাকা ভার্চুয়াল ক্যাশ
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {}  # কেনা শেয়ারের হিসাব

# ৩. সাইডবার - ইউজার ব্যালেন্স ও পোর্টফোলিও দেখানো
st.sidebar.header("💰 আপনার অ্যাকাউন্ট")
st.sidebar.metric(label="অবশিষ্ট ব্যালেন্স (Cash)", value=f"${st.session_state.balance:,.2f}")

st.sidebar.subheader("💼 আপনার পোর্টফোলিও")
if st.session_state.portfolio:
    for stock, qty in st.session_state.portfolio.items():
        if qty > 0:
            st.sidebar.write(f"**{stock}**: {qty} টি শেয়ার")
else:
    st.sidebar.write("আপনার কোনো শেয়ার কেনা নেই।")

# ৪. মেইন স্ক্রিন - স্টক সিলেকশন ও ডাটা ফেচিং
ticker = st.text_input("স্টক সিম্বল লিখুন (যেমন: AAPL, TSLA, MSFT):", value="AAPL").upper()

try:
    # yfinance থেকে স্টক ডাটা আনা
    stock_data = yf.download(ticker, period="1mo", interval="1d")
    
    if not stock_data.empty:
        # বর্তমান লাইভ প্রাইস বের করা
        current_price = float(stock_data['Close'].iloc[-1])
        st.subheader(f"{ticker} এর বর্তমান মূল্য: ${current_price:,.2f}")
        
        # ৫. ক্যান্ডেলস্টিক চার্ট তৈরি (Plotly দিয়ে)
        fig = go.Figure(data=[go.Candlestick(
            x=stock_data.index,
            open=stock_data['Open'],
            high=stock_data['High'],
            low=stock_data['Low'],
            close=stock_data['Close']
        )])
        fig.update_layout(xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # ৬. বাই/সেল প্যানেল (Trading Logic)
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🛒 শেয়ার কিনুন (Buy)")
            buy_qty = st.number_input("কতটি শেয়ার কিনতে চান?", min_value=1, step=1, key="buy")
            total_cost = buy_qty * current_price
            st.write(f"মোট খরচ: ${total_cost:,.2f}")
            
            if st.button("Buy Order Place"):
                if st.session_state.balance >= total_cost:
                    st.session_state.balance -= total_cost
                    st.session_state.portfolio[ticker] = st.session_state.portfolio.get(ticker, 0) + buy_qty
                    st.success(f"সফলভাবে {buy_qty}টি {ticker} শেয়ার কেনা হয়েছে!")
                    st.rerun()
                else:
                    st.error("দুঃখিত! আপনার অ্যাকাউন্টে পর্যাপ্ত ব্যালেন্স নেই।")
                    
        with col2:
            st.subheader("💰 শেয়ার বিক্রি করুন (Sell)")
            sell_qty = st.number_input("কতটি শেয়ার বিক্রি করতে চান?", min_value=1, step=1, key="sell")
            total_revenue = sell_qty * current_price
            st.write(f"মোট পাবেন: ${total_revenue:,.2f}")
            
            if st.button("Sell Order Place"):
                current_owned = st.session_state.portfolio.get(ticker, 0)
                if current_owned >= sell_qty:
                    st.session_state.balance += total_revenue
                    st.session_state.portfolio[ticker] -= sell_qty
                    st.success(f"সফলভাবে {sell_qty}টি {ticker} শেয়ার বিক্রি করা হয়েছে!")
                    st.rerun()
                else:
                    st.error(f"আপনার কাছে পর্যাপ্ত {ticker} শেয়ার নেই! (বর্তমানে আছে: {current_owned}টি)")
                    
    else:
        st.error("কোনো ডাটা পাওয়া যায়নি। দয়া করে সঠিক স্টক কোড লিখুন।")
except Exception as e:
    st.error("ডাটা লোড করতে সমস্যা হচ্ছে। সঠিক সিম্বল দিন।")
