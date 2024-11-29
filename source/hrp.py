import pandas as pd
import numpy as np
import riskfolio as rp

def calculate_hrp_weights(prices_close, rolling = 50):
    weights = pd.concat([prices_close.apply(lambda x: 1 / len(x.dropna()), axis = 1)] * prices_close.shape[1], axis = 1)
    weights.columns = prices_close.columns
    weights[prices_close.isna()] = pd.NA
    for date in prices_close.iloc[rolling:, :].index:
        pos = np.where(prices_close.index == date)[0][0]
        prices_ = prices_close.iloc[(pos - rolling):pos].dropna(axis = 1)
        if prices_.shape[1] > 1:
            # if more than 1 price is available
            returns = prices_.pct_change().dropna()
            # Building the portfolio object
            port = rp.HCPortfolio(returns = returns)
            # Estimate optimal portfolio:
            w = port.optimization(model = "HRP", codependence = "pearson", rm = "MV", rf = 0, linkage = "single", max_k = 10, leaf_order = True)

            for col in w.T:
                weights.loc[date, col] = w.loc[col, "weights"]
        else:
            # if only 1 price available
            weights.loc[date, prices_.columns[0]] = 1
    return weights