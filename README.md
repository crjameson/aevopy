# Aevopy

Aevopy is a python client for the perp and options trading platform aevo.xyz. It is still in a very early stage, but maybe
useful if you considering automated crypto currency trading. 

For signup with Aevo you can use this link to save on fees:

https://app.aevo.xyz/r/Tulip-Sturdy-Laffont

You can find complete tutorials on how to use this code to build your own trading strategies on my substack or medium account: 

https://substack.com/@crjameson

https://medium.com/@crjameson

## Table of Contents

- [Introduction](#introduction)
- [Usage](#usage)
- [Installation](#installation)
- [Usage](#usage)

## Introduction

Aevopy is a simple to use python library to execute cryptocurrency perp and options trades via Aevo. It should work with all Python versions > 3.11. Older versions are untested but might work as well.

## Usage

Here is some example code to give you a basic idea how to use it:

```python
import aevopy
client = aevopy.AevoClient()

portfolio = client.get_portfolio()
print(f"available portfolio margin balance: {portfolio.user_margin.balance}")

# # get the market details about the asset we want to trade - TIA in this example
instrument = aevopy.get_markets(asset="TIA")
print(f"instrument: {instrument}")

# create a market buy order
order = client.buy_market(instrument.instrument_id, amount=1)
print(f"order: {order} order_id: {order.order_id} avg_price: {order.avg_price}")

# set stop loss and take profit
stop_loss_price = order.avg_price * 0.99
take_profit_price = order.avg_price * 1.02
order = client.sell_stop_loss(instrument.instrument_id, trigger=stop_loss_price)
order = client.sell_take_profit(instrument.instrument_id, trigger=take_profit_price)
```

## Installation

Pypi following soon, for now use poetry. Put a .env file with your credentials in the same directory as your script is running. Take a look at .env.example in the examples folder.

To run the example:

poetry run python examples/basic_trade_and_risk_management.py

To run the tests:

poetry run pytest


## Contact

For questions or ideas write me a DM on twitter here:

https://twitter.com/crjameson_