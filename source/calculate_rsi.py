import ta

def _get_rsi_sma(series, period):
    """
    Calculate the Relative Strength Index (RSI) for a pandas Series using Simple MA.

    Parameters:
        series (pd.Series): Input data series (e.g., closing prices).
        period (int): Lookback period for RSI calculation. Default is 14.

    Returns:
        pd.Series: RSI values.
    """
    # Calculate price changes
    delta = series.diff()

    # Separate gains and losses
    gains = delta.where(delta > 0, 0)
    losses = -delta.where(delta < 0, 0)

    # Calculate average gains and losses
    avg_gains = gains.rolling(window = period, min_periods = period).mean()
    avg_losses = losses.rolling(window = period, min_periods = period).mean()

    # Avoid division by zero
    avg_losses = avg_losses.replace(0, 1e-10)

    # Calculate the Relative Strength (RS)
    rs = avg_gains / avg_losses

    # Calculate the RSI
    rsi = 100 - (100 / (1 + rs))

    return rsi.iloc[(period - 1):]

def _get_rsi_ema(series, period):
    """
    Calculate the Relative Strength Index (RSI) for a pandas Series using Exponential MA.

    Parameters:
        series (pd.Series): Input data series (e.g., closing prices).
        period (int): Lookback period for RSI calculation. Default is 14.

    Returns:
        pd.Series: RSI values.
    """
    return ta.momentum.rsi(series, window = period).iloc[(period - 1):]

def calculate_rsi(prices, smoothing = "sma", period = 14):
    """
    Calculate the Relative Strength Index (RSI) for a pandas DataFrame.

    Parameters:
        prices (pd.DataFrame): Input price dataframe, each instrument as a column.
        smoothing (str): One of ("sma", "ema"). Smoothing moving average method.
        period (int): Lookback period for RSI calculation. Default is 14.

    Returns:
        pd.DataFrame: DataFrame of RSI values.
    """
    match smoothing:
        case "sma":
            rsi_df = prices.apply(lambda ser : _get_rsi_sma(ser.dropna(), period), axis = 0)
        case "ema":
            rsi_df = prices.apply(lambda ser : _get_rsi_ema(ser.dropna(), period), axis = 0)
        case _:
            raise NotImplementedError(f"{smoothing} is not a valid smoothing parameter.")
    return rsi_df