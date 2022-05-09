import numpy as np
import pandas as pd
import powerlaw

def calculate_alpha(target_yoy_growth, target_exit_time):
    # Convert annually compounded growth rate (YoY) to continuously compounded
    target_cont_comp_growth = np.log(1 + target_yoy_growth)

    return (1/(target_cont_comp_growth * target_exit_time) + 1)

def simulate_single_draw(alpha, liquidation_pct, prob_dist):
    # Ensure the probabilities sum to one by proportionally distributing
    # remainder across array
    prob_array = np.array(prob_dist)
    prob_array = prob_array/prob_array.sum(axis=0, keepdims=1)

    # Perform a weighted, random draw
    draw = np.random.choice(["ZERO", "LIQUIDATION", "MULTIPLE"], 1, p=prob_array)[0]
    if draw == "ZERO":
        return 0
    elif draw == "LIQUIDATION":
        return liquidation_pct
    else:
        dist = powerlaw.Power_Law(xmin=1, parameters=[alpha])
        return dist.generate_random(1)[0]

def simulate_multiple_funds(prob_dist, liquidation_pct, target_yoy_growth, target_exit_time, portfolio_size, simulation_runs=2500):
    # Calculate the appropriate alpha given the inputs
    alpha = calculate_alpha(target_yoy_growth, target_exit_time)

    # Simuate i=simulation_runs of funds with a n=portfolio_size portfolio size
    simulated_funds_list = [[simulate_single_draw(alpha, liquidation_pct, prob_dist) for i in range(portfolio_size)] for j in range(int(simulation_runs))]

    return simulated_funds_list

def calculate_overall_fund_returns(simulation_data):
    overall_returns_list = []
    for fund in simulation_data:
        fund_array = np.array(fund)
        fund_return = (fund_array.sum() - len(fund_array)) / len(fund_array)
        overall_returns_list.append(fund_return)
    return overall_returns_list
