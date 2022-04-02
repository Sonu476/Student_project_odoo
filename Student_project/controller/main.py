
from odoo import http

from odoo.addons.website_sale.controllers.main import WebsiteSale
import json

from functools import partial

from odoo.tools import formatLang
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.sale.controllers.portal import CustomerPortal


class Sale(http.Controller):
    @http.route('/my_sale_details', type='http', auth='public', website=True)
    def sale_details(self , **kwargs):
        sale_details = request.env['sale.order'].sudo().search([])
        return request.render('Student_project.sale_details_page', {'my_details': sale_details})

    @http.route('/edit_mode', type='http', auth='public', website=True)
    def edit(self, **kwargs):

        # portal_link = "%s/?db=%s" % (request.env['ir.config_parameter'].sudo().get_param('web.base.url'), request.env.cr)
        #
        # portal_link = "%s" %(request.env..url.fetchall())
        # # portal_link = "%s" % (request.env['ir.config_parameter'].sudo().get_param("url"))
        # print(portal_link)

        # dom=request.env['website'].get_current_website().website_domain()
        # print(dom)

        order = request.env['sale.order'].sudo().browse(int(kwargs['order_id']))
        if order.order_line.exists():
            print("changed")
            order.state='sent'

        return request.redirect(order.get_portal_url())

    @http.route('/save_change', type='http', auth='public', website=True)
    def save_change(self, **kwargs):
        order = request.env['sale.order'].sudo().browse(int(kwargs['order_id']))
        if order.order_line.exists():
            print("saved changed")
            order.state = 'sale'
        return request.redirect(order.get_portal_url())




class CustomerPortal(CustomerPortal):
    @http.route(['/my/orders/<int:order_id>/update_line_dict'], type='json', auth="public", website=True)
    def update_line_dict(self, line_id, remove=False, unlink=False, order_id=None, access_token=None,
                         input_quantity=False, **kwargs):
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if order_sudo.state not in ('draft', 'sent', 'sale'):
            return False
        order_line = request.env['sale.order.line'].sudo().browse(int(line_id))
        if order_line.order_id != order_sudo:
            return False
        if unlink:
            order_line.unlink()
            return False  # return False to reload the page, the line must move back to options and the JS doesn't handle it

        if input_quantity is not False:
            quantity = input_quantity
        else:
            number = -1 if remove else 1
            quantity = order_line.product_uom_qty + number

        if quantity < 0:
            quantity = 0.0
        order_line.write({'product_uom_qty': quantity})
        currency = order_sudo.currency_id
        format_price = partial(formatLang, request.env, digits=currency.decimal_places)

        results = {
            'order_line_product_uom_qty': str(quantity),
            'order_line_price_total': format_price(order_line.price_total),
            'order_line_price_subtotal': format_price(order_line.price_subtotal),
            'order_amount_total': format_price(order_sudo.amount_total),
            'order_amount_untaxed': format_price(order_sudo.amount_untaxed),
            'order_amount_tax': format_price(order_sudo.amount_tax),
            'order_amount_undiscounted': format_price(order_sudo.amount_undiscounted),
        }
        try:
            results['order_totals_table'] = request.env['ir.ui.view'].render_template(
                'sale.sale_order_portal_content_totals_table', {'sale_order': order_sudo})
        except ValueError:
            pass

        return results




class WebsiteShopInherit(WebsiteSale):
    # sale_order_portal_content

    @http.route('/shop/cart/update/', website=True, auth='public')
    def cart_update(self, product_id=None, add_qty=1, set_qty=0, **kw):
        product_ids = request.env['product.product'].sudo().search([])
        tmp = request.env['product.public.category'].sudo().search([])
        category_id = product_id
        print('********', category_id, "######", type(category_id))
        products=[]
        searched_product = []

        for r in tmp:
            print("*********", r.name)

        print("inside controller")
        sale_order = request.website.sale_get_order(force_create=True)

        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)

        product_custom_attribute_values = None
        if kw.get('product_custom_attribute_values'):
            product_custom_attribute_values = json.loads(kw.get('product_custom_attribute_values'))

        no_variant_attribute_values = None
        if kw.get('no_variant_attribute_values'):
            no_variant_attribute_values = json.loads(kw.get('no_variant_attribute_values'))

        for ids in product_ids:
            if ids.public_categ_ids.parent_id.id == int(category_id) or ids.public_categ_ids.id == int(category_id):
                print("inside for loop")
                print('****************', ids)
                product_id = ids

                if ids.name not in products:

                    sale_order._cart_update(
                        product_id=int(product_id),
                        add_qty=add_qty,
                        set_qty=set_qty,
                        product_custom_attribute_values=product_custom_attribute_values,
                        no_variant_attribute_values=no_variant_attribute_values
                    )

                    searched_product.append(ids.name)
                products.append(ids.name)
            print(searched_product)
            print(products)


        print(products)
        if kw.get('express'):
            return request.redirect("/shop/checkout?express=1")

        return request.redirect("/shop/cart/")
