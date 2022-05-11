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
        input_average_yoy_growth = st.number_input(label="Average % for YoY growth", min_value=0.1, max_value=300.0, step=1.0, value=25.0,
        help="The average percentage of year-over-year growth that the venture funds \
        are seeking with their investments.")
        input_average_exit_time = st.number_input(label="Average # of years until an investment exits", min_value=1, max_value=100, step=1, value=5,
        help="The average number of years by which the venture fund would like to exit \
        an investment.")
        st.markdown("*Given the above parameters, `α = {:.3f}`.*".format(calculate_alpha(input_average_yoy_growth / 100.0, input_average_exit_time)))
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

    if input_simulation_runs > 2500:
        st.info("Please be aware that running more than 2,500 fund simulations at a \
        time is very resource intensive and will take a while for Streamlit to process.")


    # SECTION: TITLE
    st.title("Venture Fund Simulator")
    st.markdown("##")

    sim_data = simulate_multiple_funds([input_prob_dist_zero / 100.0,
                                        input_prob_dist_liquidation / 100.0,
                                        input_prob_dist_multiple / 100.0],
                                    input_liquidation_pct / 100.0,
                                    input_average_yoy_growth / 100.0,
                                    input_average_exit_time,
                                    input_portfolio_size,
                                    input_simulation_runs)

    raw_returns_list = calculate_raw_fund_returns(sim_data)
    actual_returns_list = calculate_actual_fund_returns(raw_returns_list,
                                                        input_management_fee_percent
                                                        / 100.0,
                                                        input_fund_lifespan)

    # Configure necessary fonts for matplotlib
    ssp_font_regular = font_manager.FontProperties(fname='./Source_Sans_Pro/SourceSansPro-Regular.ttf')
    ssp_font_bold = font_manager.FontProperties(fname='./Source_Sans_Pro/SourceSansPro-Bold.ttf')
    ssp_font_semibold = font_manager.FontProperties(fname='./Source_Sans_Pro/SourceSansPro-SemiBold.ttf')


    # SECTION: OVERVIEW OF SIMULATED FUND RETURNS
    st.subheader("I. Overview of simulated fund returns")

    st.markdown("#### A) Quick overview")
    st.markdown("Given `{}` venture funds with a portfolio size of `{}` \
    companies each, below is a breakdown of fund returns after the `{}%` \
    management fee has been deducted.".format(input_simulation_runs,
                                              input_portfolio_size,
                                              input_management_fee_percent))

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

    fig_overview, ax_overview = plt.subplots(figsize=(12, 4))
    fig_overview.patch.set_facecolor("#000000")
    fig_overview.patch.set_alpha(0)
    ax_overview.patch.set_facecolor("#000000")
    ax_overview.patch.set_alpha(0)
    ax_overview.hist(x=actual_returns_list, range=(1,100), rwidth=1, color="#14BAA6")
    ax_overview.tick_params(color='white', labelcolor="white")
    for spine in ax_overview.spines.values():
            spine.set_edgecolor('white')
    plt.title("Histogram of Fund Return Multiples", color="white",
            fontproperties=ssp_font_bold, fontsize=18)
    plt.xlabel("Return Multiple", color="white", fontproperties=ssp_font_semibold, fontsize=14)
    plt.ylabel("Frequency", color="white", fontproperties=ssp_font_semibold, fontsize=14)
    plt.setp(ax_overview.get_xticklabels(), fontproperties=ssp_font_regular, fontsize=13)
    plt.setp(ax_overview.get_yticklabels(), fontproperties=ssp_font_regular, fontsize=13)
    st.pyplot(fig_overview)

    cagr_quantile_25 = 100 * convert_moic_to_cagr(actual_quantile_25, input_fund_lifespan)
    cagr_quantile_50 = 100 * convert_moic_to_cagr(actual_quantile_50, input_fund_lifespan)
    cagr_quantile_75 = 100 * convert_moic_to_cagr(actual_quantile_75, input_fund_lifespan)
    cagr_quantile_90 = 100 * convert_moic_to_cagr(actual_quantile_90, input_fund_lifespan)
    cagr_quantile_99 = 100 * convert_moic_to_cagr(actual_quantile_99, input_fund_lifespan)

    st.markdown("#### B) Percentile ranking")
    st.markdown("Below is a percentile ranking of the funds' compounded annual \
    growth rates (CAGR) from worst to best.")
    cagr_stat_col1, cagr_stat_col2, cagr_stat_col3, cagr_stat_col4, cagr_stat_col5 = st.columns(5)
    cagr_stat_col1.metric("25th Percentile", "{0:.1f}%".format(cagr_quantile_25))
    cagr_stat_col2.metric("50th Percentile", "{0:.1f}%".format(cagr_quantile_50))
    cagr_stat_col3.metric("75th Percentile", "{0:.1f}%".format(cagr_quantile_75))
    cagr_stat_col4.metric("90th Percentile", "{0:.1f}%".format(cagr_quantile_90))
    cagr_stat_col5.metric("99th Percentile", "{0:.1f}%".format(cagr_quantile_99))
    st.markdown("###")


    # SECTION: COMPARISON AGAINST INDUSTRY BENCHMARKS
    st.subheader("II. Comparison against industry benchmarks")
    st.markdown("In addition to understanding what the topline return multiples \
    are, it can be helpful to undertand how the funds stack up against the \
    industry benchmarks for what's expected of the VC asset class.")

    st.markdown("#### A) Comparison against the stock market")
    stock_benchmark = (1.10) ** input_fund_lifespan
    st.markdown("The simplest approach would be to compare the funds' returns \
    against investing the money into the stock market for the equivalent period \
    of time. The stock market has median returns of about 10% each year. Given a \
    fund lifespan of `{}` years, the simulated funds will need to return at \
    least a `{:.1f}x` multiple to match the stock market's average performance.".format(input_fund_lifespan, (1.10) ** input_fund_lifespan))
    st.markdown("Below are charts of the simulated fund return multiples. To \
    make viewing the data easier, it is split into two different scatterplots: \
    the first showing return multiples from 0-50x and the second for 51x and \
    greater. Note that anything above the red line achieves the desired `{:.1f}x` \
    benchmark.".format(stock_benchmark))
    st.markdown("As can be seen in the charts below, `{:.1f}%` of all simulated \
    funds at least matched the stock market's \
    performance.".format((len(list(filter(lambda x: x > stock_benchmark,
                                          actual_returns_list))) /
                          len(actual_returns_list)) * 100))

    fig_lower_mult, ax_lower_mult = plt.subplots(figsize=(12, 6))
    fig_lower_mult.patch.set_facecolor("#000000")
    fig_lower_mult.patch.set_alpha(0)
    ax_lower_mult.patch.set_facecolor("#000000")
    ax_lower_mult.patch.set_alpha(0)
    ax_lower_mult.scatter(x=np.arange(0,len(actual_returns_list)), y=actual_returns_list,
                color="#14BAA6", s=3)
    plt.ylim(0,50)
    plt.axhline(y=stock_benchmark, color='#ef4444', linestyle='dashed', linewidth=3)
    ax_lower_mult.tick_params(color='white', labelcolor="white")
    for spine in ax_lower_mult.spines.values():
            spine.set_edgecolor('white')
    plt.title("Scatterplot of Fund Return Multiples (0-50x)", color="white",
            fontproperties=ssp_font_bold, fontsize=18)
    plt.xlabel("Fund #", color="white", fontproperties=ssp_font_semibold, fontsize=14)
    plt.ylabel("Multiple", color="white", fontproperties=ssp_font_semibold, fontsize=14)
    plt.setp(ax_lower_mult.get_xticklabels(), fontproperties=ssp_font_regular, fontsize=13)
    plt.setp(ax_lower_mult.get_yticklabels(), fontproperties=ssp_font_regular, fontsize=13)
    st.pyplot(fig_lower_mult)


    fig_upper_mult, ax_upper_mult = plt.subplots(figsize=(12, 6))
    fig_upper_mult.patch.set_facecolor("#000000")
    fig_upper_mult.patch.set_alpha(0)
    ax_upper_mult.patch.set_facecolor("#000000")
    ax_upper_mult.patch.set_alpha(0)
    filtered_list = list(filter(lambda x: x > 50, actual_returns_list))
    ax_upper_mult.scatter(x=np.arange(0,len(filtered_list)), y=filtered_list, color="#14BAA6", s=50)
    plt.ylim(0,np.max(actual_returns_list) + 100)
    plt.axhline(y=stock_benchmark, color='#ef4444', linestyle='dashed', linewidth=3)
    ax_upper_mult.tick_params(color='white', labelcolor="white")
    for spine in ax_upper_mult.spines.values():
            spine.set_edgecolor('white')
    plt.title("Scatterplot of Fund Return Multiples (>50x)", color="white",
            fontproperties=ssp_font_bold, fontsize=18)
    plt.xlabel("Fund #", color="white", fontproperties=ssp_font_semibold, fontsize=14)
    plt.ylabel("Multiple", color="white", fontproperties=ssp_font_semibold, fontsize=14)
    plt.setp(ax_upper_mult.get_xticklabels(), fontproperties=ssp_font_regular, fontsize=13)
    plt.setp(ax_upper_mult.get_yticklabels(), fontproperties=ssp_font_regular, fontsize=13)
    st.pyplot(fig_upper_mult)
    st.markdown("###")


    fund_analysis_list = analyze_fund_returns(sim_data, raw_returns_list, input_portfolio_size)

    st.subheader("III. Analysis of the power law")
    st.markdown("VC returns notoriously follow a [power law \
    distribution](https://en.wikipedia.org/wiki/Power_law). This means that a \
    small percentage of companies will drive the vast majority of a portfolio's \
    returns. Likewise, a small percentage of funds will outperform all the rest.")
    st.markdown("We can visualize the power law in action by investigating where the \
    returns are coming from *within* each venture fund (i.e., what investments \
    are actually driving the overall portfolio returns). To do this, we'll split \
    our simulated funds into four performance buckets: funds that achieved a <1x \
    return, 1-2x return, 2-3x return, and ≥3x return. Below is a breakdown of \
    how many funds fall into each bucket.")

    bm_col1, bm_col2, bm_col3, bm_col4 = st.columns(4)
    bm_col1.metric("% funds with < 1x return", "{0:.1f}%".format((len([x for x in actual_returns_list if x < 1])/len(actual_returns_list))*100))
    bm_col2.metric("% funds with 1-2x return", "{0:.1f}%".format((len([x for x in actual_returns_list if (x < 2) and (x >= 1)])/len(actual_returns_list))*100))
    bm_col3.metric("% funds with 2-3x return", "{0:.1f}%".format((len([x for x in actual_returns_list if (x < 3) and (x >= 2)])/len(actual_returns_list))*100))
    bm_col4.metric("% funds with ≥ 3x return", "{0:.1f}%".format((len([x for x in actual_returns_list if x >= 3])/len(actual_returns_list))*100))

    st.markdown("#### A) Composition of fund returns")
    st.markdown("Next, we'll look at the composition of each performance bucket \
    in terms of the types of companies that make up each bucket. We'll \
    categorize companies in the same way we categorized funds: by return. \
    There will be four types of companies in our analysis: failed (<1x return), \
    breakeven (1-2x return), moderately successful (2-3x), and winner (≥3x \
    return) companies. Below is a chart showing the composition of each \
    bucket in terms of the relative proportions of companies within funds in that bucket.")

    fig_comp, ax_comp = plt.subplots(figsize=(12, 6))
    fig_comp.patch.set_facecolor("#000000")
    fig_comp.patch.set_alpha(0)
    ax_comp.patch.set_facecolor("#000000")
    ax_comp.patch.set_alpha(0)
    labels = ['Failed Fund', 'Breakeven Fund', 'Moderately Successful Fund', 'Winner Fund']

    pct_comp_less_1x = 100 * get_averages_for_variable_across_buckets(fund_analysis_list, 'pct_comp_less_1x')
    pct_comp_1x_2x = 100 * get_averages_for_variable_across_buckets(fund_analysis_list, 'pct_comp_1x_2x')
    pct_comp_2x_3x = 100 * get_averages_for_variable_across_buckets(fund_analysis_list, 'pct_comp_2x_3x')
    pct_comp_greateq_3x = 100 * get_averages_for_variable_across_buckets(fund_analysis_list, 'pct_comp_greateq_3x')

    ax_comp.bar(labels, pct_comp_less_1x, label='Companies returning < 1x', color="#ef4444")
    ax_comp.bar(labels, pct_comp_1x_2x, label='Companies returning 1-2x',
            bottom=pct_comp_less_1x, color="#eab308")
    ax_comp.bar(labels, pct_comp_2x_3x, label='Companies returning 2-3x',
            bottom=pct_comp_less_1x+pct_comp_1x_2x, color="#3b82f6")
    ax_comp.bar(labels, pct_comp_greateq_3x, label='Companies returning ≥3x',
            bottom=pct_comp_less_1x+pct_comp_1x_2x+pct_comp_2x_3x, color="#22c55e")
    ax_comp.tick_params(color='white', labelcolor="white")
    plt.ylim(0,105,1)
    for spine in ax_comp.spines.values():
            spine.set_edgecolor('white')
    plt.title("Breakdown of Fund Composition", color="white",
            fontproperties=ssp_font_bold, fontsize=18)
    plt.xlabel("Bucket of Fund", color="white", fontproperties=ssp_font_semibold, fontsize=14)
    plt.ylabel("% of Fund Composition", color="white", fontproperties=ssp_font_semibold, fontsize=14)
    ax_comp.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=5,
            frameon=False)
    plt.setp(ax_comp.get_legend().get_texts(), color='white', fontproperties=ssp_font_regular,
            fontsize=12)
    plt.setp(ax_comp.get_xticklabels(), fontproperties=ssp_font_regular, fontsize=13)
    plt.setp(ax_comp.get_yticklabels(), fontproperties=ssp_font_regular, fontsize=13)
    st.pyplot(fig_comp)

    st.markdown("#### B) Source of fund returns")
    st.markdown("Finally, we can look at the source of returns for each bucket. \
    Below is a chart showing the percentage of overall fund returns that are \
    attributable to each type of company within a given portfolio.")


    st.markdown("Next, we'll compare the *source of returns* for each bucket in \
    terms of what companies are driving overall fund performance. Below is a chart \
    showing the percentage of overall fund returns that are attributable to each \
    type of company within that fund, averaged for all funds in a given performance bucket.")


    fig_return, ax_return = plt.subplots(figsize=(12, 6))
    fig_return.patch.set_facecolor("#000000")
    fig_return.patch.set_alpha(0)
    ax_return.patch.set_facecolor("#000000")
    ax_return.patch.set_alpha(0)

    pct_return_less_1x = 100 * get_averages_for_variable_across_buckets(fund_analysis_list, 'pct_return_less_1x')
    pct_return_1x_2x = 100 * get_averages_for_variable_across_buckets(fund_analysis_list, 'pct_return_1x_2x')
    pct_return_2x_3x = 100 * get_averages_for_variable_across_buckets(fund_analysis_list, 'pct_return_2x_3x')
    pct_return_greateq_3x = 100 * get_averages_for_variable_across_buckets(fund_analysis_list, 'pct_return_greateq_3x')

    ax_return.bar(labels, pct_return_less_1x, label='Companies returning < 1x', color="#ef4444")
    ax_return.bar(labels, pct_return_1x_2x, label='Companies returning 1-2x',
            bottom=pct_return_less_1x, color="#eab308")
    ax_return.bar(labels, pct_return_2x_3x, label='Companies returning 2-3x',
            bottom=pct_return_less_1x+pct_return_1x_2x, color="#3b82f6")
    ax_return.bar(labels, pct_return_greateq_3x, label='Companies returning ≥3x',
            bottom=pct_return_less_1x+pct_return_1x_2x+pct_return_2x_3x, color="#22c55e")
    ax_return.tick_params(color='white', labelcolor="white")
    plt.ylim(0,105,1)
    for spine in ax_return.spines.values():
            spine.set_edgecolor('white')
    plt.title("Breakdown of Fund Returns", color="white",
            fontproperties=ssp_font_bold, fontsize=18)
    plt.xlabel("Bucket of Fund", color="white", fontproperties=ssp_font_semibold, fontsize=14)
    plt.ylabel("% of Fund Returns", color="white", fontproperties=ssp_font_semibold, fontsize=14)
    ax_return.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=5,
            frameon=False)
    plt.setp(ax_return.get_legend().get_texts(), color='white', fontproperties=ssp_font_regular,
            fontsize=12)
    plt.setp(ax_return.get_xticklabels(), fontproperties=ssp_font_regular, fontsize=13)
    plt.setp(ax_return.get_yticklabels(), fontproperties=ssp_font_regular, fontsize=13)
    st.pyplot(fig_return)

    st.markdown("As you can see in the above two charts, the composition of the \
    funds is relatively similar across each bucket with minor variation. \
    However, there is a dramatic difference in terms of the source of returns \
    for each bucket. For breakeven, moderately successful, and winner funds, the \
    vast majority of the returns are coming from 'winner' companies. Failed \
    funds have a more diverse source of returns precisely because they have a \
    smaller (but not by much) percentage of 'winner' companies within their portfolios.")
    st.markdown("This is the power law in action. A few 'winner' companies drive \
    almost all of the overall returns for a portfolio, and without those \
    companies, your fund is bust.")
