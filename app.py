import streamlit as st
from library import *

# Configure Streamlit page
st.set_page_config(
     page_title="Venture Fund Simulator",
     page_icon="🚀",
     layout="centered",
     initial_sidebar_state="expanded",
     menu_items={
         'Get help': None,
         'Report a bug': None,
         'About': "A simulator of venture funds to help build intuition for VC investing."
     }
 )

# Input sidebar
with st.sidebar:
    st.title("Configure simulation parameters")

    st.subheader("Probability of return multiples")
    input_prob_dist_zero = st.number_input(label="% of companies that return 0x", min_value=1.0, max_value=100.0, step=5.0, value=33.33333,
    help="The percentage of companies that are expected to return nothing on the \
    original investment.")
    input_prob_dist_liquidation = st.number_input(label="% of companies that <1x", min_value=1.0, max_value=100.0, step=5.0, value=33.33333,
    help="The percentage of companies that are expected to be liquidated and return \
    some fraction of the original investment.")
    input_prob_dist_multiple = st.number_input(label="% of companies that ≥1x", min_value=1.0, max_value=100.0, step=5.0, value=33.33333,
    help="The percentage of companies that are expected to return greater than or \
    equal to the original investment.")
    input_liquidation_pct = st.number_input(label="% of original investment \
    recovered in event of liquidation", min_value=1.0, max_value=100.0, step=5.0, value=80.0,
    help="In the event a portfolio company must be liquidated, this is the expected \
    percentage of the original investment that will be recovered.")
    st.markdown("##")

    st.subheader("Fund parameters")
    input_target_yoy_growth = st.number_input(label="Target % for YoY growth", min_value=0.1, max_value=300.0, step=1.0, value=30.0,
    help="The targeted percentage of year-over-year growth that the venture funds \
    are seeking with their investments.")
    input_target_exit_time = st.number_input(label="Target # of years for exit time", min_value=1, max_value=100, step=1, value=4,
    help="The targeted number of years by which the venture fund would like to exit \
    an investment.")
    input_portfolio_size= st.number_input(label="Portfolio size", min_value=1, max_value=1000, step=1, value=50,
    help="The number of companies that each venture fund will invest in.")


# Content window
st.title("Venture Fund Simulator")
st.markdown("*Description of the simulator goes here. Built by Wes De \
Silvestro. Check out the [launch post](url) for more details.*")
