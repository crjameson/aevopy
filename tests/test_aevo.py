import pytest
from aevopy import AevoClient, AevoAccount
from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

def test_aevo_client_from_env():
    client = AevoClient()

    assert client.account
    assert client.rest_url == "https://api-testnet.aevo.xyz"
    assert client.ws_url == "wss://ws-testnet.aevo.xyz"

