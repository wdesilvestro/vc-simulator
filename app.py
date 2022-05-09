import streamlit as st
from library import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager

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
    st.markdown("*All sliders must sum to 100% in total.*")
    # TODO: Throw an error if it doesn't sum to less than 100.
    input_prob_dist_zero = st.slider(label="% of companies that return 0x", min_value=1, max_value=100, step=1, value=33,
    help="The percentage of companies that are expected to return nothing on the \
    original investment.")
    input_prob_dist_liquidation = st.slider(label="% of companies that <1x", min_value=1, max_value=100, step=1, value=33,
    help="The percentage of companies that are expected to be liquidated and return \
    some fraction of the original investment.")
    input_prob_dist_multiple = st.slider(label="% of companies that ≥1x", min_value=1, max_value=100, step=1, value=33,
    help="The percentage of companies that are expected to return greater than or \
    equal to the original investment.")
    # TODO: Reset button
    st.markdown("##")

    st.subheader("Fund parameters")
    input_liquidation_pct = st.number_input(label="% of original investment \
    recovered in event of liquidation", min_value=1.0, max_value=100.0, step=5.0, value=80.0,
    help="In the event a portfolio company must be liquidated, this is the expected \
    percentage of the original investment that will be recovered.")
    input_target_yoy_growth = st.number_input(label="Target % for YoY growth", min_value=0.1, max_value=300.0, step=1.0, value=30.0,
    help="The targeted percentage of year-over-year growth that the venture funds \
    are seeking with their investments.")
    input_target_exit_time = st.number_input(label="Target # of years until an investment exits", min_value=1, max_value=100, step=1, value=4,
    help="The targeted number of years by which the venture fund would like to exit \
    an investment.")
    input_portfolio_size= st.number_input(label="Portfolio size", min_value=1, max_value=1000, step=1, value=50,
    help="The number of companies that each venture fund will invest in.")
    st.markdown("##")

    st.subheader("Simulation parameters")
    input_simulation_runs= st.number_input(label="# of funds to simulate", min_value=1, max_value=10000, step=1, value=2500,
    help="The total number of venture funds to simulate using the selected \
    paramters.")

# Content window
st.title("Venture Fund Simulator")
st.markdown("*Description of the simulator goes here. Built by Wes De \
Silvestro. Check out the [launch post](url) for more details.*")
st.markdown("##")

sim_data = simulate_multiple_funds([input_prob_dist_zero / 100.0,
                                    input_prob_dist_liquidation / 100.0,
                                    input_prob_dist_multiple / 100.0],
                                   input_liquidation_pct / 100.0,
                                   input_target_yoy_growth / 100.0,
                                   input_target_exit_time,
                                   input_portfolio_size,
                                   input_simulation_runs)

sim_returns_list = calculate_overall_fund_returns(sim_data)

st.subheader("Overview of simulated fund returns")
st.markdown("Given `{}` venture funds with a portfolio size of `{}` companies \
each, below is a summary of overall returns for each fund.".format(input_simulation_runs, input_portfolio_size))
stat_col1, stat_col2, stat_col3, stat_col4, stat_col5 = st.columns(5)
stat_col1.metric("25th Percentile Fund", "{0:.2f}x".format(np.quantile(sim_returns_list, q=0.25)))
stat_col2.metric("50th Percentile Fund", "{0:.2f}x".format(np.quantile(sim_returns_list, q=0.50)))
stat_col3.metric("75th Percentile Fund", "{0:.2f}x".format(np.quantile(sim_returns_list, q=0.75)))
stat_col4.metric("90th Percentile Fund", "{0:.2f}x".format(np.quantile(sim_returns_list, q=0.90)))
stat_col5.metric("99th Percentile Fund", "{0:.2f}x".format(np.quantile(sim_returns_list, q=0.99)))

# Configure necessary fonts
ssp_font_regular = font_manager.FontProperties(fname='./Source_Sans_Pro/SourceSansPro-Regular.ttf')
ssp_font_bold = font_manager.FontProperties(fname='./Source_Sans_Pro/SourceSansPro-Bold.ttf')
ssp_font_semibold = font_manager.FontProperties(fname='./Source_Sans_Pro/SourceSansPro-SemiBold.ttf')

fig, ax = plt.subplots(figsize=(12, 4))
fig.patch.set_facecolor("#000000")
fig.patch.set_alpha(0)
ax.patch.set_facecolor("#000000")
ax.patch.set_alpha(0)
ax.hist(x=sim_returns_list, range=(1,100), rwidth=1, color="#14BAA6")
ax.tick_params(color='white', labelcolor="white")
for spine in ax.spines.values():
        spine.set_edgecolor('white')
plt.title("Histogram of Fund Return Multiples", color="white",
          fontproperties=ssp_font_bold, fontsize=18)
plt.xlabel("Return Multiple", color="white", fontproperties=ssp_font_semibold, fontsize=14)
plt.ylabel("Frequency", color="white", fontproperties=ssp_font_semibold, fontsize=14)
plt.setp(ax.get_xticklabels(), fontproperties=ssp_font_regular, fontsize=13)
plt.setp(ax.get_yticklabels(), fontproperties=ssp_font_regular, fontsize=13)
st.pyplot(fig)
st.markdown("###")


st.subheader("Comparison against industry benchmarks")
st.markdown("In addition to understanding what the topline return multiples are \
for the simulated funds, it's helpful to understand how the funds stack up \
against industry benchmarks for what investors expect of the VC asset class. \
Most limited partners (LPs) that provide capital to VC funds are looking for a \
**3x return**. Anything less than that and the risk-adjusted return would not \
justify investing in venture capital funds.")

bm_col1, bm_col2, bm_col3, bm_col4 = st.columns(4)
bm_col1.metric("% funds with ≥ 3x return", "{0:.1f}%".format((len([x for x in sim_returns_list if x >= 3])/len(sim_returns_list))*100))
bm_col2.metric("% funds with 2-3x return", "{0:.1f}%".format((len([x for x in sim_returns_list if (x < 3) and (x >= 2)])/len(sim_returns_list))*100))
bm_col3.metric("% funds with 1-2x return", "{0:.1f}%".format((len([x for x in sim_returns_list if (x < 2) and (x >= 1)])/len(sim_returns_list))*100))
bm_col4.metric("% funds with < 1x return", "{0:.1f}%".format((len([x for x in sim_returns_list if x < 1])/len(sim_returns_list))*100))
