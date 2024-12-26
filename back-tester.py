import backtrader as bt
from alpaca.data import TimeFrame
from alpaca_trade_api import REST

from alpaca_config.keys import config
from strategies.MomentumStrategy import MomentumStrategy


def run_backtest(strategy, symbols, start, end, timeframe, cash):
    """
    Run a backtest using the Backtrader library.

    Args:
        strategy: The trading strategy class to be tested.
        symbols: A single symbol (str) or a collection of symbols (list/set) to backtest.
        start: Start date for historical data (format: 'YYYY-MM-DD').
        end: End date for historical data (format: 'YYYY-MM-DD').
        timeframe: TimeFrame object from Alpaca (e.g., TimeFrame.Day, TimeFrame.Minute).
        cash: Initial cash amount for the portfolio.

    Returns:
        results: The results of the backtest.
    """
    # Initialize the Alpaca REST API
    rest_api = REST(config['key_id'], config['secret_key'], base_url=config['trade_api_base_url'])

    # Initialize Backtrader's Cerebro engine for backtesting
    cerebro = bt.Cerebro(stdstats=True)
    cerebro.broker.setcash(cash)  # Set the initial cash amount

    # Add the trading strategy to the backtest
    cerebro.addstrategy(strategy)

    # Add performance analyzers (e.g., Sharpe Ratio)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='mysharpre')

    # Handle single symbol or multiple symbols
    if type(symbols) == str:  # Single symbol
        symbol = symbols
        alpaca_data = rest_api.get_bars(symbol, timeframe, start, end, adjustment='all').df  # Fetch historical data
        data = bt.feeds.PandasData(dataname=alpaca_data, name=symbol)  # Convert to Backtrader-compatible data feed
        cerebro.adddata(data)  # Add data feed to Cerebro
    elif type(symbols) == list or type(symbols) == set:  # Multiple symbols
        for symbol in symbols:
            alpaca_data = rest_api.get_bars(symbol, timeframe, start, end, adjustment='all').df
            data = bt.feeds.PandasData(dataname=alpaca_data, name=symbol)
            cerebro.adddata(data)

    # Run the backtest
    initial_portfolio_value = cerebro.broker.getvalue()  # Retrieve initial portfolio value
    print(f'Starting Portfolio Value: {initial_portfolio_value}')  # Log the starting value
    results = cerebro.run()  # Execute the backtest
    final_portfolio_value = cerebro.broker.getvalue()  # Retrieve final portfolio value
    print(
        f'Final Portfolio Value: {final_portfolio_value} ----> Return {(final_portfolio_value / initial_portfolio_value - 1) * 100}%'
    )  # Log the final portfolio value and return percentage

    # Log the Sharpe Ratio (measure of risk-adjusted return)
    strat = results[0]
    print('Sharpe Ratio: ', strat.analyzers.mysharpre.get_analysis()['sharperatio'])

    # Plot the backtest results
    cerebro.plot(iplot=False)

    return results


if __name__ == "__main__":
    """
    Main execution block for running backtests. Uncomment desired backtest configuration to execute.
    """

    # Example: Backtest a diversified portfolio using AllWeatherStrategy
    # run_backtest(AllWeatherStrategy, ['VTI', 'TLT', 'IEF', 'GLD', 'DBC'], '2023-01-01', '2024-06-20',
    #              TimeFrame.Day, 100000)

    # Example: Backtest a single stock using GoldenCrossStrategy
    # run_backtest(strategy=GoldenCrossStrategy, symbols='AAPL', start='2023-01-01', end='2024-06-20', timeframe=TimeFrame.Day, cash=100000)

    # Backtest the MomentumStrategy on AAPL stock
    run_backtest(strategy=MomentumStrategy, symbols='AAPL', start='2023-01-01', end='2024-06-20', timeframe=TimeFrame.Day, cash=100000)
