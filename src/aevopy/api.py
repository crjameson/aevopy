import requests
from loguru import logger
from .models import IndexPrice, Instrument
from .aevo import AevoClient
from dacite import from_dict, Config as DaciteConfig

DACITE_CONFIG = DaciteConfig(cast=[int, float])
headers = {"accept": "application/json"}


def get_assets():
    response = requests.get("https://api.aevo.xyz/assets", headers=headers).json()
    return response


def get_expiries(asset: str):
    response = requests.get("https://api.aevo.xyz/expiries", headers=headers).json()
    return response


def get_index(asset: str) -> IndexPrice:
    response = requests.get(f"https://api.aevo.xyz/index?asset={asset}", headers=headers).json()
    return from_dict(data_class=IndexPrice, data=response, config=DACITE_CONFIG)

def get_markets(asset: str = "", type=""):
    request_url = "https://api.aevo.xyz/markets"
    if asset:
        request_url += f"?asset={asset}"
    if type:
        request_url += f"&type={type}"

    response = requests.get(request_url, headers=headers).json()
    #TODO: fix types here, we can use typehooks or post_init, but the API should return an int for instrument_id
    instruments = [from_dict(data_class=Instrument, data=instrument, config=DACITE_CONFIG) for instrument in response]
    #instruments = [Instrument(**instrument) for instrument in response]
    
    if len(instruments) == 1:
        return instruments[0]
    else:
        return instruments


def create_order(
    instrument_id: int,
    amount: float,
    is_buy: bool = True,
    limit_price: float = None,
    stop: str = None,
    trigger: float = None,
    close_position: bool = False,   
    reduce_only: bool = False,
    time_in_force: str = "GTC",
    post_only: bool = False,
    mmp: bool = False,
    account: dict = None,
    ):
    with AevoClient() as client:
        return client.create_order(
            account=account,
            instrument_id=instrument_id,
            amount=amount,
            is_buy=is_buy,
            limit_price=limit_price,
            stop=stop,
            trigger=trigger,
            close_position=close_position,
            reduce_only=reduce_only,
            time_in_force=time_in_force,
            post_only=post_only,
            mmp=mmp,
        )
