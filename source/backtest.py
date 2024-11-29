import pandas as pd
import numpy as np

from config import CAPITAL_0, COMMISSION_RATE, SLIPPAGE_RATE, MIN_TRANSC, MAX_PROP

def run_backtest(positions_signals, prices_open, prices_close, weights = None, allocation_method = "equal"):
    """
    Conduct backtesting.

    Parameters:
        positions_signals (pd.DataFrame): DataFrame of market signals generated (1: long, 0: no position), shape is (num of trading days, num of instruments).
        prices_open (pd.DataFrame): DataFrame of the market open prices, shape is (num of trading days, num of instruments).
        prices_close (pd.DataFrame): DataFrame of the market close prices, shape is (num of trading days, num of instruments).
        weights (pd.DataFrame): DataFrame of the weights for portfolio allocation, shape is (num of trading days, num of instruments).
        allocation_method (str): One of ["equal", "hrp", "voladj"].

    Returns:
        portfolio (pd.DataFrame): DataFrame of the number of open positions (in number of shares) given each day, shape is (num of trading days, num of instruments).
        portfolio_value (pd.DataFrame): DataFrame of the market closing value of portfolio given each day, shape is (num of trading days, num of instruments).
        trade_count (pd.DataFrame): DataFrame of the number of trades executed each day, shape is (num of days with trades being executed, 1).
    """
    # INTIALISATION
    cash_account = CAPITAL_0
    prev_date = positions_signals.index[0]
    prev_signal = positions_signals.loc[prev_date, :]
    # TO STORE POSITIONS (NUMBER OF SHARES) AT MARKET CLOSE
    portfolio = pd.DataFrame(index = positions_signals.index, columns = positions_signals.columns, dtype = int).fillna(0)
    # TO STORE VALUE POSITIONS AT MARKET CLOSE
    portfolio_value = pd.DataFrame(index = positions_signals.index, columns = positions_signals.columns, dtype = int).fillna(0)
    # TO STORE CASH ACCOUNT SIZE AT MARKET CLOSE
    cash_accounts = pd.DataFrame(index = positions_signals.index, columns = ["cash"])
    # TO STORE NUMBER OF TRADES
    trade_count = pd.DataFrame(index = positions_signals.index, columns = ["num_trades"])

    for date in positions_signals.iloc[1:, :].index:
        # COLLECTING INFORMATION
        ## PRE-MARKET
        prev_aum = cash_account + portfolio_value.loc[prev_date, :].sum()
        current_signal = positions_signals.loc[date, :]
        current_eligible_count = sum(current_signal)
        signal_changed = not current_signal.equals(prev_signal)

        ## MARKET-OPENS
        current_open = prices_open.loc[date, :].fillna(0)
        current_close = prices_close.loc[date, :].fillna(0)

        # EXECUTION
        if signal_changed:
            # ALLOCATE EQUAL-INVESTMENT WEIGHT, SATISFY MAX SIZE RELATIVE TO AUM
            funds_to_allocate = prev_aum * np.clip(current_eligible_count * MAX_PROP, 0, 1)
            if funds_to_allocate > 0:
                # SIGNAL CHANGED, WITH ELIGIBLE STOCKS
                funds_to_each = funds_to_allocate / current_eligible_count
                match allocation_method:
                    case "equal":
                        current_portfolio = (funds_to_each * current_signal // current_open.replace({0 : np.nan})).fillna(0)
                    case "hrp":
                        assert weights is not None, f"Weights cannot be None when {allocation_method} is chosen."
                        weights_ = weights.loc[date, :]
                        weights_ /= sum(weights_)
                        current_portfolio = (funds_to_each * current_signal * weights_ // current_open.replace({0 : np.nan})).fillna(0)
                    case "voladj":
                        assert weights is not None, f"Weights cannot be None when {allocation_method} is chosen."
                        weights_ = weights.loc[date, current_signal[current_signal > 0].index.tolist()]
                        if any(weights_ < 0):
                            weights_[weights_ < 0] = 0
                        weights_ = weights_ / weights_.sum()
                        current_portfolio = (funds_to_each * current_signal * weights_ // current_open.replace({0 : np.nan})).fillna(0)
                    case _:
                        raise ValueError(f"Invalid allocation_method: {allocation_method}")

                change_in_portfolio = (current_portfolio - portfolio.loc[prev_date, :])
                change_in_portfolio = change_in_portfolio.abs().clip(MIN_TRANSC, None) * np.sign(change_in_portfolio)
                cost = change_in_portfolio * current_open
                fees = cost.abs() * (COMMISSION_RATE + SLIPPAGE_RATE)
                cash_account_pending = cash_account - (cost.sum() + fees.sum())
                if cash_account_pending < 0:
                    # NO ACTION IF NOT ENOUGH CASH TO EXECUTE
                    portfolio.loc[date, :] = portfolio.loc[prev_date, :]
                    portfolio_value.loc[date, :] = portfolio.loc[date, :] * current_close
                else:
                    # TRANSACTION GOES THROUGH
                    cash_account = cash_account_pending
                    portfolio.loc[date, :] = current_portfolio
                    portfolio_value.loc[date, :] = portfolio.loc[date, :] * current_close
            else:
                # SIGNAL CHANGED BUT NOW HOLD NO STOCKS (IE SELL EVERYTHING)
                current_portfolio = portfolio.loc[date, :]
                change_in_portfolio = (current_portfolio - portfolio.loc[prev_date, :])
                change_in_portfolio = change_in_portfolio.abs().clip(MIN_TRANSC, None) * np.sign(change_in_portfolio)
                cost = change_in_portfolio * current_open
                fees = cost.abs() * (COMMISSION_RATE + SLIPPAGE_RATE)
                cash_account_pending = cash_account - (cost.sum() + fees.sum())
                assert cash_account_pending > 0, f"Selling off all stocks should result in positive cash_account, got {cash_account_pending}"
                # TRANSACTION GOES THROUGH
                cash_account = cash_account_pending
                portfolio.loc[date, :] = current_portfolio
                portfolio_value.loc[date, :] = portfolio.loc[date, :] * current_close
            num_trades = np.count_nonzero(change_in_portfolio)
        else:
            # NO SIGNAL CHANGE, NO CHANGE TO PORTFOLIO
            portfolio.loc[date, :] = portfolio.loc[prev_date, :]
            portfolio_value.loc[date, :] = portfolio.loc[date, :] * current_close
            num_trades = 0

        # END HOUSE-KEEPING
        prev_date = date
        prev_signal = current_signal
        cash_accounts.loc[date, "cash"] = cash_account
        trade_count.loc[date, "num_trades"] = num_trades

    # MERGE CASH HISTORY
    portfolio_value = pd.concat((portfolio_value, cash_accounts), axis = 1).dropna()

    return portfolio, portfolio_value, trade_count.dropna()