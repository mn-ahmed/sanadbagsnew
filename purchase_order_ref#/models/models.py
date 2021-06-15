# -*- coding: utf-8 -*-
import dateutil.utils
from odoo.tools.misc import formatLang, format_date, get_lang
from odoo import models, fields, api,_
from odoo.exceptions import UserError


class PurchaseOrderRefNo(models.Model):
    _inherit = 'purchase.order'


class PurchaseOrderRefNoo(models.Model):
    _inherit = 'account.move'
    _rec_name = 'name'

    @api.constrains('ref')
    def unique_ref_no(self):
        partner_rec = self.env['account.move'].search([('partner_id', '=', self.partner_id.id), ('ref', '=', self.ref)])
        if len(partner_rec) > 1:
            raise UserError(_('This Invoice number has already been used in ' + (self.ref).upper()+' Please type unique value'))

    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, '%s ' % (rec.name)))
        return res



















