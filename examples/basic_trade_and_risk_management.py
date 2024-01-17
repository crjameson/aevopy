from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

import aevopy

# create a client - this will use a session for all requests and is more efficient
client = aevopy.AevoClient()
print(f"client: {client.account.wallet_address}")

# every trading system begins with some risk management params
# how much leverage do we want to use - this also depends on the asset but for the big ones 20x is the max
leverage = 20
# how much of our initial balance do we want to risk per trade in percent
risk_per_trade_percent = 3
# what is our risk reward ratio 
risk_reward_ratio = 2
# what is our stop loss in percent - this is the max we are willing to lose per trade
stop_loss_percent = 1
# what is our take profit in percent - this is the max we want to win per trade
take_profit_percent = stop_loss_percent * risk_reward_ratio

portfolio = client.get_portfolio()
print(f"available portfolio margin balance: {portfolio.user_margin.balance}")

# this is the amount we can spend on each trade including leverage
margin_per_position = portfolio.user_margin.balance / 100 * risk_per_trade_percent * leverage

# make sure we are authenticated
response = client.is_authenticated()
print(f"auth: {response}")

# get the market details about the asset we want to trade - TIA in this example
instrument = aevopy.get_markets(asset="TIA")
print(f"instrument: {instrument}")

# now create our first order and buy as much TIA as we can affort with our position margin
position_size = int(margin_per_position // instrument.index_price)
order = client.buy_market(instrument.instrument_id, amount=position_size)
print(f"order: {order} order_id: {order.order_id} avg_price: {order.avg_price}")

# the avg_price is the price we bought at - we use this to calculate our stop loss and take profit
avg_price = order.avg_price

# set stop loss set to 1% down - order.avg_price is the price we bought at
stop_loss_price = avg_price * (1 - stop_loss_percent / 100)
order = client.sell_stop_loss(instrument.instrument_id, trigger=stop_loss_price)

# set take profit to 2% up - order.avg_price is the price we bought at
take_profit_price = avg_price * (1 + take_profit_percent / 100)
order = client.sell_take_profit(instrument.instrument_id, trigger=take_profit_price)


