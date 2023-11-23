# -*- coding: utf-8 -*-
# Import packages & Support files
from odoo import models, fields, api
from . import connection
from . import constants
from . import contact
from . import invoice
from . import purchase
from . import product
from datetime import *
import logging

#############################################################################
#                     Defined Xero Credentials Model
#############################################################################


class XeroCredentials(models.Model):
    # Defined model name & constraints

    _name = constants.XERO_CREDENTIALS_MODEL
    '''
    ## apply constrainst for db models
    _sql_constraints = [
        ('client_id', 'unique (client_id)', 'The client ID must be unique  !')
    ]
    '''

    # Defined Required and Optional fields for xero

    redirect_url = fields.Char(string="Redirect URL", required=True, default=lambda self: self._get_default_url())
    client_id = fields.Char(string="Client ID", required=True, default=lambda self: self._get_default_client_id())
    client_secret = fields.Char(string="Client Secret", required=True,
                                default=lambda self: self._get_default_secret_id())
    access_token = fields.Char(string="Access Token", default=None)
    refresh_token = fields.Char(string="Refresh Token", default=None)
    grant_code = fields.Char(string="Grant Code", default=None)

    #################################################################################
    # This method revoke on button click event and perform following actions     ####
    # a. Add Credentials to database models                                      ####
    # b. Generate Authorization link                                             ####
    # c. Perform user consent of required scopes values                          ####
    # d. Popup of authorization link for user consent                            ####
    #################################################################################

    def connect(self):
        _logging = logging.getLogger(__name__)
        rep_mesxero = ''
        val_struct = {
            'redirect_url': self.redirect_url,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }

        try:
            if constants.XERO_CREDENTIALS_RDT_URI in self.redirect_url:
                # Create db cursor and query to check existence of record
                db_cursor = self.env[self._name]
                db_rows = db_cursor.search([])
                if db_rows and len(db_rows) > 0:
                    ex_record = db_cursor.search([('client_id', '=', val_struct["client_id"])])
                    if ex_record and len(ex_record) == 0:
                        _logging.info("Update CRD record")
                        db_rows[constants.DEFAULT_INDEX].client_id = val_struct["client_id"]
                        db_rows[constants.DEFAULT_INDEX].client_secret = val_struct["client_secret"]
                        db_rows[constants.DEFAULT_INDEX].redirect_url = val_struct["redirect_url"]
                        db_cursor.update(db_rows[constants.DEFAULT_INDEX])
                else:
                    _logging.info("Create CRD record")
                    super().create(val_struct)

                # Create and generate authorization link using Connection object
                conn = connection.Connection(xero_app_cred=val_struct)
                _response = conn.get_auth_url()
                if not _response["err_status"]:
                    return {
                        'type': 'ir.actions.act_url',
                        'name': "grant_code",
                        'target': 'self',
                        'url': _response["response"],
                    }
                else:
                    rep_mesxero += constants.AUTH_URL_CREATION_FAILED
            else:
                rep_mesxero += constants.XERO_CREDENTIALS_RDT_URI_ERR
        except Exception as ex:
            _logging.exception("Exception CRD: " + str(ex))
            rep_mesxero += constants.AUTH_URL_CREATION_EXCEPT
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': constants.FAILURE_POP_UP_TITLE,
                'mesxero': rep_mesxero,
                'sticky': False,
            }
        }

    @api.model
    def _get_default_url(self):
        latest_record = self.env[constants.XERO_CREDENTIALS_MODEL].search([])
        return latest_record[constants.DEFAULT_INDEX].redirect_url if len(latest_record) > 0 else ''

    @api.model
    def _get_default_client_id(self):
        latest_record = self.env[constants.XERO_CREDENTIALS_MODEL].search([])
        return latest_record[constants.DEFAULT_INDEX].client_id if len(latest_record) > 0 else ''

    @api.model
    def _get_default_secret_id(self):
        latest_record = self.env[constants.XERO_CREDENTIALS_MODEL].search([])
        return latest_record[constants.DEFAULT_INDEX].client_secret if len(latest_record) > 0 else ''


#############################################################################
# Defined Office Sync Model
#############################################################################


class XeroSync(models.Model):
    _name = constants.XERO_CONNECTOR_MODEL

    xr_tenant = fields.Many2one(constants.XERO_TENANTS_MODEL, string="Xero-Tenant",
                                required=True, ondelete='cascade', index=True, copy=False)

    import_invoice = fields.Boolean(default=False)
    import_purchase_order = fields.Boolean(default=False)

    import_product = fields.Boolean(default=False)
    export_product = fields.Boolean(default=False)

    import_contact = fields.Boolean(default=False)
    export_contact = fields.Boolean(default=False)

    # office.connection
    import_data_stats = fields.One2many(constants.XERO_IMPORT_STATS_MODEL, inverse_name="connector")
    export_data_stats = fields.One2many(constants.XERO_EXPORT_STATS_MODEL, inverse_name="connector")

    custom_from_datetime = fields.Datetime('From Date', required=False, readonly=False, select=True,
                                           default=lambda self: (fields.datetime.now() - timedelta(hours=1))
                                           )
    custom_to_datetime = fields.Datetime('To Date', required=False, readonly=False, select=True,
                                         default=lambda self: (fields.datetime.now() + timedelta(hours=1))
                                         )

    def get_xero_credetials(self):
        cred_response = {}
        try:
            db_cursor = self.env[constants.XERO_CREDENTIALS_MODEL]
            db_rows = db_cursor.search([])
            if db_rows and len(db_rows) > 0:
                cred_response["client_id"] = db_rows[constants.DEFAULT_INDEX].client_id
                cred_response["client_secret"] = db_rows[constants.DEFAULT_INDEX].client_secret
                cred_response["redirect_url"] = db_rows[constants.DEFAULT_INDEX].redirect_url
            else:
                cred_response["err_message"] = constants.XR_CONN_CRED_NOTFND
                cred_response["error"] = "Credentials are not found"
        except Exception as ex:
            cred_response["error"] = str(ex)
            cred_response["err_message"] = constants.XR_CONN_CRED_ACS_EXCEPT
        return cred_response

    #################################################################################
    # This method revoke on button click event and perform following actions     ####
    # a. Import & Export Contents                                             #######
    # b. Support Content eg. Contacts, Calender, Emails, Tasks                #######
    # c. Collect data and store into defined models structure                 #######
    # d. Popup of notification status of action                               #######
    #################################################################################

    def synchronize(self):
        _logging = logging.getLogger(__name__)
        default_env = self.env

        pop_up_message, date_error_chk = "", False
        import_chk_status, export_chk_status = False, False
        imp_contact, imp_purchase_order, imp_product, imp_invoice = 0, 0, 0, 0
        exp_contact, exp_product = 0, 0

        try:
            if self.custom_from_datetime > self.custom_to_datetime:
                date_error_chk = True
            before_date = self.custom_from_datetime
            after_date = self.custom_to_datetime

            if not date_error_chk:
                credentials = self.get_xero_credetials()
                if 'error' not in credentials and 'err_message' not in credentials:
                    connect = connection.Connection(xero_app_cred=credentials,
                                                    default_env=default_env,
                                                    xr_tenent=self.xr_tenant)
                    conn_response = connect.get_msv_access_token()

                    if not conn_response["err_status"]:
                        if self.import_contact or self.export_contact:
                            _contacts = contact.Contact(
                                xr_access_token=conn_response["response"],
                                xr_tenant=self.xr_tenant, self_env=default_env,
                                initial_date=before_date, end_date=after_date
                            )
                            if self.import_contact:
                                contact_response = _contacts.import_contacts()
                                if not contact_response["err_status"]:
                                    imp_contact += contact_response["success"]
                            if self.export_contact:
                                contact_response = _contacts.export_contacts()
                                if not contact_response["err_status"]:
                                    exp_contact += contact_response["success"]

                        if self.import_purchase_order:
                            _purchase = purchase.Purchase(
                                xr_access_token=conn_response["response"],
                                xr_tenant=self.xr_tenant, self_env=self.env,
                                initial_date=before_date, end_date=after_date
                            )

                            purchase_response = _purchase.import_purchases()
                            if not purchase_response["err_status"]:
                                imp_purchase_order += purchase_response["success"]

                        if self.import_product or self.export_product:
                            _product = product.Product(
                                xr_access_token=conn_response["response"],
                                xr_tenant=self.xr_tenant,
                                default_env=self.env,
                                initial_date=before_date,
                                end_date=after_date
                            )

                            if self.import_product:
                                product_resposne = _product.import_products()
                                if not product_resposne["err_status"]:
                                    imp_product += product_resposne["success"]
                            if self.export_product:
                                product_resposne = _product.export_products()
                                if not product_resposne["err_status"]:
                                    exp_product += product_resposne["success"]

                        if self.import_invoice:
                            _invoice = invoice.Invoice(
                                xr_access_token=conn_response["response"],
                                xr_tenant=self.xr_tenant,
                                self_env=self.env,
                                initial_date=before_date,
                                end_date=after_date
                            )

                            invoice_response = _invoice.import_invoices()
                            if not invoice_response["err_status"]:
                                imp_invoice += invoice_response["success"]

                        if self.import_contact or self.import_purchase_order or\
                                self.import_invoice or self.import_product:
                            if imp_invoice or imp_product or imp_contact or imp_purchase_order:
                                self.env[constants.XERO_IMPORT_STATS_MODEL].create({
                                    'invoice': imp_invoice, 'product': imp_product,
                                    'purchase_order': imp_purchase_order, 'contact': imp_contact,
                                    'connector': self.id})
                            if pop_up_message == "":
                                pop_up_message += constants.SYNC_PROCESS_MXR
                            import_chk_status = True

                        if self.export_contact or self.export_product:
                            if exp_product or exp_contact:
                                self.env[constants.XERO_EXPORT_STATS_MODEL].create({
                                    'product': exp_product, 'contact': exp_contact, 'connector': self.id})
                            if pop_up_message == "":
                                pop_up_message += constants.SYNC_PROCESS_MXR
                            export_chk_status = True

                        if not export_chk_status and not import_chk_status:
                            pop_up_message = constants.NO_OPT_SECTION_ERR
                    else:
                        pop_up_message += conn_response["response"]
                else:
                    pop_up_message += credentials["err_mesxero"]
                    _logging.info("Error while Sync: " + credentials["error"])
            else:
                pop_up_message += constants.INVALID_DATE_RANGES
        except Exception as ex:
            _logging.exception("Sync Exception: " + str(ex))
            pop_up_message += constants.SYNC_REQ_ERROR
        return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': "System Notification",
                    'mesxero': pop_up_message,
                    'sticky': False,
                }
            }

    def import_history_action(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': constants.XERO_IMPORT_STATS_MODEL,
            'view_mode': 'tree',
            'context': {'no_breadcrumbs': True}
        }

    def export_history_action(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': constants.XERO_EXPORT_STATS_MODEL,
            'view_mode': 'tree',
            'context': {'no_breadcrumbs': True}
        }


class ImportDataStats(models.Model):
    _name = constants.XERO_IMPORT_STATS_MODEL

    connector = fields.Many2one(constants.XERO_CONNECTOR_MODEL)
    invoice = fields.Integer()
    product = fields.Integer()
    purchase_order = fields.Integer()
    contact = fields.Integer()


class ExportDataStats(models.Model):
    _name = constants.XERO_EXPORT_STATS_MODEL

    connector = fields.Many2one(constants.XERO_CONNECTOR_MODEL)
    product = fields.Integer()
    contact = fields.Integer()


class XeroTenants(models.Model):
    _name = constants.XERO_TENANTS_MODEL

    uid = fields.Char('uid')
    name = fields.Char('Name')
    tenant_id = fields.Char('Tenant-ID')
    tenant_type = fields.Char('Type')


class XeroResPartner(models.Model):
    _inherit = constants.CONTACT_TASK_MODEL

    xero_user_type = fields.Selection([('CUSTOMER', 'CUSTOMER'), ('VENDOR', 'VENDOR')], 'User Type',
                                      default='CUSTOMER')
    source = fields.Char(String="Source", readonly=True, default="internal")
    xero_contact_id = fields.Char(String="XR ContactID", readonly=True, default="internal")


class XeroProductTemplate(models.Model):
    _inherit = constants.PRODUCT_TEMPLATE_MODEL

    item_id = fields.Char(String="Item-Id", readonly=True, default="internal")
    product_code = fields.Char(String="Product-Code", readonly=True, default="internal")
    purchase_code = fields.Char(String="Purchase-Code", readonly=True, default=constants.XR_PRODUCT_PURCHASE_CODE)
    sale_code = fields.Char(String="Sale-Code", readonly=True, default=constants.XR_PRODUCT_SALE_CODE)
