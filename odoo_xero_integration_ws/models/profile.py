import logging
import requests
from . import constants


class Profile:
    def __init__(self, xr_access_token, xr_tenant):
        self.__logging = logging.getLogger(__name__)

        self.__base_endpoint = constants.XR_BASE_URL
        self.__req_version = constants.XR_APP_VERSION
        self.__req_timeout = constants.XR_REQ_TIMEOUT
        self.__xr_tenant = xr_tenant

        self.__users_api = constants.XR_USER_LINK

        self.__xr_access_token = xr_access_token
        self.__req_headers = {
            "Authorization": "Bearer " + self.__xr_access_token,
            "Accept": "application/json",
            "Xero-tenant-id": self.__xr_tenant.tenant_id
        }

        self.__js_resp = {
            "err_status": True,
            "response": "",
            "addons": None
        }

    def reset_response(self):
        self.__js_resp["err_status"] = True
        self.__js_resp["response"] = ""
        self.__js_resp["addons"] = None

    def get_profile(self):
        self.reset_response()
        try:
            req_url = self.__base_endpoint + self.__req_version + self.__users_api
            resp = requests.get(req_url, headers=self.__req_headers).json()

            if resp[constants.XR_RESPONSE_STATUS_KEY] == constants.XR_RESPONSE_STATUS_VALUE:
                if len(resp[constants.XR_USER_RESPONSE_KEY]) > 0:
                    self.__js_resp["err_status"] = False
            self.__js_resp["response"] = resp
        except Exception as ex:
            self.__logging.exception("Profile Exception: " + str(ex))
            self.__js_resp["response"] = constants.XR_USER_SERV_FETCH_EXCEPT
        return self.__js_resp
