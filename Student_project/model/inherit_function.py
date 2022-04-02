from odoo import models, fields, api, _
from odoo.addons.website_sale_stock.models.sale_order import SaleOrder as WebsiteSaleStock
from odoo.http import request

from datetime import datetime, timedelta
from odoo.exceptions import MissingError
from lxml import etree
# from odoo.osv.orm import setup_modifiers
import decimal,re
from odoo.exceptions import except_orm, Warning, RedirectWarning, UserError
import logging
_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = 'website'

    @api.model
    def get_sale_product(self):
        orders = self.env['sale.order'].sudo().search([])
        # product = orders.id
        order = self.env['sale.order'].sudo().search([('id', '=', 1)])

        # company_names = []
        #
        # for rec in company_name:
        #     company_names.append(rec.name)

        # companies = self.env['res.partner'].sudo().search([('name', 'in', company_names)])
        products = order.order_line.product_id
        return products

    def refresh_page(self):

        print("calling button")
        return {'type': 'ir.actions.client', 'tag': 'reload'}
