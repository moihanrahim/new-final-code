from fyers_api import fyersModel
from fyers_api import accessToken
from kiteconnect import KiteConnect
import logging
import os
import traceback
from datetime import datetime as dt


def place_order(symbol, quantity, side, type):
    client_id = "EGNBLDBRXZ-100"
    access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhcGkuZnllcnMuaW4iLCJpYXQiOjE2NTc1NTQ5MDgsImV4cCI6MTY1NzU4NTgwOCwibmJmIjoxNjU3NTU0OTA4LCJhdWQiOlsieDowIiwieDoxIiwieDoyIiwiZDoxIiwiZDoyIiwieDoxIiwieDowIl0sInN1YiI6ImFjY2Vzc190b2tlbiIsImF0X2hhc2giOiJnQUFBQUFCaXpFZmMzWEFLckJSaXZ1X25sSEhNVmJ2RkNGc2E5ZlRreWI0QjRUY2VDZnVZbkRFRWtfaEdBbWxBVUIzeWZjclA1Qk41SUk0cVVTdGlZNXFlUy01VUgyOGtCS3h6ZFM0Y1dhOXk3Vy1jSkc3eGlUdz0iLCJkaXNwbGF5X25hbWUiOiJLUklTSE5BS1VNQVIgTU9IQU5SQU0iLCJmeV9pZCI6IlhLMTU5NDAiLCJhcHBUeXBlIjoxMDAsInBvYV9mbGFnIjoiTiJ9.ozPEpL4NxfLp0w-VLez6OWHz8M_SbbRcU2kXO3ax4CM"
    fyers = fyersModel.FyersModel(client_id=client_id, token=access_token)
    is_async = True

    data = {
        "symbol": symbol,
        "qty": quantity,
        "type": 2,
        "side": side,
        "productType": type,
        "limitPrice": 0,
        "stopPrice": 0,
        "validity": "DAY",
        "disclosedQty": 0,
        "offlineOrder": "False",
        "stopLoss": 0,
        "takeProfit": 0
    }

    print(data)
    print(fyers.place_order(data))


# generate trading session
access_token = open("access_token.txt", 'r').read()
key_secret = open("api_key.txt", 'r').read().split()
kite = KiteConnect(api_key=key_secret[0])
kite.set_access_token(access_token)
print(kite)


def place_order_zerodha(symbol, quantity, side, type):
    print(symbol, quantity, side, type)
    # Place an intraday market order on NSE
    if type == 'MARGIN':
        type = kite.PRODUCT_NRML
    else:
        type = kite.PRODUCT_MIS

    if side == 1:
        t_type = kite.TRANSACTION_TYPE_BUY
    else:
        t_type = kite.TRANSACTION_TYPE_SELL

    try:

        kite.place_order(tradingsymbol=symbol,
                         exchange=kite.EXCHANGE_NFO,
                         transaction_type=t_type,
                         quantity=quantity,
                         order_type=kite.ORDER_TYPE_MARKET,
                         product=type,
                         variety=kite.VARIETY_REGULAR,
                         )
        print("%" * 30)
        print(dt.now())
        print(symbol, kite.EXCHANGE_NFO, t_type, quantity, kite.ORDER_TYPE_MARKET, type, kite.VARIETY_REGULAR)
        print("%" * 30)

    except Exception as err:
        print("@" * 30)
        print(dt.now())
        print(symbol, kite.EXCHANGE_NFO, t_type, quantity, kite.ORDER_TYPE_MARKET, type, kite.VARIETY_REGULAR)
        traceback.print_exc()
        print(err)
        print("@" * 30)
