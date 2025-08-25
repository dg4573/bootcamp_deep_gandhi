import streamlit as st
import utils

api_key = "q3NHa6rL"
client_code = "D531034"
pwd = "1123"
totp = "MKFRGXBJ66GCDC2U3BP4LLKMWM"

st.set_page_config(layout="wide")

@st.cache_data  
def load_data():
    obj = utils.connect_api()
    ce_df, pe_df = utils.fetch_data(obj)
    ce_df, pe_df = utils.preprocess_data(ce_df, pe_df)
    pivot_ce, pivot_pe = utils.make_pivots(ce_df, pe_df)
    fig_ce = utils.make_surface(pivot_ce, "CE IV Surface", "Viridis")
    fig_pe = utils.make_surface(pivot_pe, "PE IV Surface", "Plasma")
    return ce_df, pe_df, pivot_ce, pivot_pe, fig_ce, fig_pe

@st.cache_resource  
def load_iv_rank():
    return utils.display_iv_rank()

# Initial load
ce_df, pe_df, pivot_ce, pivot_pe, fig_ce, fig_pe = load_data()
iv_results = load_iv_rank()

page = st.sidebar.selectbox(
    "Select Page",
    ["CE IV Surface", "PE IV Surface", "Trade Recommendation Engine"]
)

if st.sidebar.button("Refresh IV Surfaces"):
    load_data.clear()  # Clear cache to force reload
    ce_df, pe_df, pivot_ce, pivot_pe, fig_ce, fig_pe = load_data()

if page == "CE IV Surface":
    st.title("NIFTY Call (CE) Implied Volatility Surface")
    col1, col2 = st.columns([3,1])
    col1.plotly_chart(fig_ce, use_container_width=True)
    col2.header("IV Rank & Percentile")
    for d, (rank, pct) in iv_results.items():
        col2.write(f"Last {d} days: Rank = {rank:.2f}%, Percentile = {pct:.2f}%")

elif page == "PE IV Surface":
    st.title("NIFTY Put (PE) Implied Volatility Surface")
    col1, col2 = st.columns([3,1])
    col1.plotly_chart(fig_pe, use_container_width=True)
    col2.header("IV Rank & Percentile")
    for d, (rank, pct) in iv_results.items():
        col2.write(f"Last {d} days: Rank = {rank:.2f}%, Percentile = {pct:.2f}%")

else:
    st.title("Trade Recommendation Engine")
    st.write("To be continued...")
