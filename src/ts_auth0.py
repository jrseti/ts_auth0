# -*- coding: utf-8 -*-
"""
Script: ts_auth0
Description: This script handles the authentication process for the Tradestation API
Author: Jon Richards, jrseti@gmail.com
Copyrite: 2023, Jon Richards
Licence: MIT
"""
import requests
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import string
import random
import time
import copy
import os

__author__ = "Jon Richards"
__copyright__ = "Copyright 2023, Jon Richards"
__credits__ = ["Jon Richards"]
__license__ = "MIT"
__version__ = "0.0.14"
__maintainer__ = "Jon Richards"
__email__ = "jrseti@gmail.com"
__status__ = "Dev"

class TS_Auth: 

    """This class handles the authentication process for the Tradestation API"""

    _DEFAULT_PARAMETERS = {
        "BASE_URL" : "https://signin.tradestation.com/authorize",
        "AUDIENCE" : "https://api.tradestation.com",
        "REDIRECT_PORT" : 3000,
        "REDIRECT_URI" : "http://localhost",
        "SCOPE" : "openid profile MarketData ReadAccount Trade Matrix OptionSpreads offline_access",
        "TOKEN_REQUEST_URL" : "https://signin.tradestation.com/oauth/token",
        "SHOW_KEYS_IN_STR" : False,
        "REFRESH_TOKEN_CACHE_FILE" : "refresh_token_cache.txt"
    }

    def __init__(self, 
                 api_key, api_secret_key, 
                 **parameters):  
        """Initialize the TS_Auth class
        Args:
            api_key (str): Tradestation API key
            api_secret_key (str): Tradestation API secret key
            parameters (dict): Optional parameters
                BASE_URL (str): The base URL for the auth server
                    Default: https://signin.tradestation.com/authorize
                AUDIENCE (str): The audience for the auth server
                    Default: https://api.tradestation.com
                REDIRECT_PORT (int): The port for the auth server
                    Default: 3000
                REDIRECT_URI (str): The URI for the auth server
                    Default: http://localhost
                SCOPE (str): The scope for the auth server
                    Default: "openid profile MarketData ReadAccount Trade Matrix OptionSpreads offline_access"
                TOKEN_REQUEST_URL (str): The URL for the token request
                    Default: https://signin.tradestation.com/oauth/token
                SHOW_KEYS_IN_STR (bool): Show the API keys in the string representation of the class
                    Default: False
                REFRESH_TOKEN_CACHE_FILE (str): The file to cache the refresh token
                    Default: refresh_token_cache.txt

        Raises:
            Auth_Error: Invalid parameter
        """

        # Make sure all the parameters are valid.
        for key in parameters:
            if key not in TS_Auth._DEFAULT_PARAMETERS:
                raise TS_Auth.Auth_Error("Invalid parameter: " + key)
            
        self._api_key = api_key
        self._api_secret_key = api_secret_key

        # Make sure all the necessary parameters have been specified.
        self._parameters = copy.deepcopy(parameters)
        if "BASE_URL" not in parameters:
            self._parameters["BASE_URL"] = TS_Auth._DEFAULT_PARAMETERS["BASE_URL"]
        if "AUDIENCE" not in parameters:
            self._parameters["AUDIENCE"] = TS_Auth._DEFAULT_PARAMETERS["AUDIENCE"]
        if "REDIRECT_PORT" not in parameters:
            self._parameters["REDIRECT_PORT"] = TS_Auth._DEFAULT_PARAMETERS["REDIRECT_PORT"]
        if "REDIRECT_URI" not in parameters:
            self._parameters["REDIRECT_URI"] = TS_Auth._DEFAULT_PARAMETERS["REDIRECT_URI"]
        if "SCOPE" not in parameters:
            self._parameters["SCOPE"] = TS_Auth._DEFAULT_PARAMETERS["SCOPE"]
        if "TOKEN_REQUEST_URL" not in parameters:
            self._parameters["TOKEN_REQUEST_URL"] = TS_Auth._DEFAULT_PARAMETERS["TOKEN_REQUEST_URL"]
        if "SHOW_KEYS_IN_STR" not in parameters:
            self._parameters["SHOW_KEYS_IN_STR"] = TS_Auth._DEFAULT_PARAMETERS["SHOW_KEYS_IN_STR"] 
        if "REFRESH_TOKEN_CACHE_FILE" not in parameters:
            self._parameters["REFRESH_TOKEN_CACHE_FILE"] = TS_Auth._DEFAULT_PARAMETERS["REFRESH_TOKEN_CACHE_FILE"]
     
        # Initialize the class variables.
        self._code = None
        self._access_end_of_life = 0
        self._access_token = None
        self._refresh_token = None
        self._keep_running = False;

    def __str__(self):
        """Return a string representation of the TS_Auth class
        Returns:
            str: A string representation of the TS_Auth class
        """

        description  = "BASE_URL:\t\t" + self._parameters["BASE_URL"] + "\n"
        description += "AUDIENCE:\t\t" + self._parameters["AUDIENCE"] + "\n"
        description += "REDIRECT_PORT:\t\t" + str(self._parameters["REDIRECT_PORT"]) + "\n"
        description += "REDIRECT_URI:\t\t" + self._parameters["REDIRECT_URI"] + "\n"
        description += "SCOPE:\t\t\t" + self._parameters["SCOPE"] + "\n"
        description += "TOKEN_REQUEST_URL:\t" + self._parameters["TOKEN_REQUEST_URL"] + "\n"
        description += "Code:\t\t\t" + str(self._code) + "\n"
        description += "Access End of Life:\t" + str(self._access_end_of_life) + "\n"
        description += "Access Token:\t\t" + str(self._access_token) + "\n"
        description += "Refresh Token:\t\t" + str(self._refresh_token) + "\n"
        if self._parameters["SHOW_KEYS_IN_STR"]:
            description += "API Key:\t\t" + str(self._api_key) + "\n"
            description += "API Secret Key:\t\t" + str(self._api_secret_key) + "\n"
        else:
            description += "API Key hidden\n"
            description += "API Secret Key hdden\n"

        return description    

    class Auth_Error(Exception):
        """Base class for exceptions in this module."""
        pass

    class _RequestHandler(BaseHTTPRequestHandler):
        """Handles the HTTP requests for the auth server
        Inherits from BaseHTTPRequestHandler"""
        parent = None

        def do_GET(self):
            """Handle a GET request"""

            # Prepare the response and header
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = ""

            if "code=" in self.path and "state=" in self.path:
                parts = self.path.split("&")
                code = parts[0].split("code=")[1]
                state = parts[1].split("state=")[1]
                if(state == self.parent.state_string):
                    self.parent._code = code
                    message = b"<html><body><h1>Success: Code received.</h1>Your program should receive a token.</body></html>"
                else:
                    message = b"<html><body><h1>Error: Invalid state value, not authenticated</h1>Not possible to get token.</body></html>"

            self.wfile.write(message)
            self.parent._keep_running = False
    

    def start_auth0(self, timeout_secs=10):
        """Start the auth0 process
        Args:
            timeout_secs (int): The number of seconds to wait for the auth server to respond. Default: 10
        Raises:
            Auth_Error: The auth server did not respond within the specified timeout period.
        """

        if self._attempt_getting_access_token() is True:
            print("Access token already exists and is valid, skipping login")
            return;

        self._returned_code = None
        self._keep_running = True;

        server_address = ('localhost', self._parameters["REDIRECT_PORT"])
   
        # Create an HTTP server and a handler class
        # Tell the request handler class who its parent is so the received code can be
        # passed back.
        TS_Auth._RequestHandler.parent = self
        httpd = HTTPServer(server_address, TS_Auth._RequestHandler)
        httpd.timeout = 1 #
        
        # Generate a random string for the state parameter
        # TS_Auth._RequestHandler will check that the state parameter is returned by the auth server
        self.state_string = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k=33))
        
        # Build the URL for the auth request
        url_params = {
            'response_type': 'code',
            'client_id': self._api_key,
            'audience': self._parameters["AUDIENCE"],
            'redirect_uri': self._constructRedirectURI(),
            'scope': self._parameters["SCOPE"],
            'state': self.state_string
        }
        url = f'{self._parameters["BASE_URL"]}?{urllib.parse.urlencode(url_params)}'
        
        # Open the browser and request the url, requiring the user to manually login
        webbrowser.open(url)
        
        # Wait for the auth server to report the code. _RequestHandler do_Get() will set self._code
        count_for_timeout = timeout_secs
        while self._keep_running:
            if(count_for_timeout == 0):
                raise self.Auth_Error(f'{timeout_secs} second Timeout waiting for auth response using request: {url}')
                break
            count_for_timeout -= 1
            httpd.handle_request() # Will return after {httpd.timeout} seconds if no request received
        
        # Check if we got a code and raise an exception if not
        if(self._code == None):
            raise self.Auth_Error(f'No code received from auth request: {url}')
        
        # Get the refresh token
        self._get_refresh_token()

        if self._refresh_token == None:
            raise self.Auth_Error("No refresh token received")

        # We are now authorized, the user can now call get_access_token() to get an access token
        # which requires the refresh token.
    
        return True
    
    def get_access_token(self):
        """Get an access token
        Returns:
            str: The access token, exception is there was an error
        Note: start_auth0() must have been called first and there must be a valid refresh token
        """

        if self._refresh_token == None:
            raise self.Auth_Error("No refresh token, you must call start_auth0() first")
        
        # Check if the access token is still valid, it times out usually after 1200 seconds
        if time.time() < self._access_end_of_life:
            print(f"Access token is still valid, {self._access_end_of_life - time.time()} seconds left until expiration")
            return self._access_token
        print("Access token is expired, requesting a new one...")
        
        # Get a new access token
        url = "https://signin.tradestation.com/oauth/token"
        payload_params = {
            'grant_type' : 'refresh_token',
            'client_id': self._api_key,
            'client_secret': self._api_secret_key,
            'refresh_token' : self._refresh_token,
            'redirect_uri' : self._constructRedirectURI()
            }

        payload = urllib.parse.urlencode(payload_params)
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            response_data = response.json()
            # Calculate the end of life for the access token, which is 30 seconds less than the expires_in value
            self._access_end_of_life = int(response_data['expires_in']) + int(time.time()) - 30
            self._access_token = response_data['access_token']
        except:
            raise self.Auth_Error("Error getting access token, try again")

        return response_data['access_token']
    
    def _attempt_getting_access_token(self):
        """Attempt to get an access token using the previous refresh token
        Args:
            previous_refresh_token (str): The previous refresh token
        Returns:
            str: The access token, None if there was an error
        """
        token_cache_file = self._parameters["REFRESH_TOKEN_CACHE_FILE"]
        if os.path.exists(token_cache_file) == False:
            return False;
    
        with open(token_cache_file, 'r') as f:
            previous_refresh_token = f.read()
            self._refresh_token = previous_refresh_token
            print(f"Attempting to get access token using previous refresh token {self._refresh_token}")
            try:
                self.get_access_token()
                print("Got access token using previous refresh token")
                return True
            except:
                print("Error getting access token using previous refresh token")
                return False
    
    def _constructRedirectURI(self):
        """Construct the actual redirect URI from the server name and port.
        If the server port is None, then the port is not included in the URI
        Returns:
            str: The redirect URI
        """ 
        return f'{self._parameters["REDIRECT_URI"]}:{self._parameters["REDIRECT_PORT"]}'      

    def _get_refresh_token(self):
        """Get a refresh token"""

        # Check if we have a code, else raise an exception
        if self._code is None:
            raise self.Auth_Error("No code, you must call start_auth0() first")
        
        # Get the refresh token
        url = "https://signin.tradestation.com/oauth/token"
        payload_params = {
            'grant_type' : 'authorization_code',
            'client_id': self._api_key,
            'client_secret': self._api_secret_key,
            'code' : self._code,
            'redirect_uri' : self._constructRedirectURI()
        }
        payload = urllib.parse.urlencode(payload_params)
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            response_data = response.json()
            self._refresh_token = response_data['refresh_token']
            # Save the refresh token to a file
            token_cache_file = self._parameters["REFRESH_TOKEN_CACHE_FILE"]
            with open(token_cache_file, 'w') as f:
                f.write(self._refresh_token)
            return
        except:
            raise self.Auth_Error("Error getting refresh token, try again")
        
