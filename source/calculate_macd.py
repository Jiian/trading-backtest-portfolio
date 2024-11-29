import ta

def _get_macd_signal(series):
    """
    Calculate the MACD-based entry signal (enter at crossover) for a pandas Series.

    Parameters:
        series (pd.Series): Input data series (e.g., closing prices).
        period (int): Lookback period for RSI calculation. Default is 14.

    Returns:
        pd.Series: MACD signals.
    """
    macd = ta.trend.macd_diff(series).dropna()
    macd[macd >= 0] = 1
    macd[macd < 0] = 0
    macd = macd.diff()
    return macd.dropna()


def calculate_macd_signal(prices):
    """
    Calculate the MACD-based entry signal (enter at crossover) for a pandas DataFrame.

    Parameters:
        prices (pd.DataFrame): Input price dataframe, each instrument as a column.

    Returns:
        pd.DataFrame: DataFrame of MACD signals.
    """

    macd_df = prices.apply(lambda ser : _get_macd_signal(ser), axis = 0)

    return macd_df