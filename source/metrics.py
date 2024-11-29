import pandas as pd
import numpy as np

from config import CAPITAL_0, RISK_FREE_RATE, BUSINESS_DAYS, COMMISSION_RATE, SLIPPAGE_RATE

def _calculate_trade_by_trade_metrics(portfolio, prices_open):
    """
    Calculate trade-by-trade profit. A trade is completed when a non-zero position completely closed.
    Rebalancing does not constitute as a trade, but the profit/loss will be added to the trade results.

    Parameters:
        portfolio (pd.DataFrame): DataFrame of the open positions (in number of shares), shape is (num of trading days, num of instruments).
        prices_open (pd.DataFrame): DataFrame of the market open prices, shape is (num of trading days, num of instruments).

    Returns:
        dict of pd.Series: Dictionary with each key being a ticker, each item is a pd.Series of length = number of trades, and value equals to the profit/loss of each trade closed on the date specified in the index.
    """
    trade_metrics = dict()
    for ticker in portfolio.columns:
        # Change in position size ie trades
        transactions = portfolio.loc[:, ticker].diff().replace({0 : np.nan}).dropna()
        # Initialisation
        profits, indices = list(), list()
        cost, rev, pos = 0, 0, 0
        # For each change in position sizing
        for date, pos_change in zip(transactions.index, transactions):
            if pos_change > 0: # if buy
                cost += pos_change * prices_open.loc[date, ticker] * (1 + COMMISSION_RATE + SLIPPAGE_RATE)
                pos += pos_change
            else: # if sell
                rev += abs(pos_change) * prices_open.loc[date, ticker] * (1 - COMMISSION_RATE - SLIPPAGE_RATE)
                pos += pos_change
            # Completed a full trade (ie sold off everything)
            if pos == 0:
                profit = rev - cost
                profits.append(profit)
                indices.append(date)
                # RESET
                cost, rev, pos = 0, 0, 0
        # CLOSE ANY REMAINING POSITIONS AT THE END OF TESTING
        if pos > 0:
            rev += abs(pos) * prices_open.loc[date, ticker] * (1 - COMMISSION_RATE - SLIPPAGE_RATE)
            pos = 0
            profit = rev - cost
            profits.append(profit)
            indices.append(date)
        # OUTPUT
        trades = pd.Series(profits, indices)
        trade_metrics[ticker] = trades
    return trade_metrics



def calculate_portfolio_metrics(aum, trade_count, portfolio, prices_open):
    """
    Calculate portfolio metrics.

    Parameters:
        aum (pd.Series): Series of the total value of Asset Under Management daily, shape is (num of trading days, ).
        trade_count (pd.DataFrame): DataFrame of the number of trades executed each day, shape is (num of days with trades being executed, 1).
        portfolio (pd.DataFrame): DataFrame of the number of open positions (in number of shares) given each day, shape is (num of trading days, num of instruments).
        prices_open (pd.DataFrame): DataFrame of the market open prices, shape is (num of trading days, num of instruments).

    Returns:
        metrics (dict): Dictionary of main metrics.
        metadata (dict): Additional data.
    """
    # METRIC: Total Return
    total_return = (aum.iloc[-1] - CAPITAL_0) / CAPITAL_0

    # METRIC: Annual Return - no RFR adjustments
    daily_returns = aum.astype(float).pct_change().dropna()
    annualised_returns = (1 + daily_returns.mean()) ** BUSINESS_DAYS - 1

    # METRIC: Annual Volatility - no RFR adjustments
    annualised_volatility = daily_returns.std() * np.sqrt(BUSINESS_DAYS)

    # METRIC: Max Drawdown - no RFR adjustments
    rolling_max = aum.cummax()
    drawdowns = aum / rolling_max - 1

    # METRIC - Sharpe Ratio - RFR-adjusted
    excess_daily_returns = daily_returns - (RISK_FREE_RATE / 252)
    sharpe_ratio = np.sqrt(BUSINESS_DAYS) * excess_daily_returns.mean() / excess_daily_returns.std()

    # METRIC - Sortino Ratio - RFR-adjusted
    sortino_ratio = np.sqrt(BUSINESS_DAYS) * np.mean(excess_daily_returns / excess_daily_returns.clip(None, 0).std())

    # METRICS - Win Rate & Expectancy
    trade_metrics = _calculate_trade_by_trade_metrics(portfolio, prices_open)
    expectancy_table = dict()
    # for each ticker
    for key in trade_metrics.keys():
        trades = trade_metrics.get(key)
        win_rate_ = np.mean(trades > 0)
        avg_win_ = trades[trades > 0].mean()
        avg_lose_ = trades[trades < 0].mean()
        expectancy_table[key] = [win_rate_, win_rate_ * avg_win_ - (1 - win_rate_) * abs(avg_lose_)]
    # full portfolio
    trades = pd.concat([trade_metrics.get(key) for key in trade_metrics.keys()])
    win_rate = np.mean(trades > 0)
    avg_win = trades[trades > 0].mean()
    avg_lose = trades[trades < 0].mean()

    # OUTPUT
    metrics = {
        "Total Return" : total_return,
        "Annualised Return" : annualised_returns,
        "Annualised Volatility" : annualised_volatility,
        "Maximum Drawdown" : abs(drawdowns.min()),
        "Sharpe Ratio" : sharpe_ratio,
        "Sortino Ratio" : sortino_ratio,
        "Total Number of Trades" : trade_count.iloc[:, 0].sum(),
        "Average Return per Trade" : total_return / trade_count.iloc[:, 0].sum(),
        "Win Rate" : win_rate,
        "Expectancy" : win_rate * avg_win - (1 - win_rate) * abs(avg_lose)
    }

    metadata = {
        "drawdowns" : drawdowns,
        "expectancy_table" : expectancy_table,
        "trade_metrics" : trade_metrics
    }

    return metrics, metadata