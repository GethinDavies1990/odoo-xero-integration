# -*- coding: utf-8 -*-
import logging
from urllib.parse import unquote
from odoo import http
from odoo.http import request
from ..models.connection import Connection
from ..models.tenant import Tenant
from ..models.constants import *
import werkzeug


class TeamsIntegration(http.Controller):
    @http.route('/xero_success', auth='public')
    def index(self, **kw):
        _log = logging.getLogger(__name__)
        def_model = request.env[XERO_CREDENTIALS_MODEL]
        last_conseq_record = def_model.search([])[DEFAULT_INDEX]
        try:
            if 'code=' in str(http.request.httprequest.full_path):
                grant_code = str(http.request.httprequest.full_path).split('code=')[1]
                if '&' in grant_code:
                    grant_code = grant_code.split('&')[0]
                grant_code = unquote(grant_code)

                xero_cloud_params = {
                    'redirect_url': last_conseq_record.redirect_url,
                    'client_id': last_conseq_record.client_id,
                    'client_secret': last_conseq_record.client_secret
                }

                conn = Connection(xero_app_cred=xero_cloud_params)
                _response = conn.generate_access_token(grant_code=grant_code)
                if not _response["err_status"]:
                    last_conseq_record.grant_code = grant_code
                    last_conseq_record.access_token = conn.get_access_token()
                    last_conseq_record.refresh_token = conn.get_refresh_token()
                    def_model.update(last_conseq_record)
                    xr_tenant_resp = Tenant(
                        xr_access_token=conn.get_access_token(), self_env=request.env).save_tenant_info()
                    if not xr_tenant_resp["err_status"]:
                        return werkzeug.utils.redirect('/web')
                    else:
                        return XR_TENANT_STORE_ERR
                else:
                    return "Connection failed: " + str(_response["response"])
            else:
                return GRANT_CODE_ERR
        except Exception as ex:
            return "Internal Exception found: " + str(ex)
