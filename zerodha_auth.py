from kiteconnect import KiteConnect
from selenium import webdriver
import time
import os
from pyotp import TOTP

from selenium.webdriver.common.keys import Keys


def zerodha_connect_first():
    def autologin():
        token_path = "api_key.txt"
        key_secret = open(token_path, 'r').read().split()
        kite = KiteConnect(api_key=key_secret[0])
        service = webdriver.chrome.service.Service('chromedriver')
        service.start()
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options = options.to_capabilities()
        driver = webdriver.Remote(service.service_url, options)

        # driver = webdriver.Remote(service.service_url)
        driver.get(kite.login_url())
        driver.implicitly_wait(10)

        username = driver.find_element('xpath', '// *[ @ id = "userid"]')
        password = driver.find_element('xpath', '// *[ @ id = "password"]')
        username.send_keys(key_secret[2])
        password.send_keys(key_secret[3])
        driver.find_element('xpath', '/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[4]/button').click()
        totp = driver.find_element('xpath', '//*[@id="totp"]')
        totp_token = TOTP(key_secret[4])

        token = totp_token.now()
        totp.send_keys(token)
        driver.find_element('xpath', '/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[3]/button').click()
        time.sleep(10)
        request_token = driver.current_url.split('&request_token=')[1]
        try:
            request_token = request_token.split('&')[0]
        except:
            pass
        print(request_token)
        with open('request_token.txt', 'w') as the_file:
            the_file.write(request_token)
        driver.quit()

    autologin()

    # generating and storing access token - valid till 6 am the next day
    request_token = open("request_token.txt", 'r').read()
    key_secret = open("api_key.txt", 'r').read().split()
    kite = KiteConnect(api_key=key_secret[0])
    data = kite.generate_session(request_token, api_secret=key_secret[1])
    with open('access_token.txt', 'w') as file:
        file.write(data["access_token"])
    return kite


def zerodha_connect():
    try:
        access_token = open("access_token.txt", 'r').read()
        key_secret = open("api_key.txt", 'r').read().split()
        kite = KiteConnect(api_key=key_secret[0])
        kite.set_access_token(access_token)
        (kite.ltp('NSE:NIFTY 50'))
        return kite
    except:
        return zerodha_connect_first()


if __name__ == '__main__':
    kite = zerodha_connect()
    print(kite.ltp('NSE:NIFTY 50'))
    print(kite.profile())
