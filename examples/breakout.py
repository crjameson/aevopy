from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.
import collections
import time
import aevopy

# define our risk management parameters - adapt this to your needs
# how much leverage do we want to use - this also depends on the asset but for the big ones 20x is the max
LEVERAGE = 20
# how much of our initial balance do we want to risk per trade in percent
RISK_PER_TRADE_PERCENT = 1
# what is our risk reward ratio 
RISK_REWARD_RATIO = 2
# what is our stop loss in percent - this is the max we are willing to lose per trade
# becasue we are working with very low timeframes we need to set this very tight
STOP_LOSS_PERCENT = 0.1
# what is our take profit in percent - this is the max we want to win per trade
TAKE_PROFIT_PERCENT = STOP_LOSS_PERCENT * RISK_REWARD_RATIO
# the length of the queue is the period of the donchian channel
# 120 means we look at the last 120 prices, one request every 30 seconds = 1h timeframe
DON_MAX_PERIOD = 12
REQUEST_INTERVAL_SECONDS = 30

def buy(client, instrument, position_size):
    order = client.buy_market(instrument.instrument_id, amount=position_size)
    print(f"order: {order}")

    stop_loss_price = order.avg_price * (1 - STOP_LOSS_PERCENT / 100)
    order = client.sell_stop_loss(instrument.instrument_id, trigger=stop_loss_price)

    take_profit_price = order.avg_price * (1 + TAKE_PROFIT_PERCENT / 100)
    order = client.sell_take_profit(instrument.instrument_id, trigger=take_profit_price)  

def sell(client, instrument, position_size):
    order = client.sell_market(instrument.instrument_id, amount=position_size)
    print(f"order: {order}")

    stop_loss_price = order.avg_price * (1 + STOP_LOSS_PERCENT / 100)
    order = client.buy_stop_loss(instrument.instrument_id, trigger=stop_loss_price)

    take_profit_price = order.avg_price * (1 - TAKE_PROFIT_PERCENT / 100)
    order = client.buy_take_profit(instrument.instrument_id, trigger=take_profit_price)

def run_trading_strategy(client, instrument, margin_per_position, last_prices):
    if positions := client.get_positions():
        # we always trade only one position at the same time, so just print the details and start over
        print(f"open position: asset: {positions[0].asset} amount: {positions[0].amount} unrealized_pnl: {positions[0].unrealized_pnl}")
        print(f"prices: current: {positions[0].mark_price} entry: {positions[0].avg_entry_price} liquidation: {positions[0].liquidation_price}")
        time.sleep(60)
        return

    price = aevopy.get_index(asset=instrument.underlying_asset)
    # our strategy only works when we have 120 prices in our queue
    if len(last_prices) < DON_MAX_PERIOD:
        print(f"collecting data: {price.timestamp}: price: {price.price}")
    else:
        min,max = min(last_prices),max(last_prices)
        print(f"{price.timestamp}: price: {price.price} local min: {min(last_prices)} local max: {max(last_prices)}")

        position_size = int(margin_per_position // instrument.index_price)
        
        if price.price > max:
            print(f"price: {price.price} is above max: {max} - open long position")
            buy(client, instrument, position_size)
            last_prices.clear()
        if price.price < min:
            print(f"price: {price.price} is below min: {min} - open short position")
            sell(client, instrument, position_size)
            last_prices.clear()
        
    last_prices.append(price.price)


if __name__ == "__main__":
    client = aevopy.AevoClient()
    print(f"client: {client.account.wallet_address} collecting data and start trading...")
    portfolio = client.get_portfolio()
    print(f"available portfolio margin balance: {portfolio.user_margin.balance}")

    # this is the amount we can spend on each trade including leverage
    margin_per_position = portfolio.user_margin.balance / 100 * RISK_PER_TRADE_PERCENT * LEVERAGE

    # get the market details about the asset we want to trade - TIA in this example
    instrument = aevopy.get_markets(asset="BNB")
    print(f"instrument: {instrument}")
    last_prices = collections.deque(maxlen=DON_MAX_PERIOD)  
    # this should catch exceptions for production, i had a few network errors during testing:
    #( requests.exceptions.ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response')))
    while True:
        try:
            run_trading_strategy(client, instrument, margin_per_position, last_prices)
        except Exception as e:
            print(f"error: {e} trying again...")
        time.sleep(REQUEST_INTERVAL_SECONDS)
    





