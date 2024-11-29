# backtest-momentum-trading

This repository stores the codes to backtest several momentum-based trading strategies.

## Trading Setup
From the point of view of an asset-management entity, the goal is to maximise the returns through holding positive positions of stocks while adhering to the agreed-upon trading strategy and universe of assets.

### Scope and Assumptions
1. The stocks under consideration are what are famously-known as the "Magnificent 7" companies today: AAPL, MSFT, META, TSLA, NVDA, AMZN and GOOG.
2. Only long positions are allowed.
3. Rebalancing is allowed only when a trading signal is triggered.
4. Backtest for the years 1981 to 2023 inclusive.

### Financial Parameters
All parameters are contained within the `./config.py` file.

<table>
    <tr>
        <th>Parameter</th>
        <th>Default Value</th>
        <th>Description</th>
    </tr>
    <tr>
        <td>CAPITAL_0</td>
        <td>1,000,000</td>
        <td>Initial capital for investment.</td>
    </tr>
    <tr>
        <td>COMMISSION_RATE</td>
        <td>0.0010</td>
        <td>Commission rate per transaction.</td>
    </tr>
    <tr>
        <td>SLIPPAGE_RATE</td>
        <td>0.0002</td>
        <td>Estimated slippage per transaction.</td>
    </tr>
    <tr>
        <td>MIN_TRANSC</td>
        <td>10</td>
        <td>Minimum transaction size (in number of stocks).</td>
    </tr>
    <tr>
        <td>MAX_PROP</td>
        <td>0.30</td>
        <td>Maximum proportion of asset under management (AUM) to be risked per instrument.</td>
    </tr>
    <tr>
        <td>RISK_FREE_RATE</td>
        <td>0.02</td>
        <td>Annual risk-free interest rate.</td>
    </tr>
    <tr>
        <td>BUSINESS_DAYS</td>
        <td>252</td>
        <td>Number of business days in a year.</td>
    </tr>
</table>

### Strategies Tested
<table>
    <tr>
        <th>No.</th>
        <th>Strategy Name</th>
        <th>Notebook Name</th>
        <th>Description</th>
    </tr>
    <tr>
        <td>1</td>
        <td>RSI</td>
        <td>01 rsi-only.ipynb</td>
        <td>The idea is to buy an instrument when it is "oversold" i.e. having a low RSI value.</td>
    </tr>
    <tr>
        <td>2</td>
        <td>MACD+RSI</td>
        <td>02 macd-and-rsi.ipynb</td>
        <td>Consider buying an instrument when its MACD Difference crosses zero from below. RSI must be relatively oversold to enter this position.</td>
    </tr>
    <tr>
        <td>3</td>
        <td>HRP</td>
        <td>03 hrp-alloc.ipynb</td>
        <td>An extension of the MACD+RSI strategy. Portfolio allocation is done through Hierarchical Risk Parity.</td>
    </tr>
    <tr>
        <td>4</td>
        <td>VolAdj</td>
        <td>04 voladj-alloc.ipynb</td>
        <td>An extension of the MACD+RSI strategy. Portfolio allocation is done through proportionally allocating funds based on each instrument's rolling returns per standard deviation.</td>
    </tr>
</table>

## Technical Setup

### Files and Directories
<table>
    <tr>
        <th>File Name</th>
        <th>Function</th>
        <th>Description</th>
    </tr>
    <tr>
        <td>backtest.py</td>
        <td>run_backtest()</td>
        <td>Given the positions signal and relevant price data, the function in this module runs the backtest to produce two tables - portfolio (in number of shares) and portfolio_value (in $) for each trading day.</td>
    </tr>
    <tr>
        <td>calculate_macd.py</td>
        <td>calculate_macd_signal()</td>
        <td>Computes the MACD (Moving Average Convergence Divergence) difference indicator signal.</td>
    </tr>
    <tr>
        <td>calculate_rsi.py</td>
        <td>calculate_rsi()</td>
        <td>Computes the RSI (Relative Strength Index) indicator signal.</td>
    </tr>
    <tr>
        <td>generate_positions_macd.py</td>
        <td>generate_positions_macd()</td>
        <td>Generates trading positions based on MACD signals. "1" represents a long position is active while "0" represents no active positions.</td>
    </tr>
    <tr>
        <td>generate_positions_rsi.py</td>
        <td>generate_positions_rsi()</td>
        <td>Generates trading positions based on RSI signals. "1" represents a long position is active while "0" represents no active positions.</td>
    </tr>
    <tr>
        <td>hrp.py</td>
        <td>calculate_hrp_weights()</td>
        <td>Calculates the Hierarchical Risk Parity (HRP) portfolio allocation weights.</td>
    </tr>
    <tr>
        <td>metrics.py</td>
        <td>calculate_portfolio_metrics()</td>
        <td>Defines performance metrics for evaluating strategies.</td>
    </tr>
    <tr>
        <td>read_data.py</td>
        <td>read_data()</td>
        <td>Handles reading and processing data from source.</td>
    </tr>
    <tr>
        <td>voladj.py</td>
        <td>calculate_voladj_weights()</td>
        <td>Calculates the volatility-adjusted portfolio allocation weights.</td>
    </tr>
</table>

## Results and Discussion

<table>
    <tr>
        <th>Metric</th>
        <th>RSI</th>
        <th>MACD+RSI</th>
        <th>HRP</th>
        <th>VolAdj</th>
        <th>S&P500</th>
    </tr>
    <tr>
        <td>Total Return</td>
        <td>1.8662</td>
        <td>56.8983</td>
        <td>0.2976</td>
        <td>2.2947</td>
        <td>33.9848</td>
    </tr>
    <tr>
        <td>Annualised Return</td>
        <td>0.0486</td>
        <td>0.1251</td>
        <td>0.0062</td>
        <td>0.0317</td>
    </tr>
    <tr>
        <td>Annualised Volatility</td>
        <td>0.2143</td>
        <td>0.2163</td>
        <td>0.0142</td>
        <td>0.0827</td>
    </tr>
    <tr>
        <td>Maximum Drawdown</td>
        <td>0.6484</td>
        <td>0.4885</td>
        <td>0.0631</td>
        <td>0.2757</td>
    </tr>
    <tr>
        <td>Sharpe Ratio</td>
        <td>0.1280</td>
        <td>0.4527</td>
        <td>-0.9762</td>
        <td>0.1354</td>
    </tr>
    <tr>
        <td>Sortino Ratio</td>
        <td>0.2012</td>
        <td>0.7331</td>
        <td>-1.4788</td>
        <td>0.2158</td>
    </tr>
    <tr>
        <td>Total Number of Trades</td>
        <td>1504</td>
        <td>1437</td>
        <td>833</td>
        <td>754</td>
    </tr>
    <tr>
        <td>Average Return per Trade</td>
        <td>0.0012</td>
        <td>0.0396</td>
        <td>0.0004</td>
        <td>0.0030</td>
    </tr>
    <tr>
        <td>Win Rate</td>
        <td>0.6918</td>
        <td>0.7519</td>
        <td>0.7970</td>
        <td>0.6305</td>
    </tr>
    <tr>
        <td>Expectancy</td>
        <td>6009</td>
        <td>211358</td>
        <td>2237</td>
        <td>9215</td>
    </tr>
</table>

1. RSI is considered a leading indicator. Using RSI alone to indicate mean-reversion timings produced a return far lower than the S&P500 index.
2. Adding MACD as a lagging indicator for momentum, the results significantly outperformed the first model. The model has also outperformed the S&P500 index in total returns over the long run.
3. While it is tempting to minimise the drawdown and volatility of the trading strategy in step 2, both approaches that were experimented with resulted in significantly worse metrics.

    (a) Both HRP and Volatility-adjusted portfolio optimisation approaches aim to reduce volatility in the portfolio by setting a lower weight to the higher volatility instruments.

    (b) Given that the magnificent 7 companies are high-performing in hindsight, they are in a long-term uptrend. In such an uptrend, the returns are usually driven by the more volatile stocks. The de-prooritisation of these stocks resulted in the strategies missing out on the upside.

    (c) Volatility-adjusted portfolio optimisation is unsuitable to be used together with our mean-reverting RSI strategy. By definition, an instrument that is oversold has experienced a recent downtrend. Adjusting the portfolio by looking at its recent volatility-adjusted returns are not helpful, given that the returns are likely poor.