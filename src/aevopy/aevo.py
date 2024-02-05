from random import randint
import time
from eip712_structs import make_domain
from eth_hash.auto import keccak
from eth_account import Account
import requests
from dacite import from_dict, Config as DaciteConfig
DACITE_CONFIG = DaciteConfig(cast=[int, float])
from functools import partialmethod  # partial method passes self - partial doesnt
from .exceptions import AevoException, ConfigurationException, UnauthorizedException
from aevopy.models import AevoAccount, OrderDetails, Order, Portfolio, Position

AEVO_TESTNET = {
        "rest_url": "https://api-testnet.aevo.xyz",
        "ws_url": "wss://ws-testnet.aevo.xyz",
        "signing_domain": {
            "name": "Aevo Testnet",
            "version": "1",
            "chainId": "11155111",
        },
    }

AEVO_MAINNET = {
        "rest_url": "https://api.aevo.xyz",
        "ws_url": "wss://ws.aevo.xyz",
        "signing_domain": {
            "name": "Aevo Mainnet",
            "version": "1",
            "chainId": "1",
        },
    }

class AevoClient():
    def __init__(self, account=None, env="testnet"):
        self.account = AevoAccount.from_env() if account is None else account
        if not self.account.signing_key:
            raise ConfigurationException("signing_key is missing")
        if not self.account.wallet_address:
            raise ConfigurationException("wallet_address is missing")
        if not self.account.api_key:
            raise ConfigurationException("api_key is missing")
        if not self.account.api_secret:
            raise ConfigurationException("api_secret is missing")
        if not self.account.env:
            raise ConfigurationException("env is missing")
        
        self.rest_headers = {
            "accept": "application/json",
            "AEVO-KEY": self.account.api_key,
            "AEVO-SECRET": self.account.api_secret,
        }

        self.env = self.account.env
        if self.env == "testnet":
            self.rest_url = AEVO_TESTNET["rest_url"]
            self.ws_url = AEVO_TESTNET["ws_url"]
            self.signing_domain = make_domain(AEVO_TESTNET["signing_domain"]["name"], AEVO_TESTNET["signing_domain"]["version"], AEVO_TESTNET["signing_domain"]["chainId"])
        elif self.env == "mainnet":
            self.rest_url = AEVO_MAINNET["rest_url"]
            self.ws_url = AEVO_MAINNET["ws_url"]
            self.signing_domain = make_domain(AEVO_MAINNET["signing_domain"]["name"], AEVO_MAINNET["signing_domain"]["version"], AEVO_MAINNET["signing_domain"]["chainId"])
        else:
            raise ConfigurationException("env must be either testnet or mainnet")
        # using a session here for connection pooling and auth
        self.session = requests.Session()
        self.session.headers.update(self.rest_headers)
        
    def is_authenticated(self):
        response = self.session.get(f"{self.rest_url}/auth")
        if "success" in response.json():
            return True
        else:
            return False
        
    def _convert_price(self, price, decimals=6):
        """ aevo uses 6 decimals for all pricings and int values - so we convert it"""
        truncated_price = int(price * 10000) / 10000.0 # this is the smallest price change of 0.0001
        converted_price = truncated_price * 10**decimals
        return str(int(converted_price))
    
    def get_portfolio(self):
        portfolio_json = self.session.get(f"{self.rest_url}/portfolio").json()
        if "error" in portfolio_json:
            raise AevoException(portfolio_json["error"])
        try:
            portfolio = from_dict(data_class=Portfolio, data=portfolio_json, config=DACITE_CONFIG)
            return portfolio
        except Exception as e:
            raise AevoException(f"invalid data: {e}")
        
    def get_positions(self, wallet_address=None):
        if wallet_address is None:
            wallet_address = self.account.wallet_address
        positions_json = self.session.get(f"{self.rest_url}/positions").json()
        if "error" in positions_json:
                raise AevoException(positions_json["error"])
        try:
            positions = [from_dict(data_class=Position, data=position, config=DACITE_CONFIG) for position in positions_json["positions"]]
            return positions
        except Exception as e:
            raise AevoException(f"invalid data: {e}")
        
    def create_order(
            self,
        instrument_id: int,
        amount: float = 1,
        is_buy: bool = True, # its bull market we set buy default :D 
        limit_price: float = None, # no limit means market order
        stop: str = None, # this should be named stop_type or order_type
        trigger: float = None, # this should be name trigger_price to be more consistent
        close_position: bool = False,   
        reduce_only: bool = False,
        time_in_force: str = "GTC",
        post_only: bool = False,
        mmp: bool = False,
        ):
        timestamp = int(time.time())
        salt = randint(0, 10**6)
        # no limit price set means market order - so we just set the limits very high/low 
        if limit_price is None:
            limit_price = 2**256-1 if is_buy else 0  
        else:
            limit_price = self._convert_price(limit_price)
        amount = self._convert_price(amount)
        #TODO: figure out the other params and implement them
        order_struct = Order(
                maker=self.account.wallet_address,  # The wallet"s main address
                isBuy=is_buy,
                limitPrice=int(limit_price), 
                amount=int(amount),
                salt=salt,
                instrument=instrument_id,
                timestamp=timestamp,
            )  
        signable_bytes = keccak(order_struct.signable_bytes(domain=self.signing_domain))  
        signature = Account._sign_hash(signable_bytes, self.account.signing_key).signature.hex()
        #order_id = f"0x{signable_bytes.hex()}"

        order_json = {
            "maker": self.account.wallet_address,
            "is_buy": is_buy,
            "instrument": int(instrument_id),
            "limit_price": str(limit_price),
            "amount": str(amount),
            "salt": str(salt),
            "signature": signature,
            "post_only": post_only,
            "reduce_only": reduce_only,
            "close_position": close_position,
            #"time_in_force": time_in_force,
            #"mmp": mmp,
            "timestamp": timestamp,
        }

        if trigger and stop:
            order_json["stop"] = stop
            order_json["trigger"] = self._convert_price(trigger)

        response_json = self.session.post(f"{self.rest_url}/orders", json=order_json).json()
        if "error" in response_json:
            raise AevoException(response_json["error"])
        try:
            order = from_dict(data_class=OrderDetails, data=response_json, config=DACITE_CONFIG)
            return order
        except Exception as e:
            #TODO: handle this better
            print(response_json)
            raise e

    # this is just to make the code more readable    
    buy_market = partialmethod(create_order, is_buy=True)
    sell_market = partialmethod(create_order, is_buy=False) 
    buy_limit = partialmethod(create_order, is_buy=True)
    sell_limit = partialmethod(create_order, is_buy=False)
    # to close a long position we need to sell and vice versa
    # for close_position amount needs to be set to 0
    sell_stop_loss = partialmethod(create_order, is_buy=False, amount=0, stop="STOP_LOSS", reduce_only=True,  close_position=True)
    sell_take_profit = partialmethod(create_order, is_buy=False, amount=0, stop="TAKE_PROFIT", reduce_only=True, close_position=True)
    buy_stop_loss = partialmethod(create_order, is_buy=False, amount=0, stop="STOP_LOSS", reduce_only=True,  close_position=True)
    buy_take_profit = partialmethod(create_order, is_buy=False, amount=0, stop="TAKE_PROFIT", reduce_only=True, close_position=True)
    #TODO: trailing stop method would be useful, which updates the current stop_loss and take profit based on the current index price
    #TODO: close all function would be useful, which closes all positions at once
