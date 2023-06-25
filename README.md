# ts_auth0
Simple Python Auth0 login for Tradestation API v3

BNOTE: Not ready for general use yet! Still in development!

This package is purely for experimental purposes and is not supported by Tradestation https://www.tradestation.com/. Use at your own risk - trading is risky!

I found the Tradestation authenication process to be complicated, so once I figured out the correct procedure and was able to authenicate and get an access token, I wrapped it all into this easy to use Python class for all to enjoy!

ts_auth0 provides a simple Python class which simplifies the Tradestation authentication process.
See https://api.tradestation.com/docs/fundamentals/authentication/auth-overview/ for details of the authentication process ts_auth0 facilitates.

## Overview

This package provides a simple way for your Python scripts to log into Tradestation for API access. The goal is to complete authenication and get an access token used in every API call. 

To start, you provide your API Key and Secret API Key. A simple function call is all that is required to log in and obtain an access token. The access token is then used for all API calls to get market updates, account information, etc.

Please note that this package only addresses authentication. Making API calls is a seperate task and not addresses in this package. But, see the example code below for an example of making an API once you pass authentication and are able to obtain the access token needed for all Tradestation API calls.
 
- Works with Python >= 3.8
- Tested on MacOS and Windows 11

To start, you will need to request API access from Tradestation. See  https://api.tradestation.com/docs/faq#how-do-i-get-an-api-key. Baically you need to do the following:

- Deposit at least $10,000 into Tradestation (!). It may take over a week to get confirmation that the money was deposited and available. Without this deposit your requests for API access will be declined.
- After requesting API access you will receive via email a PDF file that requres a password to view. This file contains your API Key and Secret API Key.

## Getting Started

Install ts_auth0 with:
- pip install ts_auth0

Create a simple Ptyhon script with the following code: 

```
from ts_auth0 import ts_auth0 

ts = TS_Auth("Your API key", "Your Secret key")        
ts.start_auth0()

try:
    
    count = 0
    while True:
        access_token = ts.get_access_token()

        print(ts)

        url = "https://sim-api.tradestation.com/v3/marketdata/barcharts/AAPL?interval=1&unit=minute&barsback=1"
        
        headers = {'Authorization': f'Bearer {access_token}' }

        response = requests.request("GET", url, headers=headers)
        json_data = response.json()
        print(json.dumps(json_data, indent=4, sort_keys=False))

        print(f"Access Token: {access_token[:8]}... {count}")
        time.sleep(60)
        count += 1
    
except TS_Auth.Auth_Error as e:
    print(e)
```

Running this script (python ./test.py) will cause the following:

* A webbrowser should appear with the Tradestation login page. Enter you user name and password.
* If login was successful, the webbrowser should be redirected to http://localhost:3000. You will see this in the webbroswer. The ts_auth0 is listening on port 3000 and will handle the reply.
* Back to your script, when ts.start_auth0() completes you can call ts.get_access_token() and use this access token to call the API. The example script show an eternal while loop that gets AAPL market data every minute.

See the Tradestation documentation to make API calls:

- https://api.tradestation.com/docs/fundamentals/http-requests
- https://api.tradestation.com/docs/fundamentals/http-streaming

## Customization

If you want to get fancy and change some of the parameters used in the authentication process, there are parameters you can modify.

Refer to the sample scripts above. The instantiation of the TS_Auth0 class can contain an optional list of paramters. Here is an example of how to specify the extra parameters:

```
...
parameters = {
    'REDIRECT_URI': 'http://localhost',
    'REDIRECT_PORT': 8080,
    'SHOW_KEYS_IN_STR': True
}
ts = TS_Auth("Your API key", "Your Secret key", **parameters)
...
```

Here is a list of the extra parametersw you can modify:

- BASE_URL (str): The base URL for the auth server
  - Default: https://signin.tradestation.com/authorize
- AUDIENCE (str): The audience for the auth server
  - Default: https://api.tradestation.com
- REDIRECT_PORT (int): The port for the auth server
  - Default: 3000
- REDIRECT_URI (str): The URI for the auth server
  - Default: http://localhost
- SCOPE (str): The scope for the auth server
  - Default: "openid profile MarketData ReadAccount Trade Matrix OptionSpreads offline_access"
- TOKEN_REQUEST_URL (str): The URL for the token request
  - Default: https://signin.tradestation.com/oauth/token
- SHOW_KEYS_IN_STR (bool): Show the API keys in the string representation of the class
  - Default: False




