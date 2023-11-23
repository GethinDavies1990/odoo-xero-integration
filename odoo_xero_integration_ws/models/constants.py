########################################################################################
# ###############################     Xero Basic      ##################################
########################################################################################

XR_AUTH_URL = 'https://login.xero.com/identity/connect/authorize'
XR_AUTH_EXCODE_URL = 'https://identity.xero.com/connect/token'
XR_TENANT_URL = 'https://api.xero.com/connections'
XR_SCOPES = [
    'offline_access', 'openid', 'profile', 'email',
    'accounting.transactions', 'accounting.contacts', 'accounting.settings'
]

XR_BASE_URL = 'https://api.xero.com/api.xro/'
XR_APP_VERSION = '2.0'
XR_REQ_TIMEOUT = 5

CONTACT_USER_TYPE = 'Xero'
CONTACT_TASK_MODEL = 'res.partner'
PRODUCT_TEMPLATE_MODEL = 'product.template'
PRODUCT_PRODUCT_MODEL = 'product.product'
PRODUCT_TEMPL_ID = 'product_tmpl_id'
ACCOUNT_MOVE_MODEL = 'account.move'
ACCOUNT_MOVE_LINES_MODEL = 'account.move.line'


XERO_CREDENTIALS_MODEL = 'xero.credentials'
XERO_TENANTS_MODEL = 'xero.tenants'
XERO_CONNECTOR_MODEL = 'xero.connector'
XERO_IMPORT_STATS_MODEL = 'xero.import.stats'
XERO_EXPORT_STATS_MODEL = 'xero.export.stats'
XERO_CREDENTIALS_RDT_URI = 'xero_success'
XERO_CREDENTIALS_RDT_URI_ERR = 'Oops, Given redirect url is not supported, Please try again'

XR_RESPONSE_STATUS_KEY = 'Status'
XR_RESPONSE_STATUS_VALUE = 'OK'
RESPONSE_ERR_KEY = 'error'
RESPONSE_ERR_CODE = 401
RESPONSE_ERR_TITLE = 'Title'
RESPONSE_ERR_TL_VALUES = ['Unauthorized', 'Forbidden']
RESPONSE_ERR_DETAILS = 'Detail'
RESPONSE_ERR_MESSAGE = 'Message'

COUNT_RECORD_KEY = '$total'
LIST_RECORD_KEY = '$items'
PERVIOUS_PAGE_KEY = '$back'
NEXT_PAGE_KEY = '$next'

DEFAULT_INDEX = -1
TOKEN_EXPIRE_STATUS = 'AccessTokenExpiredError'

ACCESS_TOKEN_ATTEMPT = 3
TOKEN_ERROR_CODE = '80049228'
TOKEN_ERR_STATUS_CODE = 401
DEFAULT_ATTACHMENT_PATH = '\\office_attachments\\'

#################################################################################################
# #################################     Contacts Section      ###################################
#################################################################################################

XR_CONTACT_AP_LINK = '/Contacts'
XR_CONTACT_AP_KEY = 'Contacts'
XR_CONTACT_SOURCE = 'XERO'

XR_CONTACTS_IMP_EXCEPT = 'Oops, Import Contacts failed, Please try again.'
XR_CONTACTS_IMP_SERV_EXCEPT = 'Oops, Import Contacts from Server failed, Please try again.'
XR_CONTACTS_EXP_EXCEPT = 'Oops, Export Contacts failed, Please try again.'
XR_CONTACTS_EXP_SERV_ERR = 'Oops, unable to export contact. Please try again.'
XR_CONTACTS_EXP_SERV_EXCEPT = 'Oops, Export Contacts to Server failed, Please try again.'
XR_CONTACTS_EXP_NOTFND = "Oops, Contacts are not found according to date ranges"
XR_CONTACTS_SERV_NOTFND = "Oops, Contacts are not found from server. Please try again."


#################################################################################################
# #################################     Products Section      ######################################
#################################################################################################

XR_PRODUCT_AP_LINK = '/Items'
XR_PRODUCT_AP_KEY = 'Items'
XR_PRODUCT_PURCHASE_CODE = '437'
XR_PRODUCT_SALE_CODE = '200'
XR_PRODUCT_SALES_LEDGER_LINK = '/ledger_accounts?visible_in=sales'
XR_PRODUCT_PURCHASES_LEDGER_LINK = '/ledger_accounts?visible_in=expenses'

XR_PRODUCT_CRT_ERR = 'Oops, unable to create product. Please try again.'
XR_PRODUCT_CRT_ERR_EXCEPT = 'Oops, product creation failed, Please try again.'
XR_PRODUCT_IMP_EXCEPT = 'Oops, Import Products failed, Please try again.'
XR_PRODUCT_IMP_SERV_PRD_DTL_ERR = 'Oops, unable to find product details, Please try again.'
XR_PRODUCT_IMP_SERV_FILTER_NOTFND = 'Oops, No record found while apply filter, Please try again.'
XR_PRODUCT_IMP_SERV_EXCEPT = 'Oops, Import Products from Server failed, Please try again.'
XR_PRODUCT_IMP_SERV_REQ_ERR = 'Oops, Import Products from Server Request failed, Please try again.'
XR_PRODUCT_IMP_SERV_NOTFND = 'Oops, products not found, Please try again.'


XR_PRODUCT_EXP_SERV_EXCEPT = 'Oops, Export Server Products Exception, Please try again.'
XR_PRODUCT_EXP_SERV_ERR = 'Oops, Export Server Products Exception, Please try again.'
XR_PRODUCT_EXP_RECS_ERR = 'Oops, unable to export product records, Please try again.'
XR_PRODUCT_EXP_REC_EXCEPT = 'Oops, Export product record except, Please try again.'

XR_PRODUCT_EXP_REC_NTFD = 'Oops, Product Records are not found, Please try again.'
XR_PRODUCT_EXP_EXCEPT = 'Oops, Export Products failed, Please try again.'
XR_PRODUCT_UNK_REQ_ERR = 'Oops, Unknown product request found, Please try again.'

#################################################################################################
# #################################     Invoices Section      ######################################
#################################################################################################

XR_INVOICE_SALES_LINK = '/Invoices'
XR_INVOICE_SALES_KEY = 'Invoices'
XR_INVOICE_MESXERO_DATETIME_FORMAT_GMT = '%a, %d %b %Y %H:%M:%S GMT'
XR_INVOICE_MESXERO_DATETIME_FORMAT = '%a, %d %b %Y %H:%M:%S'

XR_INVOICE_IMP_ROLLBACK_ERR = "Oops, unable to complete import invoices from server, Please try again"
XR_INVOICE_IMP_SERV_PG_EXCEPT = "Oops, invoices page fetching failure from server, Please try again"
XR_INVOICE_IMP_SERV_PG_ERR = "Oops, invoices page failed from server, Please try again"
XR_INVOICE_IMP_SERV_MLD_EXCEPT = "Oops, invoice details fetching failure, Please try again"
XR_INVOICE_IMP_SERV_MLD_ERR = "Oops, invoice details failed, Please try again"
XR_INVOICE_IMP_SERV_NOTFND = "Oops, invoices are not found, Please try again"
XR_INVOICE_IMP_SERV_FILTER_NOTFND = "Oops, invoices are not found while apply filter, Please try again"

XR_INVOICE_IMP_SERV_ERR = 'Oops, Import Invoices failed, Please try again.'
XR_INVOICE_IMP_SERV_EXCEPT = 'Oops, Unable to fetch mails from server, Please try again.'
XR_INVOICE_IMP_SERV_FLD_ERR = 'Oops, Unable to fetch folder information from server, Please try again.'
XR_INVOICE_IMP_EXCEPT = 'Oops, unable to fetch invoices records from server, Please try again.'

XR_INVOICE_EXP_ROLLBACK_ERR = "Oops, unable to complete import invoices from server, Please try again"

XR_INVOICE_EXP_SERV_CHK_EXCEPT = "Oops, server invoice searcing proccess failed. Please try again"
XR_INVOICE_EXP_SERV_CHK_ERR = "Oops, unable to fetch invoice records. Please try again"
XR_INVOICE_EXP_SERV_CHK_NOTFND = "Oops, sale invoice records are not found. Please try again"

XR_INVOICE_EXP_SERV_PG_EXCEPT = "Oops, invoices page fetching failure from server, Please try again"
XR_INVOICE_EXP_SERV_PG_ERR = "Oops, invoices page failed from server, Please try again"
XR_INVOICE_EXP_SERV_MLD_EXCEPT = "Oops, invoice details fetching failure, Please try again"
XR_INVOICE_EXP_SERV_MLD_ERR = "Oops, invoice details failed, Please try again"
XR_INVOICE_EXP_SERV_NOTFND = "Oops, invoices are not found, Please try again"
XR_INVOICE_EXP_FILTER_NOTFND = "Oops, invoices are not found while apply filter, Please try again"

XR_INVOICE_EXP_SERV_ERR = 'Oops, unable to export invoice. Please try again.'
XR_INVOICE_EXP_SERV_EXCEPT = 'Oops, export invoices failed. Please try again.'
XR_INVOICE_EXP_SERV_RCD_EXCEPT = 'Oops, export invoice record failed. Please try again.'
XR_INVOICE_EXP_SERV_FLD_ERR = 'Oops, Unable to fetch folder information from server, Please try again.'
XR_INVOICE_EXP_EXCEPT = 'Oops, unable to fetch invoices records from database, Please try again.'

#################################################################################################
# ###############################     Calendar Section      #####################################
#################################################################################################

XR_PURCHASE_AP_LINK = '/PurchaseOrders'
XR_PURCHASE_AP_KEY = 'PurchaseOrders'

XR_PURCHASE_EXP_SERV_EXCEPT = 'Oops, Export purchase records to server failed, Please try again.'
XR_PURCHASE_EXP_EXCEPT = 'Oops, Export purchase records failed, Please try again.'
XR_PURCHASE_EXP_NT_RCD = 'Oops, Export purchase records are not found, Please try again.'
XR_PURCHASE_EXP_NT_DFN = 'Oops, Export purchase records build not proceed, Please try again.'

XR_PURCHASE_EXP_CHK_NTFND = 'Oops, purchases are not found, Please try again.'

XR_PURCHASE_IMP_SERV_EXCEPT = 'Oops, Import Purchases from Server failed, Please try again.'
XR_PURCHASE_IMP_SERV_NOTFND = 'Oops, No purchases are found from Server Purchases, Please try again.'
XR_PURCHASE_IMP_SERV_ERR = 'Oops, unable to fetch purchases from server. Please try again.'
XR_PURCHASE_IMP_EXCEPT = 'Oops, Import Purchases failed, Please try again.'
XR_PURCHASE_IMP_REC_EXCEPT = 'Oops, Import Purchase Record failed, Please try again.'

XR_PURCHASE_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
XR_PURCHASE_PARTNER_REL_ID = 4

#################################################################################################
# ################################     Profile Section      #####################################
#################################################################################################

XR_USER_LINK = '/Users'
XR_USER_RESPONSE_KEY = 'Users'
XR_USER_SERV_FETCH_EXCEPT = 'Oops, unable to fetch profile information, Please try again.'

XR_TENANT_SERV_FETCH_EXCEPT = 'Oops, unable to fetch tenant(s) information, Please try again.'
XR_TENANT_STORE_ERR = 'Oops, unable to store tenant(s) information, Please try again.'

#################################################################################################
# ##############################      Connection Section      ###################################
#################################################################################################

XR_CONN_URL_FAILED = "Oops, unable to generate authorization link."
XR_CONN_URL_EXCEPT = "Oops, unable to generate authorize link, Please try again."
XR_CONN_CRED_NOTFND = "Oops, unable to find credentials. Please try again."
XR_CONN_CRED_ACS_FAILED = "Oops, unable to generate access credentials, Please try again."
XR_CONN_CRED_ACS_EXCEPT = "Oops, unable to request for access credentials, Please try again."
XR_CONN_RAT_FAILED = "Oops, unable to refresh authorization information."
XR_CONN_RAT_EXCEPT = "Oops, unable to request for refresh authorize info, Please try again."


# System Mesxeros
FAILURE_POP_UP_TITLE = 'System Alert'
AUTH_URL_CREATION_FAILED = 'Oops, system unable to create authorize link'
AUTH_URL_CREATION_EXCEPT = 'Oops, system found exception while creating authorize link'

SYNC_REQ_ERROR = 'Oops, unable to process given request, Please try again'
ACCESS_TOKEN_ERR_REFRESH = 'Oops, unable to refresh authorization information, Please try again'
ACCESS_TOKEN_EXCEPT = 'Oops, unable to get credentials information, Please try again'
ACCESS_TOKEN_CRED_NTFND = 'Oops, credentials information not found, Please save credentials before uxero'
ACCESS_TOKEN_NOTFOUND = 'Oops, authorization information not found, Please authorize account before uxero'
ACCESS_TOKEN_INVALID = 'Oops, authorization information is invalid, Please authorize account again'
GRANT_CODE_ERR = 'Unable to get authorization code information, Please try again.'

NO_OPT_SECTION_ERR = 'Oops, no operation is not being selected, Please some operation to proceed.'
SYNC_PROCESS_MXR = "Synchronization process completed"
# DateTime Format
DEFAULT_DATETIME = '2020-01-01 07:00:00'
DEFAULT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_TZ_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
INVALID_DATE_RANGES = "Invalid date ranges found, Please correct date ranges."
MILLISEC_DIV = 1000
