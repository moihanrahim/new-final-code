from fyers_api import fyersModel
from fyers_api import accessToken


client_id ="EGNBLDBRXZ-100"
secret_key= "7LMUVLXZ6Z"
response_type = "code"
grant_type ="authorization_code"
redirect_uri = "https://trade.fyers.in/"

session=accessToken.SessionModel(client_id=client_id,
secret_key=secret_key,redirect_uri=redirect_uri,
response_type=response_type, grant_type=grant_type,state="jef")

url  = session.generate_authcode()
print(url)

# selenium automation to be done
# options = webdriver.ChromeOptions()
#     options.add_argument('--headless')
#     options = options.to_capabilities()
#     driver = webdriver.Remote(service.service_url, options)
#     driver.get(kite.login_url())
#     driver.implicitly_wait(10)
#     username = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[1]/input')
#     password = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[2]/input')
#     username.send_keys(key_se

auth_code = input()
print(auth_code)

session.set_token(auth_code)
response = session.generate_token()
print(response)

access_token = response["access_token"]
print(access_token)

fyers = fyersModel.FyersModel(client_id=client_id, token=access_token)
is_async = True

print(fyers)