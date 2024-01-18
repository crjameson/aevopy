from typing import List, TypedDict
from dataclasses import dataclass
from eip712_structs import EIP712Struct, Address, Uint, Boolean
import os
from dotenv import load_dotenv

#this needs to be named Order because of the signature which takes the name
class Order(EIP712Struct):
    maker = Address()
    isBuy = Boolean()
    limitPrice = Uint(256)
    amount = Uint(256)
    salt = Uint(256)
    instrument = Uint(256)
    timestamp = Uint(256)

#typed dicts might be a little faster, but i guess that doesnt matter, just buy a better server from the gains
@dataclass(slots=True, kw_only=True)
class AevoAccount():
    signing_key:str
    wallet_address:str
    api_key:str
    api_secret:str
    env:str
    
    @classmethod
    def from_env(cls):
        return cls(signing_key=os.getenv("AEVO_SIGNING_KEY"),
                   wallet_address=os.getenv("AEVO_WALLET_ADDRESS"),
                   api_key=os.getenv("AEVO_API_KEY"),
                   api_secret=os.getenv("AEVO_API_SECRET"),
                   env=os.getenv("AEVO_ENV"))
    
@dataclass(slots=True, kw_only=True)
class IndexPrice():
    timestamp: int
    price: float

@dataclass(slots=True, kw_only=True)
class Instrument():
    # we stick with the original names to align with the original api even when it looks ugly
    instrument_id: int
    instrument_name: str
    instrument_type: str
    underlying_asset: str
    quote_asset: str
    price_step: float
    amount_step: float
    min_order_value: float
    mark_price: float
    index_price: float
    is_active: bool
    max_leverage: float

@dataclass(slots=True, kw_only=True)
class OrderDetails():
    # we stick with the original names to align with the original api even when it looks ugly
    order_id: str
    account: str
    instrument_name: str
    instrument_id: int
    instrument_type: str
    order_type: str
    order_status: str
    side: str
    amount: float
    price: float
    filled: float
    created_timestamp: int
    timestamp: int
    system_type: str = "API"
    initial_margin: float = 0
    avg_price: float = 0
    close_position: bool = False
    trigger: float = 0
    stop: str = None
    reduce_only: bool = False
    
@dataclass(slots=True, kw_only=True)
class Greek():
    asset: str
    delta: float
    gamma: float
    rho: float
    theta: float
    vega: float

@dataclass(slots=True, kw_only=True)
class UserMargin():
    used: float
    balance: float

@dataclass(slots=True, kw_only=True)
class Portfolio():
    balance: float
    pnl: float
    realized_pnl: float
    win_rate: float
    profit_factor: float
    sharpe_ratio: float
    greeks: List[Greek]
    user_margin: UserMargin

@dataclass
class Trigger:
    order_id: str
    trigger: str

@dataclass
class PositionTriggers:
    take_profit: Trigger
    stop_loss: Trigger

@dataclass(slots=True, kw_only=True)
class Position():
    asset:str
    instrument_id: int
    instrument_name: str
    instrument_type: str
    amount: float
    side: str
    mark_price: float
    avg_entry_price: float
    unrealized_pnl: float
    maintenance_margin: float
    liquidation_price: float
    margin_type: str
    triggers: PositionTriggers