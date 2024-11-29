import os
import yfinance as yf
import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta

from config import LIST_OF_STOCKS, BACKTEST_START, BACKTEST_END, RSI_PERIOD

def read_data(use_backup = False):
    """
    Read yahoo finance price data.

    Parameters:
        use_backup (bool): Set to True to use backup data saved as csv. Use for connection issues etc.

    Returns:
        tuple: Tuple of two dataframes (prices_close, prices_open) of the size (n, len(tickers)).
    """
    # Read data
    backup_path = ".\\data\\data_backup.csv"
    if not use_backup:
        prices = yf.download(tickers = LIST_OF_STOCKS, period = 'max', interval = '1d', auto_adjust = True, multi_level_index = False)
        if not os.path.isfile(backup_path):
            prices.to_csv(backup_path)
    else:
        prices = pd.read_csv(backup_path, parse_dates = [0], index_col = 0, header = [0, 1])
    # Validation
    assert prices.index.min() <= BACKTEST_START - relativedelta(days = RSI_PERIOD)
    assert prices.index.max() >= BACKTEST_END
    # Filter for required data
    prices = prices[np.logical_and(prices.index >= BACKTEST_START - relativedelta(days = RSI_PERIOD), prices.index <= BACKTEST_END)]
    # Split into two tables
    prices_close = prices.loc[:, "Close"]
    prices_open = prices.loc[:, "Open"]
    return prices_close, prices_open