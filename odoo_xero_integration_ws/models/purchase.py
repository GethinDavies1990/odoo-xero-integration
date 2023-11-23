import logging
import requests
from dateutil import tz
from . import constants
from . import contact
from . import product


class Purchase:
    def __init__(self, xr_access_token, xr_tenant, self_env, initial_date=None, end_date=None):
        self.__logging = logging.getLogger(__name__)

        self.__base_endpoint = constants.XR_BASE_URL
        self.__req_version = constants.XR_APP_VERSION
        self.__req_timeout = constants.XR_REQ_TIMEOUT

        self.__default_purchase_api = constants.XR_PURCHASE_AP_LINK
        self.__default_purchase_key = constants.XR_PURCHASE_AP_KEY

        self.__xr_tenant = xr_tenant
        self.__xr_access_token = xr_access_token
        self.__req_headers = {
            "Authorization": "Bearer " + self.__xr_access_token,
            "Accept": "application/json",
            "Xero-tenant-id": self.__xr_tenant.tenant_id
        }

        self.__selfenv = self_env
        self.__initial_date = initial_date
        self.__end_date = end_date

        self.__contact = contact.Contact(
            xr_access_token=self.__xr_access_token,
            xr_tenant=self.__xr_tenant,
            self_env=self.__selfenv
        )
        self.__product = product.Product(
            xr_access_token=self.__xr_access_token,
            xr_tenant=self.__xr_tenant,
            default_env=self.__selfenv
        )

        self.__js_resp = {
            "err_status": True,
            "response": None,
            "total": 0,
            "success": 0,
            "failed": 0
        }

        self.__from_zone = tz.tzutc()
        self.__to_zone = tz.tzlocal()

    def reset_response(self):
        self.__js_resp["err_status"] = True
        self.__js_resp["response"] = None
        self.__js_resp["total"] = 0
        self.__js_resp["success"] = 0
        self.__js_resp["failed"] = 0

    def read_serv_purchases(self):
        try:
            qry_params = {
                "where": "UpdatedDateUTC>= DateTime(" + str(
                    self.__initial_date.strftime('%Y, %m, %d, %H, %M, %S')
                ) + ") && UpdatedDateUTC<= DateTime(" + str(
                    self.__end_date.strftime('%Y, %m, %d, %H, %M, %S')
                ) + ")"
            }
            req_url = self.__base_endpoint + self.__req_version + self.__default_purchase_api
            serv_resp = requests.get(req_url, params=qry_params, headers=self.__req_headers).json()

            if serv_resp[constants.XR_RESPONSE_STATUS_KEY] == constants.XR_RESPONSE_STATUS_VALUE:
                if len(serv_resp[self.__default_purchase_key]) > 0:
                    self.__js_resp["response"] = serv_resp[self.__default_purchase_key]
                    self.__js_resp["err_status"] = False
                else:
                    self.__js_resp["response"] = constants.XR_PURCHASE_IMP_SERV_NOTFND
            else:
                self.__js_resp["response"] = constants.XR_PURCHASE_IMP_SERV_ERR
        except Exception as ex:
            self.__logging.exception("Purchase Serv Read Exception found: " + str(ex))
            self.__js_resp["response"] = constants.XR_PURCHASE_IMP_SERV_EXCEPT

    def get_invoice_product_detail(self, invoice_detail):
        move_line_list = []
        for invoice_pdt in invoice_detail:
            chk_product = self.__selfenv[constants.PRODUCT_TEMPLATE_MODEL].search([
                ('name', '=', invoice_pdt["ItemCode"])
            ])

            if chk_product and len(chk_product) > 0:
                prod_temp_id = chk_product[0].id
            else:
                prod_temp_id = self.__product.create_product(s2l_product_object=invoice_pdt)["response"][0].id

            prod_prod_id = self.__selfenv[constants.PRODUCT_PRODUCT_MODEL].search([
                (constants.PRODUCT_TEMPL_ID, '=', prod_temp_id)
            ])
            sales_data = (0, 0, {
                "price_unit": float(invoice_pdt["UnitAmount"]),
                "quantity": float(invoice_pdt["Quantity"]),
                "product_id": prod_prod_id
            })
            move_line_list.append(sales_data)
        return move_line_list

    def import_purchases(self):
        self.reset_response()
        try:
            self.read_serv_purchases()
            if not self.__js_resp["err_status"]:
                self.__js_resp["total"] = len(self.__js_resp["response"])
                for purchase in self.__js_resp["response"]:
                    email_add = purchase["Contact"]["EmailAddress"] if 'EmailAddress' in purchase["Contact"] else ""
                    contact_rep = self.__selfenv[constants.CONTACT_TASK_MODEL].search([
                        '&', ("email", "=", email_add),
                        ("name", "=", purchase["Contact"]["Name"])
                    ])
                    if contact_rep and len(contact_rep) > 0:
                        pass
                    else:
                        ct_resp = self.__contact.create_contact(purchase["Contact"])
                        if not ct_resp["err_status"]:
                            contact_rep = ct_resp["response"][0]
                    move_line_list = self.get_invoice_product_detail(purchase["LineItems"])
                    self.__selfenv[constants.ACCOUNT_MOVE_MODEL].create({
                        "name": purchase["PurchaseOrderNumber"],
                        'move_type': 'in_invoice',
                        'journal_id': 2,
                        "invoice_date_due": purchase["DeliveryDateString"].split('T')[0],
                        'partner_id': contact_rep.id,
                        'invoice_date': purchase["DateString"].split('T')[0],
                        'currency_id': self.__selfenv.ref('base.GBP').id,
                        'invoice_line_ids': move_line_list
                    })
                    self.__js_resp["success"] += 1

        except Exception as ex:
            self.__logging.exception("Purchase Import Exception: "+str(ex))
            self.__js_resp["response"] = constants.XR_PURCHASE_IMP_EXCEPT
        return self.__js_resp
