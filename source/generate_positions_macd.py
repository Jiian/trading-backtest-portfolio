import pandas as pd

def _generate_position_signal_macd(macd_signal, rsi_series, entry_rsi_range = (25, 50), exit_rsi_range = (75, 100)):
    """
    Generate position indicator. Logic employed:
        - Entry is allowed when MACD difference crosses over zero.
        - When this happens, if RSI is between entry_rsi_range, we will enter a long position.
        - When RSI is between exit_rsi_range, we will exit this position.

    Parameters:
        rsi_series (pd.Series): RSI time series values.
        exit_rsi (float): RSI points from BUY/SELL signal to exit existing position. eg. if BUY_SIGNAL is 25 and exit_rsi is 30 then close long position when RSI > 55.
        allow_shorts (bool): Set to True to allow holding negative positions.

    Returns:
        pd.Series: Positioning 1 indicating an open long position, -1 indicating an open short position, 0 indicating no position.
    """
    position_series = list()
    position = 0
    for date in macd_signal.index:
        if macd_signal.loc[date] > 0 and rsi_series.loc[date] > entry_rsi_range[0] and rsi_series.loc[date] < entry_rsi_range[1]:
            # ENTRY
            position = 1
        elif position == 1 and rsi_series.loc[date] > exit_rsi_range[0] and rsi_series.loc[date] < exit_rsi_range[1]:
            # EXIT
            position = 0
        else:
            # No change to position
            None
 
        position_series.append(position)
    position_series = pd.Series(position_series, index = macd_signal.index)
    return position_series

def generate_positions_macd(macd_close, rsi_close, entry_rsi_range = (25, 50), exit_rsi_range = (75, 100)):
    """
    Generate position indicator given dataframe of RSI.

    Parameters:
        rsi_close (pd.DataFrame): All RSI time series values.
        exit_rsi (float): RSI points from BUY/SELL signal to exit existing position. eg. if BUY_SIGNAL is 25 and exit_rsi is 30 then close long position when RSI > 55.

    Returns:
        pd.DataFrame: Positioning 1 indicating an open long position, -1 indicating an open short position, 0 indicating no position.
    """
    position_signal = pd.DataFrame(0, index = macd_close.index, columns = macd_close.columns)
    for col in macd_close.columns:
        series = _generate_position_signal_macd(macd_close.loc[:, col], rsi_close.loc[:, col], entry_rsi_range, exit_rsi_range)
        position_signal.loc[:, col] = series
    return position_signal