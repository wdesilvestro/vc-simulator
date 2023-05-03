import streamlit as st
from library import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager


def app():
    # SECTION: CONFIGURATION SIDEBAR
    with st.sidebar:
        st.title("Configure simulation parameters")

        st.subheader("Probability of return multiples")
        st.caption("All sliders must sum to 100% in total.")
        input_prob_dist_zero = st.slider(label="% of companies that return 0x", min_value=0, max_value=100, step=1, value=33,
        help="The percentage of companies that are expected to return nothing on the \
        original investment.")
        input_prob_dist_liquidation = st.slider(label="% of companies that <1x", min_value=0, max_value=100, step=1, value=33,
        help="The percentage of companies that are expected to be liquidated and return \
        some fraction of the original investment.")
        input_prob_dist_multiple = st.slider(label="% of companies that ≥1x", min_value=0, max_value=100, step=1, value=33,
        help="The percentage of companies that are expected to return greater than or \
        equal to the original investment.")
        st.markdown("##")

        st.subheader("Investment parameters")
        input_liquidation_pct = st.number_input(label="% of original investment \
        recovered in event of liquidation", min_value=1.0, max_value=100.0, step=5.0, value=80.0,
        help="In the event a portfolio company must be liquidated, this is the expected \
        percentage of the original investment that will be recovered.")
        input_average_yoy_growth_start = st.number_input(label="Start average % for YoY growth", min_value=0, max_value=500, step=1, value=15,
        help="The average percentage of year-over-year growth that the venture funds \
        are seeking with their investments.")
        input_average_yoy_growth_end = st.number_input(label="End average % for YoY growth", min_value=1, max_value=1000, step=1, value=30,
        help="The average percentage of year-over-year growth that the venture funds \
        are seeking with their investments.")
        input_average_exit_time = st.number_input(label="Average # of years until an investment exits", min_value=1, max_value=100, step=1, value=5,
        help="The average number of years by which the venture fund would like to exit \
        an investment.")
        st.markdown("##")

        st.subheader("Fund parameters")
        st.caption("Note that the Simulator assumes an equal investment into each \
        company in the portfolio, meaning there is no need to ask about check size \
        or total assets under management in order to calculate overall returns.")
        st.caption("Note that the Simulator also assumes a clawback provision is \
        present. Meaning that the VC will take no more of the profits than their \
        performance fee indicates they are owed.")
        input_portfolio_size= st.number_input(label="Portfolio size", min_value=1, max_value=10000, step=1, value=50,
        help="The number of companies that each venture fund will invest in.")
        input_management_fee_percent = st.number_input(label="% management fee", min_value=0.0, max_value=100.0, step=0.5, value=2.0,
        help="The percentage of committed capital charged annually as a \
        management fee.")
        input_carry_percent = st.number_input(label="% performance fee (carried interest)", min_value=0.0, max_value=100.0, step=1.0, value=20.0,
        help='The percentage of profits made on the principal investment that goes \
        to the venture capitalist for generating a positive return. This is commonly \
        called "carry" in the industry.')
        input_fund_lifespan = st.number_input(label="Fund lifespan in years", min_value=1, max_value=100, step=1, value=10,
        help="The amount of years the venture fund is expected to exist before all \
        capital must be returned to its limited partners.")
        st.markdown("##")

        st.subheader("Simulation parameters")
        input_simulation_runs= st.number_input(label="# of funds to simulate", min_value=1, max_value=100000, step=1, value=1000,
        help="The total number of venture funds to simulate using the selected \
        paramters.")


    # SECTION: ERRORS, WARNINGS, AND INFO INDICATORS
    prob_dist_sum = input_prob_dist_zero + input_prob_dist_liquidation + input_prob_dist_multiple
    if prob_dist_sum > 100:
        st.error("The probability of return multiple sliders are cumulative greater \
        than 100%. Please adjust them accordingly.")
    if (prob_dist_sum < 100) and (100 - prob_dist_sum > 1):
        st.warning("The probability of return multiple sliders do not cumulatively \
        add up to 100. The remaining percentage points will be proportionally \
        distributed across each outcome.")

    if input_average_exit_time > input_fund_lifespan:
        st.warning("The target exit time for an investment is greater than the \
        fund's lifespan. Due to the way the Simulator is written, the simulation \
        will still run, but please be aware that this scenario would be not possible \
        in the real world (at least not without a fund extension granted by the LPs).")

    if input_simulation_runs > 1000:
        st.info("Please be aware that running more than 2,500 fund simulations at a \
        time is very resource intensive and will take a while for Streamlit to process.")


    # SECTION: TITLE
    st.title("Venture Fund Simulator")
    st.markdown("##")

    growth_rates_list = list(range(input_average_yoy_growth_start,
                                   input_average_yoy_growth_end + 1))

    growth_rates_dict = {}

    for growth_rate in growth_rates_list:
        sim_data = simulate_multiple_funds([input_prob_dist_zero / 100.0,
                                            input_prob_dist_liquidation / 100.0,
                                            input_prob_dist_multiple / 100.0],
                                        input_liquidation_pct / 100.0,
                                        growth_rate / 100.0,
                                        input_average_exit_time,
                                        input_portfolio_size,
                                        input_simulation_runs)
        raw_returns_list = calculate_raw_fund_returns(sim_data)
        actual_returns_list = calculate_actual_fund_returns(raw_returns_list,
                                                            input_management_fee_percent
                                                            / 100.0,
                                                            input_fund_lifespan)

        actual_quantile_25 = np.quantile(actual_returns_list, q=0.25)
        actual_quantile_50 = np.quantile(actual_returns_list, q=0.50)
        actual_quantile_75 = np.quantile(actual_returns_list, q=0.75)
        actual_quantile_90 = np.quantile(actual_returns_list, q=0.90)
        actual_quantile_99 = np.quantile(actual_returns_list, q=0.99)
        growth_rates_dict[str(growth_rate)] = (np.average(actual_returns_list),
                                               actual_quantile_25,
                                               actual_quantile_50,
                                               actual_quantile_75,
                                               actual_quantile_90,
                                               actual_quantile_99)


    # Configure necessary fonts for matplotlib
    ssp_font_regular = font_manager.FontProperties(fname='./Source_Sans_Pro/SourceSansPro-Regular.ttf')
    ssp_font_bold = font_manager.FontProperties(fname='./Source_Sans_Pro/SourceSansPro-Bold.ttf')
    ssp_font_semibold = font_manager.FontProperties(fname='./Source_Sans_Pro/SourceSansPro-SemiBold.ttf')


    # # SECTION: OVERVIEW OF SIMULATED FUND RETURNS
    # st.subheader("I. Overview of simulated fund returns")

    # st.markdown("#### A) Quick overview")
    # st.markdown("Given `{}` venture funds with a portfolio size of `{}` \
    # companies each, below is a breakdown of fund returns after the `{}%` \
    # management fee has been deducted.".format(input_simulation_runs,
    #                                           input_portfolio_size,
    #                                           input_management_fee_percent))

    stock_benchmark = (1.10) ** input_fund_lifespan

    fig_average, ax_average = plt.subplots(figsize=(12, 4))
    fig_average.patch.set_facecolor("#000000")
    fig_average.patch.set_alpha(0)
    ax_average.patch.set_facecolor("#000000")
    ax_average.patch.set_alpha(0)
    ax_average.scatter(x=list(map(int, growth_rates_dict.keys())), y=[x[0] for x in growth_rates_dict.values()])
    plt.axhline(y=stock_benchmark, color='#ef4444', linestyle='dashed', linewidth=3)
    ax_average.tick_params(color='white', labelcolor="white")
    for spine in ax_average.spines.values():
            spine.set_edgecolor('white')
    plt.title("Scatterplot of Growth Rates vs. Average Return Multiples", color="white",
            fontproperties=ssp_font_bold, fontsize=18)
    plt.xlabel("Average annual growth rate", color="white", fontproperties=ssp_font_semibold, fontsize=14)
    plt.ylabel("Simulated fund return multiple", color="white", fontproperties=ssp_font_semibold, fontsize=14)
    plt.setp(ax_average.get_xticklabels(), fontproperties=ssp_font_regular, fontsize=13)
    plt.setp(ax_average.get_yticklabels(), fontproperties=ssp_font_regular, fontsize=13)
    st.pyplot(fig_average)


    fig_quartiles, ax_quartiles = plt.subplots(figsize=(12, 4))
    fig_quartiles.patch.set_facecolor("#000000")
    fig_quartiles.patch.set_alpha(0)
    ax_quartiles.patch.set_facecolor("#000000")
    ax_quartiles.patch.set_alpha(0)
    ax_quartiles.scatter(x=list(map(int, growth_rates_dict.keys())),
                         y=[x[1] for x in growth_rates_dict.values()],
                         label="25th percentile", color="#ef4444")
    ax_quartiles.scatter(x=list(map(int, growth_rates_dict.keys())),
                         y=[x[2] for x in growth_rates_dict.values()],
                         label="50th percentile", color="#eab308")
    ax_quartiles.scatter(x=list(map(int, growth_rates_dict.keys())),
                         y=[x[3] for x in growth_rates_dict.values()],
                         label="75th percentile", color="#3b82f6")
    ax_quartiles.scatter(x=list(map(int, growth_rates_dict.keys())),
                         y=[x[4] for x in growth_rates_dict.values()],
                         label="90th percentile", color="#22c55e")
    ax_quartiles.scatter(x=list(map(int, growth_rates_dict.keys())),
                         y=[x[5] for x in growth_rates_dict.values()],
                         label="99th percentile", color="#166534")

    plt.axhline(y=stock_benchmark, color='#ef4444', linestyle='dashed', linewidth=3)
    ax_quartiles.tick_params(color='white', labelcolor="white")
    for spine in ax_quartiles.spines.values():
            spine.set_edgecolor('white')
    plt.title("Scatterplot of Growth Rates vs. Return Multiples at Various Quartiles (0-1000x)", color="white",
            fontproperties=ssp_font_bold, fontsize=18)
    plt.ylim(0,1000)
    plt.xlabel("Annual growth rate", color="white", fontproperties=ssp_font_semibold, fontsize=14)
    plt.ylabel("Simulated fund return multiple", color="white", fontproperties=ssp_font_semibold, fontsize=14)
    ax_quartiles.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=5,
            frameon=False)
    plt.setp(ax_quartiles.get_legend().get_texts(), color='white', fontproperties=ssp_font_regular,
            fontsize=12)
    plt.setp(ax_quartiles.get_xticklabels(), fontproperties=ssp_font_regular, fontsize=13)
    plt.setp(ax_quartiles.get_yticklabels(), fontproperties=ssp_font_regular, fontsize=13)
    st.pyplot(fig_quartiles)


    fig_quartiles, ax_quartiles = plt.subplots(figsize=(12, 4))
    fig_quartiles.patch.set_facecolor("#000000")
    fig_quartiles.patch.set_alpha(0)
    ax_quartiles.patch.set_facecolor("#000000")
    ax_quartiles.patch.set_alpha(0)
    ax_quartiles.scatter(x=list(map(int, growth_rates_dict.keys())),
                         y=[x[1] for x in growth_rates_dict.values()],
                         label="25th percentile", color="#ef4444")
    ax_quartiles.scatter(x=list(map(int, growth_rates_dict.keys())),
                         y=[x[2] for x in growth_rates_dict.values()],
                         label="50th percentile", color="#eab308")
    ax_quartiles.scatter(x=list(map(int, growth_rates_dict.keys())),
                         y=[x[3] for x in growth_rates_dict.values()],
                         label="75th percentile", color="#3b82f6")
    ax_quartiles.scatter(x=list(map(int, growth_rates_dict.keys())),
                         y=[x[4] for x in growth_rates_dict.values()],
                         label="90th percentile", color="#22c55e")
    ax_quartiles.scatter(x=list(map(int, growth_rates_dict.keys())),
                         y=[x[5] for x in growth_rates_dict.values()],
                         label="99th percentile", color="#166534")
    plt.ylim(0,10)
    plt.axhline(y=stock_benchmark, color='#ef4444', linestyle='dashed', linewidth=3)
    ax_quartiles.tick_params(color='white', labelcolor="white")
    for spine in ax_quartiles.spines.values():
            spine.set_edgecolor('white')
    plt.title("Scatterplot of Growth Rates vs. Return Multiples at Various Quartiles (0-10x)", color="white",
            fontproperties=ssp_font_bold, fontsize=18)
    plt.xlabel("Annual growth rate", color="white", fontproperties=ssp_font_semibold, fontsize=14)
    plt.ylabel("Simulated fund return multiple", color="white", fontproperties=ssp_font_semibold, fontsize=14)
    ax_quartiles.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=5,
            frameon=False)
    plt.setp(ax_quartiles.get_legend().get_texts(), color='white', fontproperties=ssp_font_regular,
            fontsize=12)
    plt.setp(ax_quartiles.get_xticklabels(), fontproperties=ssp_font_regular, fontsize=13)
    plt.setp(ax_quartiles.get_yticklabels(), fontproperties=ssp_font_regular, fontsize=13)
    st.pyplot(fig_quartiles)
