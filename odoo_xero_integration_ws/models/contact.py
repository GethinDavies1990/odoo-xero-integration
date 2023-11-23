from . import constants
import requests
import json
import logging
import re
from datetime import *


class Contact:
    def __init__(self, xr_access_token, xr_tenant, self_env, initial_date=None, end_date=None):
        self.__logging = logging.getLogger(__name__)

        self.__base_endpoint = constants.XR_BASE_URL
        self.__req_version = constants.XR_APP_VERSION
        self.__req_timeout = constants.XR_REQ_TIMEOUT

        self.__contact_default_api = constants.XR_CONTACT_AP_LINK
        self.__contact_default_key = constants.XR_CONTACT_AP_KEY

        self.__xr_tenant = xr_tenant
        self.__selfenv = self_env
        self.__xr_access_token = xr_access_token
        self.__req_headers = {
            "Authorization": "Bearer " + self.__xr_access_token,
            "Accept": "application/json",
            "Xero-tenant-id": self.__xr_tenant.tenant_id
        }

        self.__initial_date = initial_date
        self.__end_date = end_date
        self.__js_resp = {
            "err_status": True,
            "response": None,
            "total": 0,
            "success": 0,
            "failed": 0
        }

    def reset_response(self):
        self.__js_resp["err_status"] = True
        self.__js_resp["response"] = None
        self.__js_resp["total"] = 0
        self.__js_resp["success"] = 0
        self.__js_resp["failed"] = 0

    def read_serv_contacts(self):
        try:
            req_url = self.__base_endpoint + self.__req_version + self.__contact_default_api
            resp = requests.get(req_url, headers=self.__req_headers).json()
            if resp[constants.XR_RESPONSE_STATUS_KEY] == constants.XR_RESPONSE_STATUS_VALUE:
                if len(resp[self.__contact_default_key]) > 0:
                    tmp_contact_lists = []
                    
                    for contact in resp[self.__contact_default_key]:
                        up_datetime = int(re.search(r'\d+', contact["UpdatedDateUTC"]).group()) / constants.MILLISEC_DIV
                        rcd_datetime = datetime.utcfromtimestamp(up_datetime)

                        if rcd_datetime >= self.__initial_date and rcd_datetime <= self.__end_date:
                            tmp_contact_lists.append(contact)

                    if len(tmp_contact_lists) > 0:
                        self.__js_resp["response"] = tmp_contact_lists
                        self.__js_resp["err_status"] = False
                    else:
                        self.__js_resp["response"] = constants.XR_CONTACTS_EXP_NOTFND
                else:
                    self.__js_resp["response"] = constants.XR_CONTACTS_SERV_NOTFND
            else:
                self.__js_resp["response"] = resp[constants.RESPONSE_ERR_DETAILS]

        except Exception as ex:
            self.__logging.exception("Server Import Contacts Exception: "+str(ex))
            self.__js_resp["response"] = constants.XR_CONTACTS_IMP_SERV_EXCEPT

    def import_contacts(self):
        self.reset_response()
        try:
            self.read_serv_contacts()
            if not self.__js_resp["err_status"]:

                self.__js_resp["total"] = len(self.__js_resp["response"])
                for contact in self.__js_resp["response"]:
                    try:
                        chk_exist = self.__selfenv[constants.CONTACT_TASK_MODEL].search(
                            ['&', ('email', '=', contact["EmailAddress"]), ('name', '=', contact["Name"])])
                        if chk_exist and len(chk_exist) > 0:
                            pass
                        else:
                            self.__selfenv[constants.CONTACT_TASK_MODEL].create({
                                'name': contact["Name"],
                                'email': contact["EmailAddress"],

                                'phone': contact["Phones"][0]["PhoneCountryCode"] +
                                         contact["Phones"][0]["PhoneAreaCode"] + contact["Phones"][0]["PhoneNumber"],

                                'mobile': contact["Phones"][3]["PhoneCountryCode"] +
                                          contact["Phones"][3]["PhoneAreaCode"] + contact["Phones"][3]["PhoneNumber"],

                                'street': contact["Addresses"][0]["AttentionTo"] if len(
                                    contact["Addresses"]) > 0 else "",

                                'city': contact["Addresses"][0]["City"] if len(contact["Addresses"]) > 0 else "",
                                'zip': contact["Addresses"][0]["PostalCode"] if len(contact["Addresses"]) > 0 else "",
                                'source': constants.XR_CONTACT_SOURCE,
                                'xero_contact_id': contact["ContactID"]
                            })
                            self.__js_resp["success"] += 1
                    except Exception as ex:
                        self.__logging.info(">> Import SXR Contact Exception: " + str(ex))
                        self.__js_resp["failed"] += 1
        except Exception as ex:
            self.__logging.exception("Import Contacts Exception: " + str(ex))
            self.__js_resp["response"] = constants.XR_CONTACTS_IMP_EXCEPT
        return self.__js_resp

    def create_contact(self, contact_serv_object):
        crt_resp = {
            "err_status": True,
            "response": None
        }
        try:
            address = contact_serv_object["Addresses"]
            mobile_num = ''
            for each in contact_serv_object["Phones"]:
                if each['PhoneType'] == 'MOBILE':
                    mobile_num = each['PhoneCountryCode'] + each['PhoneAreaCode'] + each['PhoneNumber']
            contact_dtls = {
                'name': contact_serv_object["Name"],
                'email': contact_serv_object['EmailAddress'] if 'EmailAddress' in contact_serv_object else "",
                'mobile': mobile_num,
                'street': address[0]['AddressLine1'] if len(address[0]) > 0 else "",
                'street2': address[0]['AddressLine2'] if len(address[0]) > 0 else "",
                'city': address[0]['City'] if len(address) > 1 else "",
                'zip': address[0]['PostalCode'] if len(address) > 2 else "",
                'source': constants.XR_CONTACT_SOURCE
            }
            crt_resp["response"] = self.__selfenv[constants.CONTACT_TASK_MODEL].create(contact_dtls)
            crt_resp["err_status"] = False
        except Exception as ex:
            crt_resp["response"] = "Check server failure: " + str(ex)
        return crt_resp

    def create_serv_contact(self, contact_object, supplier=False):
        crt_resp = {
            "err_status": True,
            "response": None
        }
        try:
            xr_json_params = {
                "contact": {
                    "name": contact_object["name"],
                    "contact_type_ids": [
                        "CUSTOMER" if not supplier else "VENDOR"
                    ],
                    "main_address": {
                        "address_line_1": contact_object["address"] if "address" in contact_object and
                                                                       contact_object["address"] else "",
                        "city": contact_object["city"] if contact_object["city"] else "",
                        "postal_code": contact_object["zip"] if "zip" in contact_object
                                                                and contact_object["zip"] else "",
                        "name": contact_object["name"]
                    },
                    "delivery_address": {
                            "address_line_1": contact_object["address"] if "address" in contact_object and
                                                                           contact_object["address"] else "",
                            "city": contact_object["city"] if contact_object["city"] else "",
                            "postal_code": contact_object["zip"] if "zip" in contact_object
                                                                    and contact_object["zip"] else "",
                            "name": contact_object["name"]
                    },
                    "main_contact_person": {
                        "contact_person_type_ids": [
                            "CUSTOMER" if not supplier else "VENDOR"
                        ],
                        "name": contact_object["name"],
                        "telephone": contact_object["phone"] if "phone" in contact_object and
                                                                contact_object["phone"] else "",
                        "mobile": contact_object["mobile"] if "mobile" in contact_object and
                                                              contact_object["mobile"] else "",
                        "email": contact_object["email"] if contact_object["email"] else ""
                    },
                }
            }

            if supplier:
                del xr_json_params['contact']['delivery_address']

            req_url = self.__base_endpoint + self.__req_version + self.__contact_default_api
            resp = requests.post(req_url, data=json.dumps(xr_json_params),
                                 headers=self.__req_headers).json()

            if type(resp) == dict or constants.RESPONSE_ERR_KEY not in resp[0]:
                crt_resp["err_status"] = False
                crt_resp["response"] = resp
            else:
                crt_resp["response"] = constants.XR_CONTACTS_EXP_SERV_EXCEPT
        except Exception as ex:
            crt_resp["response"] = "Check server failure: " + str(ex)
        return crt_resp

    def get_serv_contact(self, contact_id):
        chk_resp = {
            "err_status": True,
            "response": None
        }
        try:
            req_url = self.__base_endpoint + self.__req_version +\
                      self.__contact_default_api + '/' + contact_id
            resp = requests.get(req_url, headers=self.__req_headers).json()

            if type(resp) == dict or constants.RESPONSE_ERR_KEY not in resp[0]:
                chk_resp["response"] = resp
                chk_resp["err_status"] = False
            else:
                chk_resp["response"] = resp["error"]["mesxero"]
        except Exception as ex:
            chk_resp["response"] = "Check server failure: " + str(ex)
        return chk_resp

    def check_serv_contact(self, sr_contact, supplier=False):
        chk_resp = {
            "err_status": True,
            "response": None
        }
        try:
            req_url = self.__base_endpoint + self.__req_version +\
                      self.__contact_default_api + '/?where=EmailAddress="' + sr_contact["email"] + '"'

            if supplier:
                req_url += '&contact_type=VENDOR'
            resp = requests.get(req_url, headers=self.__req_headers).json()

            if resp[constants.XR_RESPONSE_STATUS_KEY] == constants.XR_RESPONSE_STATUS_VALUE:
                if len(resp[self.__contact_default_key]) > 0:
                    chk_resp["err_status"] = False
                    chk_resp["response"] = resp[self.__contact_default_key]
            else:
                chk_resp["response"] = resp[constants.RESPONSE_ERR_DETAILS]
        except Exception as ex:
            chk_resp["response"] = "Check server failure: " + str(ex)
        return chk_resp

    def write_serv_contacts(self, _data):
        self.reset_response()
        try:
            req_url = self.__base_endpoint + self.__req_version + self.__contact_default_api

            for cont in _data:
                chk_serv_status = self.check_serv_contact(cont)
                if chk_serv_status["err_status"]:
                    try:
                        cname = cont["name"].split(' ')
                        xr_json_params = {
                            "ContactStatus": "ACTIVE",
                            "Name": cont["name"],
                            "FirstName": cname[0],
                            "LastName": cname[1] if len(cname) > 1 else "",
                            "EmailAddress": cont["email"],
                            "Addresses": [{
                                "AddressType": "STREET",
                                "City": cont["city"],
                                "PostalCode": cont["zip"],
                                "AttentionTo": cont["address"]
                            }],
                            "Phones": [
                                {
                                    "PhoneType": "DEFAULT",
                                    "PhoneNumber": cont["phone"]
                                },
                                {
                                    "PhoneType": "MOBILE",
                                    "PhoneNumber": cont["mobile"]
                                },
                            ]
                        }
                        resp = requests.post(
                            req_url, data=json.dumps(xr_json_params), headers=self.__req_headers).json()

                        if constants.XR_RESPONSE_STATUS_KEY in resp and \
                                resp[constants.XR_RESPONSE_STATUS_KEY] == \
                                constants.XR_RESPONSE_STATUS_VALUE:
                            self.__js_resp["success"] += 1
                        else:
                            self.__logging.info("Internal Error Export Contact: " +
                                                resp[constants.RESPONSE_ERR_MESSAGE])
                            self.__js_resp["failed"] += 1

                    except Exception as ex:
                        self.__js_resp["failed"] += 1
                        self.__logging.exception("Exception Server Export Contact Internal: " + str(ex))
                        self.__js_resp["response"] = constants.XR_CONTACTS_EXP_EXCEPT
        except Exception as ex:
            self.__logging.exception("Exception Server Export Contact: "+str(ex))
            self.__js_resp["response"] = constants.XR_CONTACTS_EXP_SERV_EXCEPT

    def export_contacts(self):
        self.reset_response()
        try:
            query_params = []
            if self.__initial_date and self.__end_date:
                query_params.append('&')

            if self.__initial_date:
                query_params.append(('write_date', '>=', str(self.__initial_date)))

            if self.__end_date:
                query_params.append(('write_date', '<=', str(self.__end_date)))

            _db_contacts = self.__selfenv[constants.CONTACT_TASK_MODEL].search(query_params)
            json_contacts = []

            if _db_contacts and len(_db_contacts) > 0:
                for cont in _db_contacts:
                    tmp = {
                        "name": cont.name,
                        "company": cont.commercial_company_name,
                        "email": cont.email,
                        "phone": cont.phone,
                        "mobile": cont.mobile,
                        "address": cont.street,
                        "city": cont.city,
                        "zip": cont.zip,
                        # "website": cont.website,
                        # 'user_type': cont.xero_user_type
                    }
                    json_contacts.append(tmp)

                if len(json_contacts) > 0:
                    self.write_serv_contacts(_data=json_contacts)
                    self.__js_resp["err_status"] = False
                else:
                    self.__js_resp["response"] = constants.XR_CONTACTS_EXP_NOTFND
            else:
                self.__js_resp["response"] = constants.XR_CONTACTS_EXP_NOTFND
        except Exception as ex:
            self.__logging.exception("Export Contacts Exception: " + str(ex))
            self.__js_resp["response"] = constants.XR_CONTACTS_EXP_EXCEPT
        return self.__js_resp
