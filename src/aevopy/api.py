import time
import requests
from .models import IndexPrice, Instrument
from .aevo import AevoClient
from dacite import from_dict, Config as DaciteConfig

DACITE_CONFIG = DaciteConfig(cast=[int, float])
headers = {"accept": "application/json"}
AEVO_API = "https://api.aevo.xyz"

def get_assets():
    response = requests.get(f"{AEVO_API}/assets", headers=headers).json()
    return response


def get_expiries(asset: str):
    response = requests.get(f"{AEVO_API}/expiries", headers=headers).json()
    return response


def get_index(asset: str) -> IndexPrice:
    response = requests.get(f"{AEVO_API}/index?asset={asset}", headers=headers).json()
    return from_dict(data_class=IndexPrice, data=response, config=DACITE_CONFIG)

def get_markets(asset: str = "", type=""):
    request_url = f"{AEVO_API}/markets"
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
    
def get_index_history(asset: str, resolution: int = 30, start_time: int = 0, end_time: int = 0):
    if start_time == 0:
        # take the last hour by default
        start_time = int(time.time()) - 300
    if end_time == 0:
        # always till now by default
        end_time = int(time.time())
    response = requests.get(f"{AEVO_API}/index-history?asset={asset}&resolution={resolution}&start_time={start_time}&end_time={end_time}", headers=headers).json()
    return response


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
