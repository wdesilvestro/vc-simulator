import numpy as np
import pandas as pd
import powerlaw

# FUNC: Given a target YoY growth rate and exit time, calculates the
# corresponding alpha parameter for the power law distribution
def calculate_alpha(target_yoy_growth, target_exit_time):
    # Convert annually compounded growth rate (YoY) to continuously compounded
    target_cont_comp_growth = np.log(1 + target_yoy_growth)

    return (1/(target_cont_comp_growth * target_exit_time) + 1)


# FUNC: Simulates a single draw (i.e., one portfolio company) from the power law
# distribution and predetermined probability distribution of return multiples
def simulate_single_draw(alpha, liquidation_pct, prob_dist):
    # Ensure the probabilities sum to one by proportionally distributing
    # remainder across array
    prob_array = np.array(prob_dist)
    prob_array = prob_array/prob_array.sum(axis=0, keepdims=1)

    # Perform a weighted, random draw
    draw = np.random.choice(["ZERO", "LIQUIDATION", "MULTIPLE"], 1, p=prob_array)[0]
    if draw == "ZERO":
        return 0.0
    elif draw == "LIQUIDATION":
        return liquidation_pct
    else:
        dist = powerlaw.Power_Law(xmin=1, parameters=[alpha])
        return dist.generate_random(1)[0]


# FUNC: Simulates several venture funds with a set portfolio size each using the
# simulate_single_draw function
def simulate_multiple_funds(prob_dist, liquidation_pct, target_yoy_growth, target_exit_time, portfolio_size, simulation_runs=2500):
    # Calculate the appropriate alpha given the inputs
    alpha = calculate_alpha(target_yoy_growth, target_exit_time)

    # Simuate i=simulation_runs of funds with a n=portfolio_size portfolio size
    simulated_funds_list = [[simulate_single_draw(alpha, liquidation_pct, prob_dist) for i in range(portfolio_size)] for j in range(int(simulation_runs))]

    return simulated_funds_list


def calculate_raw_fund_returns(simulation_data):
    raw_returns_list = []
    for fund in simulation_data:
        fund_array = np.array(fund)
        raw_fund_return = fund_array.sum() / len(fund_array)
        raw_returns_list.append(raw_fund_return)
    return raw_returns_list


def calculate_actual_fund_returns(raw_returns_list, mgmt_pct_fee, fund_lifespan):
    # Calculate what percentage of committed capital is leftover for actual investment
    pct_capital_investment = 1.0 - (mgmt_pct_fee * fund_lifespan)

    return(list(map(lambda x: x * pct_capital_investment, raw_returns_list)))


def analyze_fund_returns(simulation_data, raw_returns_list, portfolio_size):
   # Determine the bucket this fund gets sorted into
   fund_analysis_list = []
   for i in range(0, len(raw_returns_list)):
       if (raw_returns_list[i] < 1):
           fund_analysis_list.append({"bucket": "failure"})
       elif (raw_returns_list[i] >=1) and (raw_returns_list[i] < 2):
           fund_analysis_list.append({"bucket": "breakeven"})
       elif (raw_returns_list[i] >=2) and (raw_returns_list[i] < 3):
           fund_analysis_list.append({"bucket": "moderate_success"})
       else:
           fund_analysis_list.append({"bucket": "winner"})

   # Calculate the composition of each fund's portfolio companies
   for i in range(0, len(simulation_data)):
       fund_analysis_list[i]["pct_comp_less_1x"] =  len([x for x in simulation_data[i] if x < 1]) / portfolio_size
       fund_analysis_list[i]["pct_comp_1x_2x"] =  len([x for x in simulation_data[i] if (x >= 1) and (x < 2)]) / portfolio_size
       fund_analysis_list[i]["pct_comp_2x_3x"] =  len([x for x in simulation_data[i] if (x >= 2) and (x < 3)]) / portfolio_size
       fund_analysis_list[i]["pct_comp_greateq_3x"] =  len([x for x in simulation_data[i] if x >= 3]) / portfolio_size

   # Calculate the composition of each fund's returns
   for i in range(0, len(simulation_data)):
       if (raw_returns_list[i] == 0):
          fund_analysis_list[i]["pct_return_less_1x"] = 0.0
          fund_analysis_list[i]["pct_return_1x_2x"] = 0.0
          fund_analysis_list[i]["pct_return_2x_3x"] = 0.0
          fund_analysis_list[i]["pct_return_greateq_3x"] = 0.0
       else:
          fund_analysis_list[i]["pct_return_less_1x"] = np.sum([x for x in simulation_data[i] if x < 1]) / np.sum(simulation_data[i])
          fund_analysis_list[i]["pct_return_1x_2x"] = np.sum([x for x in simulation_data[i] if (x >= 1) and (x < 2)]) / np.sum(simulation_data[i])
          fund_analysis_list[i]["pct_return_2x_3x"] = np.sum([x for x in simulation_data[i] if (x >= 2) and (x < 3)]) / np.sum(simulation_data[i])
          fund_analysis_list[i]["pct_return_greateq_3x"] = np.sum([x for x in simulation_data[i] if x >= 3]) / np.sum(simulation_data[i])

   return fund_analysis_list


def get_averages_for_variable_across_buckets(fund_analysis_list, var):
    bucket_list = ['failure', 'breakeven', 'moderate_success', 'winner']
    results = []
    for bucket in bucket_list:
        result = np.average([x[var] for x in fund_analysis_list if x['bucket'] == bucket])
        results.append(result)
    return np.array(results)


def convert_moic_to_cagr(moic, fund_lifespan):
    return np.power(np.e, (np.log(moic))/fund_lifespan) - 1
