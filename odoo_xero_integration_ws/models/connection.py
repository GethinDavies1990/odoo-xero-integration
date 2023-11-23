import json
import logging
import time
from . import get_auth_code_server
from . import constants
from . import profile
import requests


class Connection:
    def __init__(self, xero_app_cred=None, default_env=None, xr_tenent=None):
        self.__xero_app_credentials = xero_app_cred
        self.__default_env = default_env
        self.__xr_tenant = xr_tenent

        self.__grant_code = None
        self.__access_token = None
        self.__refresh_token = None

        self.__js_resp = {
            "err_status": True,
            "response": '',
            "addons": None
        }
        self.__logging = logging.getLogger(__name__)

    def reset_response(self):
        self.__js_resp["err_status"] = True
        self.__js_resp["response"] = ""
        self.__js_resp["addons"] = None

    def get_auth_url(self):
        self.reset_response()
        try:
            if self.__xero_app_credentials is not None:
                auth_url = get_auth_code_server.generate_auth_url(
                    self.__xero_app_credentials["client_id"],
                    self.__xero_app_credentials["redirect_url"]
                )

                if auth_url != '':
                    self.__js_resp["response"] = auth_url
                    self.__js_resp["err_status"] = False
                else:
                    self.__js_resp["response"] = constants.XR_CONN_URL_FAILED
            else:
                self.__js_resp["response"] = constants.XR_CONN_CRED_NOTFND
        except Exception as ex:
            self.__logging.exception("Connection GEN URL Except: "+str(ex))
            self.__js_resp["response"] = constants.XR_CONN_URL_EXCEPT
        return self.__js_resp

    def get_access_token(self):
        return self.__access_token

    def get_refresh_token(self):
        return self.__refresh_token

    def generate_access_token(self, grant_code):
        self.reset_response()
        try:
            response = get_auth_code_server.get_authorize_token(
                        grant_code,
                        self.__xero_app_credentials["client_id"],
                        self.__xero_app_credentials["client_secret"],
                        self.__xero_app_credentials["redirect_url"]
                    )

            if 'error' not in response:
                if 'access_token' in response:
                    self.__access_token = response["access_token"]
                if 'refresh_token' in response:
                    self.__refresh_token = response["refresh_token"]
                self.__js_resp["err_status"] = False
            else:
                self.__js_resp["response"] = constants.XR_CONN_CRED_ACS_FAILED
        except Exception as ex:
            self.__logging.exception("Connection Credential Failed: "+str(ex))
            self.__js_resp["response"] = constants.XR_CONN_CRED_ACS_EXCEPT
        return self.__js_resp

    def refresh_access_token(self, refresh_token):
        self.reset_response()
        try:
            resp = get_auth_code_server.get_refresh_authorize_token(
                refresh_token,
                self.__xero_app_credentials["client_id"],
                self.__xero_app_credentials["client_secret"]
            )
            if 'error' not in resp:
                if 'access_token' in resp:
                    self.__access_token = resp['access_token']
                if 'refresh_token' in resp:
                    self.__refresh_token = resp["refresh_token"]
                self.__js_resp["err_status"] = False
            else:
                self.__js_resp["response"] = constants.XR_CONN_RAT_FAILED
        except Exception as ex:
            self.__logging.exception("Connection RAT Exception: " + str(ex))
            self.__js_resp["response"] = constants.XR_CONN_RAT_EXCEPT
        return self.__js_resp

    def get_msv_access_token(self):
        self.reset_response()
        try:
            db_cursor = self.__default_env[constants.XERO_CREDENTIALS_MODEL]
            db_rows = db_cursor.search([])

            if db_rows and len(db_rows) > 0:
                _db_row = db_rows[constants.DEFAULT_INDEX]
                _resp_acc_token = _db_row.access_token

                if _resp_acc_token and _resp_acc_token != "":
                    max_attempt = constants.ACCESS_TOKEN_ATTEMPT
                    while max_attempt > 0:
                        _profile = profile.Profile(xr_access_token=_resp_acc_token, xr_tenant=self.__xr_tenant)
                        p_response = _profile.get_profile()

                        if not p_response["err_status"]:
                            self.__js_resp["response"] = _resp_acc_token
                            self.__js_resp["err_status"] = False
                            self.__js_resp["addons"] = p_response["response"]
                            break

                        elif constants.RESPONSE_ERR_TITLE in p_response["response"] \
                                and p_response["response"][constants.RESPONSE_ERR_TITLE] \
                                in constants.RESPONSE_ERR_TL_VALUES:

                            rat_response = self.refresh_access_token(refresh_token=_db_row.refresh_token)
                            time.sleep(2)

                            if not rat_response["err_status"]:
                                _resp_acc_token = self.get_access_token()
                                _db_row.access_token = self.get_access_token()
                                if self.get_refresh_token():
                                    _db_row.refresh_token = self.get_refresh_token()
                                db_cursor.update(_db_row)
                            else:
                                self.__js_resp["response"] = constants.ACCESS_TOKEN_ERR_REFRESH
                        else:
                            self.__js_resp["response"] = constants.ACCESS_TOKEN_INVALID
                        max_attempt -= 1
                else:
                    self.__js_resp["response"] = constants.ACCESS_TOKEN_NOTFOUND
            else:
                self.__js_resp["response"] = constants.ACCESS_TOKEN_CRED_NTFND
        except Exception as ex:
            self.__logging.exception("Unable to get auth credentials: " + str(ex))
            self.__js_resp["response"] = constants.ACCESS_TOKEN_EXCEPT
            # resp = constants.ACCESS_TOKEN_EXCEPT
        return self.__js_resp
