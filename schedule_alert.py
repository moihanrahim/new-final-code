import schedule
import time
import os
import pandas as pd
import schedule
import time
from algo_trading import algo_imp
from csv import DictWriter
# Libraries
import pandas as pd
import requests
import json
import math
from datetime import datetime as dt
from datetime import timedelta
from dateutil.relativedelta import relativedelta, TH
import os
from zerodha_auth import zerodha_connect


def print_hr():
    print(strYellow("|".rjust(200, "-")))


# Fetching CE and PE data based on Nearest Expiry Date
def print_oi(num, step, nearest, url):
    strike = nearest - (step * num)
    start_strike = nearest - (step * num)
    response_text = get_data(url)
    data = json.loads(response_text)
    currExpiryDate = data["records"]["expiryDates"][0]
    # print(currExpiryDate)
    return currExpiryDate


# Finding highest Open Interest of People's in CE based on CE data
def highest_oi_CE(num, step, nearest, url):
    strike = nearest - (step * num)
    start_strike = nearest - (step * num)
    response_text = get_data(url)
    data = json.loads(response_text)
    currExpiryDate = data["records"]["expiryDates"][0]
    max_oi = 0
    max_oi_strike = 0
    for item in data['records']['data']:
        if item["expiryDate"] == currExpiryDate:
            if item["strikePrice"] == strike and item["strikePrice"] < start_strike + (step * num * 2):
                if item["CE"]["openInterest"] > max_oi:
                    max_oi = item["CE"]["openInterest"]
                    max_oi_strike = item["strikePrice"]
                strike = strike + step
    return max_oi_strike


# Finding highest Open Interest of People's in PE based on PE data
def highest_oi_PE(num, step, nearest, url):
    strike = nearest - (step * num)
    start_strike = nearest - (step * num)
    response_text = get_data(url)
    data = json.loads(response_text)
    currExpiryDate = data["records"]["expiryDates"][0]
    max_oi = 0
    max_oi_strike = 0
    for item in data['records']['data']:
        if item["expiryDate"] == currExpiryDate:
            if item["strikePrice"] == strike and item["strikePrice"] < start_strike + (step * num * 2):
                if item["PE"]["openInterest"] > max_oi:
                    max_oi = item["PE"]["openInterest"]
                    max_oi_strike = item["strikePrice"]
                strike = strike + step
    return max_oi_strike


def strRed(skk):
    return "\033[91m {}\033[00m".format(skk)


def strGreen(skk):
    return "\033[92m {}\033[00m".format(skk)


def strYellow(skk):
    return "\033[93m {}\033[00m".format(skk)


def strLightPurple(skk):
    return "\033[94m {}\033[00m".format(skk)


def strPurple(skk):
    return "\033[95m {}\033[00m".format(skk)


def strCyan(skk):
    return "\033[96m {}\033[00m".format(skk)


def strLightGray(skk):
    return "\033[97m {}\033[00m".format(skk)


def strBlack(skk):
    return "\033[98m {}\033[00m".format(skk)


def strBold(skk):
    return "\033[1m {}\033[0m".format(skk)


# Method to get nearest strikes
def round_nearest(x, num=50):
    return int(math.ceil(float(x) / num) * num)


def nearest_strike_bnf(x):
    return round_nearest(x, 100)


def nearest_strike_nf(x):
    return round_nearest(x, 50)


# Urls for fetching Data
url_oc = "https://www.nseindia.com/option-chain"
url_bnf = 'https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY'
url_nf = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
url_indices = "https://www.nseindia.com/api/allIndices"

# Headers
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
    'accept-language': 'en,gu;q=0.9,hi;q=0.8',
    'accept-encoding': 'gzip, deflate, br'}

sess = requests.Session()
cookies = dict()


# Local methods
def set_cookie():
    request = sess.get(url_oc, headers=headers, timeout=5)
    cookies = dict(request.cookies)


def get_data(url):
    set_cookie()
    while True:
        try:
            response = sess.get(url, headers=headers, timeout=5, cookies=
            cookies)
            break
        except:
            pass

    if (response.status_code == 401):
        set_cookie()
        response = sess.get(url_nf, headers=headers, timeout=5, cookies=cookies)
    if (response.status_code == 200):
        return response.text
    return ""


def set_header():
    global bnf_ul
    global nf_ul
    global bnf_nearest
    global nf_nearest
    response_text = get_data(url_indices)
    data = json.loads(response_text)
    for index in data["data"]:
        if index["index"] == "NIFTY 50":
            nf_ul = index["last"]
            print("nifty")
        if index["index"] == "NIFTY BANK":
            bnf_ul = index["last"]
            print("banknifty")
    bnf_nearest = nearest_strike_bnf(bnf_ul)
    nf_nearest = nearest_strike_nf(nf_ul)


def tick():
    # today is market day , dont go into the loop

    while True:
        try:
            kite = zerodha_connect()
            ltp = ((kite.ltp('NSE:NIFTY 50'))["NSE:NIFTY 50"])["last_price"]
            nf_nearest = nearest_strike_nf(ltp)
            break
        except:
            print("unable to fetch nse data")


    files = ["buy_INTRADAY","sell_INTRADAY","buy_MARGIN","sell_MARGIN"]

    for file in files:
        import os
        if os.stat("{}.csv".format(file)).st_size == 0:
            print('empty')
            continue
        existing_alert = pd.read_csv("{}.csv".format(file), header=None)
        existing_alert.columns = ['strike', 'quantity', 'strategy', 'option', 'entry']

        if False in set(existing_alert["entry"]):
            f = open("{}.csv".format(file), "w+")
            f.close()

        else:

            nearest = (existing_alert).iloc[-1,0]
            quantity =(existing_alert).iloc[-1,1]
            strategy = (existing_alert).iloc[-1,2]
            option =(existing_alert).iloc[-1,3]
            if strategy == "INTRADAY":

                if ltp >= nearest + 50:
                    expiry = print_oi(10, 50, nf_nearest, url_nf)
                    nf_ul = 0
                    algo_imp(option, strategy, expiry, "Nifty", nf_ul, nf_nearest, quantity, True)
            else:
                if ltp >= nearest + 100:
                    expiry = print_oi(10, 50, nf_nearest, url_nf)
                    nf_ul = 0
                    algo_imp(option, strategy, expiry, "Nifty", nf_ul, nf_nearest, quantity, True)
                        # option, strategy, expiry, index = "", ul = 0, nearest, quantity,True




def start_schedule():
    schedule.every(1).minutes.do(tick)

    while True:
        schedule.run_pending()
        time.sleep(1)


#
if __name__ == '__main__':
    # tick()
    start_schedule()

