# -*- coding: utf-8 -*-
import re

from odoo import models, fields, api, _
from odoo.osv import expression


class ProductTemplateInh(models.Model):
    _inherit = 'product.template'

    product_temp_seq = fields.Char('Product Code', required=True, copy=False, index=True, readonly=True, default=lambda self: _('New'))

    @api.model
    def create(self, vals):
        if vals.get('product_temp_seq', _('New')) == _('New'):
            vals['product_temp_seq'] = self.env['ir.sequence'].next_by_code('product.template.sequence') or _('New')
        result = super(ProductTemplateInh, self).create(vals)
        result.assign_sequence_in_variant()
        return result

    def write(self, vals):
        res = super(ProductTemplateInh, self).write(vals)
        for rec in self:
            rec.assign_sequence_in_variant()
        return res

    def assign_sequence_in_variant(self):
        count = 0
        for variant in self.product_variant_ids:
            count += 1
            variant.product_seq = str(00) + str(00) + str(0) + str(count)
            variant.item_code = self.product_temp_seq + variant.product_seq
        return


class ProductProductInh(models.Model):
    _inherit = 'product.product'

    product_seq = fields.Char('Product Code', required=True, copy=False, readonly=True,
                                index=True, default=lambda self: _('New'))
    product_counter = fields.Integer()
    item_code = fields.Char('Item Code')

    def compute_item_code(self):
        for rec in self:
            rec.item_code = str(rec.product_counter) #rec.product_tmpl_id.product_temp_seq +

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if not args:
            args = []
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            product_ids = []
            if operator in positive_operators:
                product_ids = list(
                    self._search(['|', ('default_code', '=', name), ('item_code', 'ilike', name)] + args, limit=limit,
                                 access_rights_uid=name_get_uid))
                if not product_ids:
                    product_ids = list(
                        self._search(['|', ('barcode', '=', name), ('item_code', 'ilike', name)] + args, limit=limit,
                                     access_rights_uid=name_get_uid))
            if not product_ids and operator not in expression.NEGATIVE_TERM_OPERATORS:
                # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
                # on a database with thousands of matching products, due to the huge merge+unique needed for the
                # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give much better performance
                product_ids = list(self._search(args + [('default_code', operator, name)], limit=limit))
                if not limit or len(product_ids) < limit:
                    # we may underrun the limit because of dupes in the results, that's fine
                    limit2 = (limit - len(product_ids)) if limit else False
                    product2_ids = self._search(args + [('name', operator, name), ('id', 'not in', product_ids)],
                                                limit=limit2, access_rights_uid=name_get_uid)
                    product_ids.extend(product2_ids)
            elif not product_ids and operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = expression.OR([
                    ['&', ('default_code', operator, name), ('name', operator, name)],
                    ['&', ('default_code', '=', False), ('name', operator, name)],
                ])
                domain = expression.AND([args, domain])
                product_ids = list(self._search(domain, limit=limit, access_rights_uid=name_get_uid))
            if not product_ids and operator in positive_operators:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    product_ids = list(self._search([('default_code', '=', res.group(2))] + args, limit=limit,
                                                    access_rights_uid=name_get_uid))
            # still no results, partner in context: search on supplier info as last hope to find something
            if not product_ids and self._context.get('partner_id'):
                suppliers_ids = self.env['product.supplierinfo']._search([
                    ('name', '=', self._context.get('partner_id')),
                    '|',
                    ('product_code', operator, name),
                    ('product_name', operator, name)], access_rights_uid=name_get_uid)
                if suppliers_ids:
                    product_ids = self._search([('product_tmpl_id.seller_ids', 'in', suppliers_ids)], limit=limit,
                                               access_rights_uid=name_get_uid)
        else:
            product_ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return product_ids