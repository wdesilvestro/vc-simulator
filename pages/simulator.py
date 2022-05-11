import streamlit as st
from library import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager


def app():
    # Input sidebar
    with st.sidebar:
        st.title("Configure simulation parameters")

        st.subheader("Probability of return multiples")
        st.caption("All sliders must sum to 100% in total.")
        # TODO: Throw an error if it doesn't sum to less than 100.
        input_prob_dist_zero = st.slider(label="% of companies that return 0x", min_value=0, max_value=100, step=1, value=33,
        help="The percentage of companies that are expected to return nothing on the \
        original investment.")
        input_prob_dist_liquidation = st.slider(label="% of companies that <1x", min_value=0, max_value=100, step=1, value=33,
        help="The percentage of companies that are expected to be liquidated and return \
        some fraction of the original investment.")
        input_prob_dist_multiple = st.slider(label="% of companies that ≥1x", min_value=0, max_value=100, step=1, value=33,
        help="The percentage of companies that are expected to return greater than or \
        equal to the original investment.")
        # TODO: Reset button
        st.markdown("##")

        st.subheader("Investment parameters")
        input_liquidation_pct = st.number_input(label="% of original investment \
        recovered in event of liquidation", min_value=1.0, max_value=100.0, step=5.0, value=80.0,
        help="In the event a portfolio company must be liquidated, this is the expected \
        percentage of the original investment that will be recovered.")
        input_target_yoy_growth = st.number_input(label="Target % for YoY growth", min_value=0.1, max_value=300.0, step=1.0, value=25.0,
        help="The targeted percentage of year-over-year growth that the venture funds \
        are seeking with their investments.")
        input_target_exit_time = st.number_input(label="Target # of years until an investment exits", min_value=1, max_value=100, step=1, value=5,
        help="The targeted number of years by which the venture fund would like to exit \
        an investment.")
        st.markdown("*Given the above parameters, `α = {:.3f}`.*".format(calculate_alpha(input_target_yoy_growth / 100.0, input_target_exit_time)))
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
        input_simulation_runs= st.number_input(label="# of funds to simulate", min_value=1, max_value=100000, step=1, value=2500,
        help="The total number of venture funds to simulate using the selected \
        paramters.")

    # Throw error, warning, and info boxes
    prob_dist_sum = input_prob_dist_zero + input_prob_dist_liquidation + input_prob_dist_multiple
    if prob_dist_sum > 100:
        st.error("The probability of return multiple sliders are cumulative greater \
        than 100%. Please adjust them accordingly.")
    if (prob_dist_sum < 100) and (100 - prob_dist_sum > 1):
        st.warning("The probability of return multiple sliders do not cumulatively \
        add up to 100. The remaining percentage points will be proportionally \
        distributed across each outcome.")

    if input_target_exit_time > input_fund_lifespan:
        st.warning("The target exit time for an investment is greater than the \
        fund's lifespan. Due to the way the Simulator is written, the simulation \
        will still run, but please be aware that this scenario would be not possible \
        in the real world (at least not without a fund extension granted by the LPs).")

    if input_simulation_runs > 2500:
        st.info("Please be aware that running more than 2,500 fund simulations at a \
        time is very resource intensive and will take a while for Streamlit to process.")


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

    raw_returns_list = calculate_raw_fund_returns(sim_data)
    actual_returns_list = calculate_actual_fund_returns(raw_returns_list,
                                                        input_management_fee_percent
                                                        / 100.0,
                                                        input_fund_lifespan)

    st.subheader("Overview of simulated fund returns")
    st.markdown("Given `{}` venture funds with a portfolio size of `{}` companies \
    each, below is a summary of overall returns for each fund after management fees \
    have been deducted.".format(input_simulation_runs, input_portfolio_size))

    # text_col1, text_col2, text_col3, text_col4, text_col5 = st.columns(5)
    # text_col1.markdown("##### 25th Percentile")
    # text_col2.markdown("##### 50th Percentile")
    # text_col3.markdown("##### 75th Percentile")
    # text_col4.markdown("##### 90th Percentile")
    # text_col5.markdown("##### 99th Percentile")

    # raw_stat_col1, raw_stat_col2, raw_stat_col3, raw_stat_col4, raw_stat_col5 = st.columns(5)
    # raw_stat_col1.metric("Raw return", "{0:.1f}x".format(np.quantile(raw_returns_list, q=0.25)))
    # raw_stat_col2.metric("Raw return", "{0:.1f}x".format(np.quantile(raw_returns_list, q=0.50)))
    # raw_stat_col3.metric("Raw return", "{0:.1f}x".format(np.quantile(raw_returns_list, q=0.75)))
    # raw_stat_col4.metric("Raw return", "{0:.1f}x".format(np.quantile(raw_returns_list, q=0.90)))
    # raw_stat_col5.metric("Raw return", "{0:.1f}x".format(np.quantile(raw_returns_list, q=0.99)))


    # actual_stat_col1, actual_stat_col2, actual_stat_col3, actual_stat_col4, actual_stat_col5 = st.columns(5)
    # actual_stat_col1.metric("Post-mgmt fee", "{0:.1f}x".format(np.quantile(actual_returns_list, q=0.25)))
    # actual_stat_col2.metric("Post-mgmt fee", "{0:.1f}x".format(np.quantile(actual_returns_list, q=0.50)))
    # actual_stat_col3.metric("Post-mgmt fee", "{0:.1f}x".format(np.quantile(actual_returns_list, q=0.75)))
    # actual_stat_col4.metric("Post-mgmt fee", "{0:.1f}x".format(np.quantile(actual_returns_list, q=0.90)))
    # actual_stat_col5.metric("Post-mgmt fee", "{0:.1f}x".format(np.quantile(actual_returns_list, q=0.99)))


    actual_quantile_25 = np.quantile(actual_returns_list, q=0.25)
    actual_quantile_50 = np.quantile(actual_returns_list, q=0.50)
    actual_quantile_75 = np.quantile(actual_returns_list, q=0.75)
    actual_quantile_90 = np.quantile(actual_returns_list, q=0.90)
    actual_quantile_99 = np.quantile(actual_returns_list, q=0.99)

    actual_stat_col1, actual_stat_col2, actual_stat_col3, actual_stat_col4, actual_stat_col5 = st.columns(5)
    actual_stat_col1.metric("25th Percentile", "{0:.1f}x".format(actual_quantile_25))
    actual_stat_col2.metric("50th Percentile", "{0:.1f}x".format(actual_quantile_50))
    actual_stat_col3.metric("75th Percentile", "{0:.1f}x".format(actual_quantile_75))
    actual_stat_col4.metric("90th Percentile", "{0:.1f}x".format(actual_quantile_90))
    actual_stat_col5.metric("99th Percentile", "{0:.1f}x".format(actual_quantile_99))

    # Configure necessary fonts
    ssp_font_regular = font_manager.FontProperties(fname='./Source_Sans_Pro/SourceSansPro-Regular.ttf')
    ssp_font_bold = font_manager.FontProperties(fname='./Source_Sans_Pro/SourceSansPro-Bold.ttf')
    ssp_font_semibold = font_manager.FontProperties(fname='./Source_Sans_Pro/SourceSansPro-SemiBold.ttf')

    fig, ax = plt.subplots(figsize=(12, 4))
    fig.patch.set_facecolor("#000000")
    fig.patch.set_alpha(0)
    ax.patch.set_facecolor("#000000")
    ax.patch.set_alpha(0)
    ax.hist(x=actual_returns_list, range=(1,100), rwidth=1, color="#14BAA6")
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
    justify investing in the venture capital asset class.")

    bm_col1, bm_col2, bm_col3, bm_col4 = st.columns(4)
    bm_col1.metric("% funds with ≥ 3x return", "{0:.1f}%".format((len([x for x in actual_returns_list if x >= 3])/len(actual_returns_list))*100))
    bm_col2.metric("% funds with 2-3x return", "{0:.1f}%".format((len([x for x in actual_returns_list if (x < 3) and (x >= 2)])/len(actual_returns_list))*100))
    bm_col3.metric("% funds with 1-2x return", "{0:.1f}%".format((len([x for x in actual_returns_list if (x < 2) and (x >= 1)])/len(actual_returns_list))*100))
    bm_col4.metric("% funds with < 1x return", "{0:.1f}%".format((len([x for x in actual_returns_list if x < 1])/len(actual_returns_list))*100))

    st.markdown("We can also look at the compounded annual growth rate (CAGR) to \
    understand what the year-to-year growth of the simulated funds are. The numbers \
    below reflect a fund lifespan of `{}` years. Keep in mind that the longer the \
    fund lifespan, the higher the multiple of return listed above will expected to \
    be.".format(input_fund_lifespan))

    cagr_quantile_25 = 100 * convert_moic_to_cagr(actual_quantile_25, input_fund_lifespan)
    cagr_quantile_50 = 100 * convert_moic_to_cagr(actual_quantile_50, input_fund_lifespan)
    cagr_quantile_75 = 100 * convert_moic_to_cagr(actual_quantile_75, input_fund_lifespan)
    cagr_quantile_90 = 100 * convert_moic_to_cagr(actual_quantile_90, input_fund_lifespan)
    cagr_quantile_99 = 100 * convert_moic_to_cagr(actual_quantile_99, input_fund_lifespan)

    cagr_stat_col1, cagr_stat_col2, cagr_stat_col3, cagr_stat_col4, cagr_stat_col5 = st.columns(5)
    cagr_stat_col1.metric("25th Percentile", "{0:.1f}%".format(cagr_quantile_25))
    cagr_stat_col2.metric("50th Percentile", "{0:.1f}%".format(cagr_quantile_50))
    cagr_stat_col3.metric("75th Percentile", "{0:.1f}%".format(cagr_quantile_75))
    cagr_stat_col4.metric("90th Percentile", "{0:.1f}%".format(cagr_quantile_90))
    cagr_stat_col5.metric("99th Percentile", "{0:.1f}%".format(cagr_quantile_99))

    st.markdown("Below are two scatterplots, one showing funding returns with \
    multiples from 0x to 50x and the second showing fund returns from 51x and \
    greater. In the first plot, anything above the red line passes the industry \
    benchmark of achieving at least a 3x return.")
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    fig2.patch.set_facecolor("#000000")
    fig2.patch.set_alpha(0)
    ax2.patch.set_facecolor("#000000")
    ax2.patch.set_alpha(0)
    ax2.scatter(x=np.arange(0,len(actual_returns_list)), y=actual_returns_list,
                color="#14BAA6", s=3)
    plt.ylim(0,50)
    plt.axhline(y=3, color='#ef4444', linestyle='dashed', linewidth=3)
    ax2.tick_params(color='white', labelcolor="white")
    for spine in ax2.spines.values():
            spine.set_edgecolor('white')
    plt.title("Scatterplot of Fund Return Multiples (0-50x)", color="white",
            fontproperties=ssp_font_bold, fontsize=18)
    plt.xlabel("Fund #", color="white", fontproperties=ssp_font_semibold, fontsize=14)
    plt.ylabel("Multiple", color="white", fontproperties=ssp_font_semibold, fontsize=14)
    plt.setp(ax2.get_xticklabels(), fontproperties=ssp_font_regular, fontsize=13)
    plt.setp(ax2.get_yticklabels(), fontproperties=ssp_font_regular, fontsize=13)
    st.pyplot(fig2)
    st.write()

    fig3, ax3 = plt.subplots(figsize=(12, 6))
    fig3.patch.set_facecolor("#000000")
    fig3.patch.set_alpha(0)
    ax3.patch.set_facecolor("#000000")
    ax3.patch.set_alpha(0)
    filtered_list = list(filter(lambda x: x > 50, actual_returns_list))
    ax3.scatter(x=np.arange(0,len(filtered_list)), y=filtered_list, color="#14BAA6", s=50)
    plt.ylim(0,np.max(actual_returns_list) + 100)
    ax3.tick_params(color='white', labelcolor="white")
    for spine in ax3.spines.values():
            spine.set_edgecolor('white')
    plt.title("Scatterplot of Fund Return Multiples (>50x)", color="white",
            fontproperties=ssp_font_bold, fontsize=18)
    plt.xlabel("Fund #", color="white", fontproperties=ssp_font_semibold, fontsize=14)
    plt.ylabel("Multiple", color="white", fontproperties=ssp_font_semibold, fontsize=14)
    plt.setp(ax3.get_xticklabels(), fontproperties=ssp_font_regular, fontsize=13)
    plt.setp(ax3.get_yticklabels(), fontproperties=ssp_font_regular, fontsize=13)
    st.pyplot(fig3)
    st.markdown("###")


    fund_analysis_list = analyze_fund_returns(sim_data, raw_returns_list, input_portfolio_size)

    st.subheader("Where the returns are coming from")
    st.markdown("We can also investigate where the returns are coming from *within* \
    each venture fund (i.e., what investments are actually driving overall returns). \
    We'll split our simulated funds into four buckets: <1x return, 1-2x return, 2-3x \
    return, and ≥ 3x return.")
    st.markdown("First, we'll look at the *composition* of each each bucket in terms \
    of the types of companies within each fund's portfolio. Below is a chart showing \
    how many failed (<1x), breakeven (1-2x), moderately sucessful (2-3x), and winner \
    (≥3x) companies make up each bucket.")

    fig4, ax4 = plt.subplots(figsize=(12, 6))
    fig4.patch.set_facecolor("#000000")
    fig4.patch.set_alpha(0)
    ax4.patch.set_facecolor("#000000")
    ax4.patch.set_alpha(0)
    labels = ['Failed Fund', 'Breakeven Fund', 'Moderately Successful Fund', 'Winner Fund']

    pct_comp_less_1x = 100 * get_averages_for_variable_across_buckets(fund_analysis_list, 'pct_comp_less_1x')
    pct_comp_1x_2x = 100 * get_averages_for_variable_across_buckets(fund_analysis_list, 'pct_comp_1x_2x')
    pct_comp_2x_3x = 100 * get_averages_for_variable_across_buckets(fund_analysis_list, 'pct_comp_2x_3x')
    pct_comp_greateq_3x = 100 * get_averages_for_variable_across_buckets(fund_analysis_list, 'pct_comp_greateq_3x')

    ax4.bar(labels, pct_comp_less_1x, label='Companies returning < 1x', color="#ef4444")
    ax4.bar(labels, pct_comp_1x_2x, label='Companies returning 1-2x',
            bottom=pct_comp_less_1x, color="#eab308")
    ax4.bar(labels, pct_comp_2x_3x, label='Companies returning 2-3x',
            bottom=pct_comp_less_1x+pct_comp_1x_2x, color="#3b82f6")
    ax4.bar(labels, pct_comp_greateq_3x, label='Companies returning ≥3x',
            bottom=pct_comp_less_1x+pct_comp_1x_2x+pct_comp_2x_3x, color="#22c55e")
    ax4.tick_params(color='white', labelcolor="white")
    plt.ylim(0,105,1)
    for spine in ax4.spines.values():
            spine.set_edgecolor('white')
    plt.title("Breakdown of Fund Composition", color="white",
            fontproperties=ssp_font_bold, fontsize=18)
    plt.xlabel("Bucket of Fund", color="white", fontproperties=ssp_font_semibold, fontsize=14)
    plt.ylabel("% of Fund Composition", color="white", fontproperties=ssp_font_semibold, fontsize=14)
    ax4.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=5,
            frameon=False)
    plt.setp(ax4.get_legend().get_texts(), color='white', fontproperties=ssp_font_regular,
            fontsize=12)
    plt.setp(ax4.get_xticklabels(), fontproperties=ssp_font_regular, fontsize=13)
    plt.setp(ax4.get_yticklabels(), fontproperties=ssp_font_regular, fontsize=13)
    st.pyplot(fig4)

    st.markdown("Next, we'll compare the *source of returns* for each bucket in \
    terms of what companies are driving overall fund performance. Below is a chart \
    showing the percentage of overall fund returns that are attributable to each \
    type of company within a particular bucket of funds.")


    fig5, ax5 = plt.subplots(figsize=(12, 6))
    fig5.patch.set_facecolor("#000000")
    fig5.patch.set_alpha(0)
    ax5.patch.set_facecolor("#000000")
    ax5.patch.set_alpha(0)

    pct_return_less_1x = 100 * get_averages_for_variable_across_buckets(fund_analysis_list, 'pct_return_less_1x')
    pct_return_1x_2x = 100 * get_averages_for_variable_across_buckets(fund_analysis_list, 'pct_return_1x_2x')
    pct_return_2x_3x = 100 * get_averages_for_variable_across_buckets(fund_analysis_list, 'pct_return_2x_3x')
    pct_return_greateq_3x = 100 * get_averages_for_variable_across_buckets(fund_analysis_list, 'pct_return_greateq_3x')

    ax5.bar(labels, pct_return_less_1x, label='Companies returning < 1x', color="#ef4444")
    ax5.bar(labels, pct_return_1x_2x, label='Companies returning 1-2x',
            bottom=pct_return_less_1x, color="#eab308")
    ax5.bar(labels, pct_return_2x_3x, label='Companies returning 2-3x',
            bottom=pct_return_less_1x+pct_return_1x_2x, color="#3b82f6")
    ax5.bar(labels, pct_return_greateq_3x, label='Companies returning ≥3x',
            bottom=pct_return_less_1x+pct_return_1x_2x+pct_return_2x_3x, color="#22c55e")
    ax5.tick_params(color='white', labelcolor="white")
    plt.ylim(0,105,1)
    for spine in ax5.spines.values():
            spine.set_edgecolor('white')
    plt.title("Breakdown of Fund Returns", color="white",
            fontproperties=ssp_font_bold, fontsize=18)
    plt.xlabel("Bucket of Fund", color="white", fontproperties=ssp_font_semibold, fontsize=14)
    plt.ylabel("% of Fund Returns", color="white", fontproperties=ssp_font_semibold, fontsize=14)
    ax5.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=5,
            frameon=False)
    plt.setp(ax5.get_legend().get_texts(), color='white', fontproperties=ssp_font_regular,
            fontsize=12)
    plt.setp(ax5.get_xticklabels(), fontproperties=ssp_font_regular, fontsize=13)
    plt.setp(ax5.get_yticklabels(), fontproperties=ssp_font_regular, fontsize=13)
    st.pyplot(fig5)
    st.markdown("As you can see in the first chart, the composition of the \
    funds is relatively similar across each bucket. However, there is a dramatic \
    difference in terms of the breakdown of returns as seen in the second chart. The \
    vast majority of the returns for funds that at least breakeven comes from \
    'winning' companies that at least triple in value from initial investment to \
    exit. Nearly all the returns come from a small set of outlier investments.")
