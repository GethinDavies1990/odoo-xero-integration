import requests
import json
import logging
import pytz
from . import constants


class Product:
    def __init__(self, xr_access_token, xr_tenant, default_env, initial_date=None, end_date=None):
        self.__logging = logging.getLogger(__name__)

        self.__base_endpoint = constants.XR_BASE_URL
        self.__req_version = constants.XR_APP_VERSION
        self.__req_timeout = constants.XR_REQ_TIMEOUT

        self.__default_product_api = constants.XR_PRODUCT_AP_LINK
        self.__default_product_key = constants.XR_PRODUCT_AP_KEY

        self.__xr_tenant = xr_tenant
        self.__xr_access_token = xr_access_token
        self.__req_headers = {
            "Authorization": "Bearer " + self.__xr_access_token,
            "Accept": "application/json",
            "Xero-tenant-id": self.__xr_tenant.tenant_id
        }

        self.__initial_date = initial_date
        self.__end_date = end_date
        self.__default_env = default_env

        self.__js_resp = {
            "err_status": True,
            "response": None,
            "total": 0,
            "success": 0,
            "failed": 0
        }
        self._user_tz = default_env.user.tz or pytz.utc
        self._local_tz = pytz.timezone(self._user_tz)

    def reset_response(self):
        self.__js_resp["err_status"] = True
        self.__js_resp["response"] = None
        self.__js_resp["total"] = 0
        self.__js_resp["success"] = 0
        self.__js_resp["failed"] = 0

    def create_product(self, s2l_product_object=None, l2s_product_object=None):
        resp = {
            "err_status": True,
            "response": None
        }
        try:
            if s2l_product_object:
                if 'Item' in s2l_product_object:
                    data = {
                        'name': s2l_product_object["Item"]["Name"],
                        'description': s2l_product_object["Description"],
                        'list_price': s2l_product_object["SalesDetails"]["UnitPrice"],
                        'item_id': s2l_product_object["Item"]["ItemID"],
                        'sale_code': s2l_product_object["SalesDetails"]["AccountCode"],
                        'product_code': s2l_product_object["Item"]["Code"]
                    }
                else:
                    data = {
                        'standard_price': s2l_product_object["UnitAmount"],
                        'name': s2l_product_object["ItemCode"],
                        'description': s2l_product_object["Description"],
                        'product_code': s2l_product_object["ItemCode"]
                    }
                resp["response"] = self.__default_env[constants.PRODUCT_TEMPLATE_MODEL].create(data)
                resp["err_status"] = False
            elif l2s_product_object:
                pdata = {
                    self.__default_product_key: [{
                        "Code": l2s_product_object.product_code,
                        "Name": l2s_product_object.name,
                        "Description": l2s_product_object.description,
                        "PurchaseDetails": {
                            "UnitPrice": l2s_product_object.standard_price
                        },
                        "SalesDetails": {
                            "UnitPrice": l2s_product_object.list_price
                        }
                    }]
                }
                rq_url = self.__base_endpoint + self.__req_version + self.__default_product_api
                serv_resp = requests.post(rq_url, data=json.dumps(pdata), headers=self.__req_headers).json()
                if serv_resp[constants.XR_RESPONSE_STATUS_KEY] == constants.XR_RESPONSE_STATUS_VALUE:
                    resp["err_status"] = False
                else:
                    resp["response"] = constants.XR_PRODUCT_CRT_ERR
            else:
                resp["response"] = constants.XR_PRODUCT_UNK_REQ_ERR
        except Exception as ex:
            self.__logging.exception("Create product exception: " + str(ex))
            resp["response"] = constants.XR_PRODUCT_CRT_ERR_EXCEPT
        return resp

    def read_serv_products(self):
        self.reset_response()
        try:
            filter_params = {}
            if self.__initial_date and self.__end_date:
                filter_params = {
                    "where": "UpdatedDateUTC>= DateTime(" + str(
                        self.__initial_date.strftime('%Y, %m, %d, %H, %M, %S')
                    ) + ") && UpdatedDateUTC<= DateTime(" + str(
                        self.__end_date.strftime('%Y, %m, %d, %H, %M, %S')
                    ) + ")"
                }
            req_url = self.__base_endpoint + self.__req_version + self.__default_product_api

            resp = requests.get(req_url, params=filter_params, headers=self.__req_headers).json()
            if resp[constants.XR_RESPONSE_STATUS_KEY] == constants.XR_RESPONSE_STATUS_VALUE:
                if len(resp[self.__default_product_key]) > 0:
                    self.__js_resp["response"] = resp[self.__default_product_key]
                    self.__js_resp["err_status"] = False
                else:
                    self.__js_resp["response"] = constants.XR_PRODUCT_IMP_SERV_NOTFND
            else:
                self.__js_resp["response"] = constants.XR_PRODUCT_IMP_SERV_REQ_ERR
        except Exception as ex:
            self.__logging.exception("Task Serv Exception found: "+str(ex))
            self.__js_resp["response"] = constants.XR_PRODUCT_IMP_SERV_EXCEPT

    def import_products(self):
        try:
            self.read_serv_products()
            if not self.__js_resp["err_status"]:
                self.__js_resp["total"] = len(self.__js_resp["response"])
                for _product in self.__js_resp["response"]:
                    try:
                        ex_product = self.__default_env[constants.PRODUCT_TEMPLATE_MODEL].search([
                            ('name', '=', _product["Name"])
                        ])
                        if ex_product and len(ex_product) > 0:
                            continue
                        else:
                            data = {
                                'name': _product["Name"],
                                'description': _product["Description"],
                                'standard_price': _product["PurchaseDetails"]["UnitPrice"],
                                'list_price': _product["SalesDetails"]["UnitPrice"],
                                'item_id': _product["ItemID"],
                                'purchase_code': _product["PurchaseDetails"]['AccountCode']
                                if 'AccountCode' in _product["PurchaseDetails"] else "",
                                'sale_code': _product["SalesDetails"]["AccountCode"]
                                if "AccountCode" in _product["SalesDetails"] else "",
                                'product_code': _product["Code"]
                            }
                            self.__default_env[constants.PRODUCT_TEMPLATE_MODEL].create(data)
                            self.__js_resp["success"] += 1
                    except Exception as ex:
                        self.__logging.exception("Import DLY task failed: "+str(ex))
                        self.__js_resp["failed"] += 1
        except Exception as ex:
            self.__logging.exception("Product Import Exception: " + str(ex))
            self.__js_resp["response"] = constants.XR_PRODUCT_IMP_EXCEPT
        return self.__js_resp

    def chk_serv_product(self, product=None, l2s_search=None):
        chk_resp = {
            "err_status": True,
            "response": None
        }
        try:
            if product:
                qry_params = {
                    "where": 'Name="' + product["name"] + '"'
                }
            else:
                qry_params = {
                    "where": 'Name="' + l2s_search.name + '"'
                }
            rq_url = self.__base_endpoint + self.__req_version + self.__default_product_api
            resp = requests.get(rq_url, params=qry_params, headers=self.__req_headers).json()

            if resp[constants.XR_RESPONSE_STATUS_KEY] == constants.XR_RESPONSE_STATUS_VALUE:
                if resp[self.__default_product_key] > 0:
                    chk_resp["err_status"] = False
                    chk_resp["response"] = resp[self.__default_product_key]
        except Exception as ex:
            chk_resp["response"] = "Exception Task Serv: " + str(ex)
        return chk_resp

    def export_serv_tasks(self, products):
        try:
            serv_data = {self.__default_product_key: []}
            for _product in products:
                try:
                    ck_resp = self.chk_serv_product(l2s_search=_product)
                    if ck_resp["err_status"]:
                        pdata = {
                            "Code": str(_product.id) + _product.name,
                            "Name": _product.name,
                            "Description": _product.description,
                            "PurchaseDetails": {
                                "UnitPrice": _product.standard_price
                            },
                            "SalesDetails": {
                                "UnitPrice": _product.list_price
                            }
                        }
                        serv_data[self.__default_product_key].append(pdata)
                except Exception as ex:
                    self.__logging.exception("Export product record exception:" + str(ex))
                    self.__js_resp["response"] = constants.XR_PRODUCT_EXP_REC_EXCEPT

            if len(serv_data[self.__default_product_key]) > 0:
                req_url = self.__base_endpoint + self.__req_version + self.__default_product_api
                resp = requests.post(req_url, data=json.dumps(serv_data), headers=self.__req_headers).json()
                if resp[constants.XR_RESPONSE_STATUS_KEY] == constants.XR_RESPONSE_STATUS_VALUE:
                    self.__js_resp["success"] += len(serv_data[self.__default_product_key])
                else:
                    self.__js_resp["response"] = constants.XR_PRODUCT_EXP_RECS_ERR
                    self.__js_resp["failed"] += len(serv_data[self.__default_product_key])
            else:
                self.__js_resp["response"] = constants.XR_PRODUCT_EXP_SERV_ERR

        except Exception as ex:
            self.__logging.exception("Exception Export found: " + str(ex))
            self.__js_resp["response"] = constants.XR_PRODUCT_EXP_SERV_EXCEPT

    def export_products(self):
        self.reset_response()
        try:
            query_params, products = [], []

            if self.__initial_date or self.__end_date:
                query_params.append('&')
            if self.__initial_date:
                query_params.append(('create_date', '>=', str(self.__initial_date).replace('T', ' ')))
            if self.__end_date:
                query_params.append(('create_date', '<=', str(self.__end_date).replace('T', ' ')))

            _db_data = self.__default_env[constants.PRODUCT_TEMPLATE_MODEL].search(query_params)
            if _db_data and len(_db_data) > 0:
                self.export_serv_tasks(_db_data)
                self.__js_resp["total"] = len(products)
                self.__js_resp["err_status"] = False
            else:
                self.__js_resp["response"] = constants.XR_PRODUCT_EXP_REC_NTFD
        except Exception as ex:
            self.__logging.exception("Task Export Exception: " + str(ex))
            self.__js_resp["response"] = constants.XR_PRODUCT_EXP_EXCEPT
        return self.__js_resp
