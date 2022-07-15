from csv import DictWriter
# Libraries
import pandas as pd
import requests
import json
import math
from demat_connecter import place_order as place_order
from datetime import datetime as dt
from datetime import timedelta
from dateutil.relativedelta import relativedelta, TH
import os
from zerodha_auth import zerodha_connect
import datetime as DT
import dateutil.relativedelta as REL

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
    print(request.text)
    cookies = dict(request.cookies)


def get_data(url):
    set_cookie()
    while True:
        try:
            response = sess.get(url, headers=headers, timeout=5, cookies=
            cookies)
            print(response.text)
            break
        except:
            pass

    if (response.status_code == 401):
        set_cookie()
        response = sess.get(url_nf, headers=headers, timeout=5, cookies=cookies)
        print(response.text)

    if (response.status_code == 200):
        print(response.text)

        return response.text
    return ""

#
# def set_header():
#     global bnf_ul
#     global nf_ul
#     global bnf_nearest
#     global nf_nearest
#     response_text = get_data(url_indices)
#     data = json.loads(response_text)
#     for index in data["data"]:
#         if index["index"] == "NIFTY 50":
#             nf_ul = index["last"]
#             print("nifty")
#         if index["index"] == "NIFTY BANK":
#             bnf_ul = index["last"]
#             print("banknifty")
#     bnf_nearest = nearest_strike_bnf(bnf_ul)
#     nf_nearest = nearest_strike_nf(nf_ul)


def custom_algo(date_format_final, nearest, quantity, strategy, option, normal_order):
    if not normal_order:
        if strategy == "MARGIN":
            if option == "buy":
                place_order("NIFTY{}{}PE".format(date_format_final, nearest), quantity, 1, strategy)
                place_order("NIFTY{}{}PE".format(date_format_final, nearest - 200), quantity, -1, strategy)
            else:
                place_order("NIFTY{}{}CE".format(date_format_final, nearest), quantity, 1, strategy)
                place_order("NIFTY{}{}CE".format(date_format_final, nearest + 200), quantity, -1, strategy)
        else:
            if option == "buy":
                place_order("NIFTY{}{}PE".format(date_format_final, nearest), quantity, 1, strategy)
            else:
                place_order("NIFTY{}{}CE".format(date_format_final, nearest), quantity, 1, strategy)
    else:
        if strategy == "MARGIN":
            if option == "buy":
                place_order("NIFTY{}{}PE".format(date_format_final, nearest - 200), quantity, 1, strategy)
                place_order("NIFTY{}{}PE".format(date_format_final, nearest), quantity, -1, strategy)
            else:
                place_order("NIFTY{}{}CE".format(date_format_final, nearest + 200), quantity, 1, strategy)
                place_order("NIFTY{}{}CE".format(date_format_final, nearest), quantity, -1, strategy)
        else:
            if option == "buy":
                place_order("NIFTY{}{}PE".format(date_format_final, nearest), quantity, -1, strategy)
            else:
                place_order("NIFTY{}{}CE".format(date_format_final, nearest), quantity, -1, strategy)


def algo_imp(option, strategy, expiry, index="", ul=0, nearest=0, quantity=0, normal_order=True):
    end_of_month = dt.today() + relativedelta(day=31)
    last_thursday = end_of_month + relativedelta(weekday=TH(-1))
    last_before_thursday = last_thursday - timedelta(days=7)
    expiry = dt.strptime(expiry, "%d-%b-%Y")

    def monthly_expiry(expiry):
        date_formateed = str(expiry)[:10]
        year = date_formateed[2:4]
        month = (expiry.strftime("%B"))
        month = (month.upper())[:3]
        date_format_final = year + month
        return date_format_final

    def weekly_expiry(expiry):
        date_formateed = str(expiry)[:10]
        year = date_formateed[2:4]
        month = str(int(date_formateed[5:7]))
        if month == '10':
            month = "O"
        if month == '11':
            month = "N"
        if month == '12':
            month = "D"

        day = str(int(date_formateed[8:10]))
        date_format_final = year + month + day
        return date_format_final

    if last_before_thursday <= dt.today() <= end_of_month:
        # monthly expiry
        date_format_final = monthly_expiry(expiry)
    elif strategy == "MARGIN":
        if last_thursday <= expiry <= end_of_month:
            date_format_final = monthly_expiry(last_thursday +  timedelta(days=7))
        else:
            date_format_final = monthly_expiry(expiry)

    else:
        # weekly expiry
        if expiry == dt.now():
            expiry = expiry + timedelta(days=7)
            if last_before_thursday <= expiry <= end_of_month:
                # monthly expiry
                date_format_final = monthly_expiry(expiry)
            else:
                date_format_final = weekly_expiry(expiry)
        else:
            date_format_final = weekly_expiry(expiry)

    def insert_nearest(date_format_final, nearest, quantity, strategy, option, entry):

        field_names = ['nearest', 'quantity',
                       'strategy', 'option', "entry"]

        # Dictionary
        dict = {'nearest': nearest, 'quantity': quantity, 'strategy': strategy,
                'option': option, "entry": entry}

        # Open your CSV file in append mode
        # Create a file object for this file
        with open('{}_{}.csv'.format(option, strategy), 'a') as f_object:
            # Pass the file object and a list
            # of column names to DictWriter()
            # You will get a object of DictWriter
            dictwriter_object = DictWriter(f_object, fieldnames=field_names)

            # Pass the dictionary as an argument to the Writerow()
            dictwriter_object.writerow(dict)

            # Close the file object
            f_object.close()


    def multi_close( date_format_final, nearest, quantity, strategy, option, normal_order):
        import os
        file = option+strategy
        if os.stat("{}.csv".format(file)).st_size == 0:
            print('empty')
        existing_alert = pd.read_csv("{}.csv".format(file), header=None)
        existing_alert.columns = ['strike', 'quantity', 'strategy', 'option', 'entry']
        nearest_list = list(existing_alert['strike'])
        for nearest in nearest_list:
            custom_algo(date_format_final, nearest, quantity, strategy, option, normal_order)

        return nearest

    if not normal_order:
        multi_close(date_format_final, nearest, quantity, strategy, option, normal_order)
    else:
        custom_algo(date_format_final, nearest, quantity, strategy, option, normal_order)
    insert_nearest(date_format_final, nearest, quantity, strategy, option, normal_order)


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

from datetime import date

def algo(option, strategy, quantity, normal_order=True):
    # set_header()
    print('\033c')
    kite = zerodha_connect()
    ltp = ((kite.ltp('NSE:NIFTY 50'))["NSE:NIFTY 50"])["last_price"]
    # if normal_order:
    nf_nearest = nearest_strike_nf(ltp)

    today = DT.date.today()
    rd = REL.relativedelta(days=1, weekday=REL.TH)
    next_thursday = today + rd
    next_thursday =str(next_thursday.strftime('%d-%b-%Y') )
    algo_imp(option, strategy, next_thursday, "Nifty", 0, nf_nearest, quantity, normal_order)


if __name__ == '__main__':
    algo("buy", "INTRADAY", 50)
    # algo("sell", "INTRADAY", 50, False)
    # algo("sell", "INTRADAY", 50)
    # algo("buy", "INTRADAY", 50, False)
    # algo("buy", "MARGIN", 50)
    # algo("sell", "MARGIN", 50, False)
    # algo("sell", "MARGIN", 50)
    # algo("buy", "MARGIN", 50, False)

#     1 signal entry signal --> margin -->  order -->  job (every 10 min ) --> web -->  100 , 50  points same buy strategy place order  --> check 100 points ( one time crossing )  --> exit signal
# #
#  1 signal entry signal --> margin/intraday -->  ++ 100, 50 crossing over -->  job (every 10 min ) --> web -->  100 points same buy strategy place order  --> check 100 points ( one time crossing )  --> exit signal
# #
