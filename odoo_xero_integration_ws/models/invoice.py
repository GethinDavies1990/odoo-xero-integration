import logging
from . import constants
from . import contact
from . import product
import requests
from datetime import datetime
import re


class Invoice:
    def __init__(self, xr_access_token, xr_tenant, self_env, initial_date=None, end_date=None):

        self.__logging = logging.getLogger(__name__)

        self.__base_endpoint = constants.XR_BASE_URL
        self.__req_version = constants.XR_APP_VERSION
        self.__req_timeout = constants.XR_REQ_TIMEOUT
        
        self.__default_sales_invoice_link = constants.XR_INVOICE_SALES_LINK
        self.__default_sales_invoice_key = constants.XR_INVOICE_SALES_KEY

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

    def reset_response(self):
        self.__js_resp["err_status"] = True
        self.__js_resp["response"] = None
        self.__js_resp["total"] = 0
        self.__js_resp["success"] = 0
        self.__js_resp["failed"] = 0

    def get_invoice_detail_by_id(self, invoice_id):
        resp = {
            "err_status": True,
            "response": None
        }
        try:
            req_url = self.__base_endpoint + self.__req_version + \
                      self.__default_sales_invoice_link + '/' + invoice_id
            invoice_resp = requests.get(req_url, headers=self.__req_headers).json()

            if invoice_resp[constants.XR_RESPONSE_STATUS_KEY] == constants.XR_RESPONSE_STATUS_VALUE:
                if len(invoice_resp[self.__default_sales_invoice_key]) > 0:
                    resp["response"] = invoice_resp
                    resp["err_status"] = False
                else:
                    resp["response"] = constants.XR_INVOICE_IMP_SERV_NOTFND
            else:
                resp["response"] = constants.XR_INVOICE_IMP_SERV_MLD_ERR
        except Exception as ex:
            self.__logging.exception("Invoice detail exception found: " + str(ex))
            resp["response"] = constants.XR_INVOICE_IMP_SERV_MLD_EXCEPT
        return resp

    def read_serv_invoices(self):
        self.reset_response()
        try:
            qry_params = {
                "where": "UpdatedDateUTC>= DateTime(" + str(
                    self.__initial_date.strftime('%Y, %m, %d, %H, %M, %S')
                ) + ") && UpdatedDateUTC<= DateTime(" + str(
                    self.__end_date.strftime('%Y, %m, %d, %H, %M, %S')
                ) + ")"
            }
            req_url = self.__base_endpoint + self.__req_version + self.__default_sales_invoice_link

            serv_resp = requests.get(req_url, params=qry_params, headers=self.__req_headers).json()
            if serv_resp[constants.XR_RESPONSE_STATUS_KEY] == constants.XR_RESPONSE_STATUS_VALUE:
                if len(serv_resp[self.__default_sales_invoice_key]) > 0:
                    self.__js_resp["response"] = serv_resp[self.__default_sales_invoice_key]
                    self.__js_resp["err_status"] = False
                else:
                    self.__js_resp["response"] = constants.XR_INVOICE_IMP_SERV_FILTER_NOTFND
            else:
                self.__js_resp["response"] = constants.XR_INVOICE_IMP_SERV_ERR

        except Exception as ex:
            self.__logging.exception("Serv Mail Import Exception: " + str(ex))
            self.__js_resp["response"] = constants.XR_INVOICE_IMP_EXCEPT

    def get_invoice_product_detail(self, invoice_detail):
        move_line_list = []
        for invoice_pdt in invoice_detail:
            chk_product = self.__selfenv[constants.PRODUCT_TEMPLATE_MODEL].search([
                ('name', '=', invoice_pdt["Item"]["Name"])
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

    def import_invoices(self):
        self.reset_response()
        try:
            self.read_serv_invoices()
            if not self.__js_resp["err_status"]:
                self.__js_resp["total"] = len(self.__js_resp["response"])
                for invoice in self.__js_resp["response"]:
                    try:
                        invoice_serv_dtl = self.get_invoice_detail_by_id(invoice_id=invoice["InvoiceID"])
                        invoice_contact = invoice_serv_dtl['response']['Invoices'][0]["Contact"]
                        invoice_lines = invoice_serv_dtl['response']['Invoices'][0]["LineItems"]

                        if not invoice_serv_dtl["err_status"]:
                            email_add = invoice_contact["EmailAddress"] if 'EmailAddress' in invoice_contact else ""
                            contact_rep = self.__selfenv[constants.CONTACT_TASK_MODEL].search([
                                '&', ("email", "=", email_add),
                                ("name", "=", invoice_contact["Name"])
                            ])
                            if contact_rep and len(contact_rep) > 0:
                                pass
                            else:
                                ct_resp = self.__contact.create_contact(invoice_contact)
                                if not ct_resp["err_status"]:
                                    contact_rep = ct_resp["response"][0]

                            move_line_list = self.get_invoice_product_detail(invoice_lines)
                            self.__selfenv[constants.ACCOUNT_MOVE_MODEL].create({
                                "name": invoice["InvoiceNumber"],
                                'move_type': 'out_invoice',
                                'journal_id': 1,
                                "invoice_date_due": str(datetime.utcfromtimestamp(
                                    int(re.search(r'\d+', invoice["DueDate"]
                                                  ).group()) / constants.MILLISEC_DIV)).split(' ')[0],
                                'partner_id': contact_rep.id,
                                'invoice_date': invoice["DateString"].split('T')[0],
                                'currency_id': self.__selfenv.ref('base.GBP').id,
                                'invoice_line_ids': move_line_list
                            })
                            self.__js_resp["success"] += 1
                        else:
                            self.__js_resp["failed"] += 1
                            self.__js_resp["response"] = constants.XR_INVOICE_IMP_SERV_MLD_ERR
                    except Exception as ex:
                        self.__js_resp["failed"] += 1
                        self.__selfenv.cr.rollback()
                        self.__logging.exception("Inner invoice import exception: " + str(ex))

        except Exception as ex:
            self.__logging.exception("Outer invoice import exception: " + str(ex))
            self.__js_resp["response"] = constants.XR_INVOICE_IMP_EXCEPT
        return self.__js_resp
