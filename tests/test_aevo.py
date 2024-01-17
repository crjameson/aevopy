import pytest
from aevopy import AevoClient, AevoAccount
import requests_mock
from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

def test_aevo_client_from_env():
    client = AevoClient()

    assert client.account
    assert client.rest_url == "https://api-testnet.aevo.xyz"
    assert client.ws_url == "wss://ws-testnet.aevo.xyz"
    assert client.env == "testnet"
    assert client.rest_headers["AEVO-KEY"] == "test-api-key"
    assert client.rest_headers["AEVO-SECRET"] == "test-api-secret"

def test_is_authenticated():
    client = AevoClient()
    with requests_mock.Mocker() as m:
        m.get("https://api-testnet.aevo.xyz/auth", json={"success": "OK"})
        assert client.is_authenticated() == True
        m.get("https://api-testnet.aevo.xyz/auth", json={"error": "UNAUTHORIZED"})
        assert client.is_authenticated() == False

def test_convert_price():
    client = AevoClient()
    assert client._convert_price(19.1234) == "19123400"
    assert client._convert_price(19.1234555644) == "19123400"
    assert client._convert_price(20.1234567891012) == "20123400"
    assert client._convert_price(0.1234567891012) == "123400"


