import pytest
import os
import sys
import aevopy
from aevopy.models import AevoAccount, OrderDetails, Order, Portfolio, Position
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from examples.breakout import run_trading_strategy, buy, sell, DON_MAX_PERIOD, STOP_LOSS_PERCENT, TAKE_PROFIT_PERCENT

def test_buy(mocker):
    # Mock the client and instrument
    client = mocker.Mock()
    instrument = mocker.Mock()

    # Mock the buy_market method to return a mock order with an avg_price
    order = OrderDetails(avg_price=100)
    client.buy_market.return_value = order
    client.sell_stop_loss.return_value = {}
    client.sell_take_profit.return_value = {}

    # Run the buy function
    buy(client, instrument, 10)

    # Check that the buy_market method was called with the correct arguments
    client.buy_market.assert_called_once_with(instrument.instrument_id, amount=10)

    # Check that the sell_stop_loss and sell_take_profit methods were called with the correct arguments
    stop_loss_price = order.avg_price * (1 - STOP_LOSS_PERCENT / 100)
    client.sell_stop_loss.assert_called_once_with(instrument.instrument_id, trigger=stop_loss_price)

    take_profit_price = order.avg_price * (1 + TAKE_PROFIT_PERCENT / 100)
    client.sell_take_profit.assert_called_once_with(instrument.instrument_id, trigger=take_profit_price)

def test_run_trading_strategy(mocker):
    # Mock the client and instrument
    client = mocker.Mock()
    instrument = mocker.Mock()

    # Mock the get_positions method to return an empty list
    client.get_positions.return_value = []

    # Mock the get_index method to return a sequence of 120 prices
    prices = [mocker.Mock(price=i) for i in range(120)]
    client.get_index.side_effect = prices

    # Run the trading strategy
    run_trading_strategy(client, instrument, 1000)

    # Check that the buy and sell methods were called
    assert client.buy.call_count == 1
    assert client.sell.call_count == 1

    # Check that the last_prices deque was cleared twice
    assert client.clear.call_count == 2

def test_run_trading_strategy_with_positions(mocker):
    # Mock the client and instrument
    client = mocker.Mock()
    instrument = mocker.Mock()

    # Mock the get_positions method to return a list with one position
    client.get_positions.return_value = [mocker.Mock()]

    # Run the trading strategy
    run_trading_strategy(client, instrument, 1000)

    # Check that the buy and sell methods were not called
    assert client.buy.call_count == 0
    assert client.sell.call_count == 0