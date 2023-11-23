import requests
import json
from . import constants
from base64 import b64encode


def generate_auth_url(client_id, redirect_uri):
    auth_url = constants.XR_AUTH_URL + '?response_type=code&client_id=' +\
               client_id + '&redirect_uri=' + redirect_uri + '&scope=' +\
               ' '.join(constants.XR_SCOPES) + '&state=123'
    return auth_url


def get_authorize_token(code, client_id, client_secret, redirect_uri):
    params = {
        "code": code,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    headers = {
        "Authorization": "Basic " + b64encode(str(client_id + ":" + client_secret).encode('utf-8')).decode("utf-8"),
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(constants.XR_AUTH_EXCODE_URL, data=params, headers=headers)
    rcont = json.loads(response.content)
    return rcont


def get_refresh_authorize_token(refresh_token, client_id, client_secret):
    params = {
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }
    headers = {
        "Authorization": "Basic " + b64encode(str(client_id + ":" + client_secret).encode('utf-8')).decode("utf-8"),
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(constants.XR_AUTH_EXCODE_URL, data=params, headers=headers)
    rcont = json.loads(response.content)
    return rcont
