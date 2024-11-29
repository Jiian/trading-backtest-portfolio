import pandas as pd

def _generate_position_signal_rsi(rsi_series, buy_level, sell_level, exit_rsi = None, allow_shorts = False):
    """
    Generate position indicator. 
    
    Parameters:
        rsi_series (pd.Series): RSI time series values.
        buy_level (int): Int from 1 to 99. RSI level to buy into a position.
        sell_level (int): Int from 1 to 99. RSI level to sell a position.
        exit_rsi (float): RSI points from BUY/SELL signal to exit existing position. eg. if buy_level is 25 and exit_rsi is 30 then close long position when RSI > 55.
        allow_shorts (bool): Set to True to allow holding negative positions.

    Returns:
        pd.Series: Positioning 1 indicating an open long position, -1 indicating an open short position, 0 indicating no position.
    """
    if allow_shorts:
        raise NotImplementedError("Currently only implemented for longs only.")
    
    position_series = list()
    position = 0
    yesterday = 0
    for rsi in rsi_series:
        if rsi < buy_level:
            match position:
                case -1:
                    # Hit buy signal with existing short - close the position
                    position = 0 # positions cancel out
                case 1:
                    # Hit buy signal with existing long - keep the position
                    position = 1
                case 0:
                    # Hit buy signal with no position - open only if not a consecutive buy (ie. close short yesterday, open long today)
                    position = 1 if yesterday <= 0 else 0
                case _:
                    raise ValueError(f"Position {position} is invalid")
            # Update today's signal
            yesterday = 1
        elif rsi > sell_level:
            match position:
                case 1:
                    # Hit sell signal with existing long - close the position
                    position = 0
                case -1:
                    # Hit sell signal with existing short - keep the position
                    position = -1
                case 0:
                    if allow_shorts:
                        # Hit sell signal with no position - open only if not a consecutive sell (ie. close long yesterday, open short today)
                        position = -1 if yesterday >= 0 else 0
                    else:
                        position = 0
                case _:
                    raise ValueError(f"Position {position} is invalid")
            # Update today's signal
            yesterday = -1
        else:
            if exit_rsi is not None:
                match position:
                    case 1:
                        # Existing long position & RSI between buy_level + exit_rsi and sell_level
                        if rsi > buy_level + exit_rsi:
                            position = 0
                    case -1:
                        # Existing short position & RSI between sell_level - exit_rsi and buy_level
                        if rsi < sell_level - exit_rsi:
                            position = 0

            # No signal - keep the position
            # Update today's signal
            yesterday = 0
            
        position_series.append(position)
    position_series = pd.Series(position_series, index = rsi_series.index)
    return position_series

def generate_positions_rsi(rsi_close, buy_level, sell_level, exit_rsi = None):
    """
    Generate position indicator given dataframe of RSI.

    Parameters:
        rsi_close (pd.DataFrame): All RSI time series values.
        buy_level (int): Int from 1 to 99. RSI level to buy into a position.
        sell_level (int): Int from 1 to 99. RSI level to sell a position.
        exit_rsi (float): RSI points from BUY/SELL signal to exit existing position. eg. if buy_level is 25 and exit_rsi is 30 then close long position when RSI > 55.

    Returns:
        pd.DataFrame: Positioning 1 indicating an open long position, -1 indicating an open short position, 0 indicating no position.
    """
    return rsi_close.apply(lambda ser : _generate_position_signal_rsi(ser.dropna(), buy_level, sell_level, exit_rsi), axis = 0)