import logging
import requests
from . import constants


class Tenant:
    def __init__(self, xr_access_token, self_env):
        self.__logging = logging.getLogger(__name__)

        self.__tenant_endpoint = constants.XR_TENANT_URL
        self.__req_timeout = constants.XR_REQ_TIMEOUT
        self.__selfenv = self_env
        self.__xr_access_token = xr_access_token
        self.__req_headers = {
            "Authorization": "Bearer " + self.__xr_access_token,
            "Accept": "application/json",
        }
        self.__js_resp = {
            "err_status": True,
            "response": "",
        }

    def reset_response(self):
        self.__js_resp["err_status"] = True
        self.__js_resp["response"] = ""

    def save_tenant_info(self):
        self.reset_response()
        try:
            resp = requests.get(self.__tenant_endpoint, headers=self.__req_headers).json()

            if constants.RESPONSE_ERR_TITLE in resp and \
                    resp[constants.RESPONSE_ERR_TITLE] in constants.RESPONSE_ERR_TL_VALUES:
                self.__js_resp["response"] = resp[constants.RESPONSE_ERR_DETAILS]
            else:
                for tenant in resp:
                    self.__selfenv[constants.XERO_TENANTS_MODEL].create({
                        "uid": tenant["id"],
                        "name": tenant["tenantName"],
                        "tenant_id": tenant["tenantId"],
                        "tenant_type": tenant["tenantType"]
                    })
                self.__js_resp["err_status"] = False
        except Exception as ex:
            self.__logging.exception("Tenant Exception: " + str(ex))
            self.__js_resp["response"] = constants.XR_TENANT_SERV_FETCH_EXCEPT
        return self.__js_resp
