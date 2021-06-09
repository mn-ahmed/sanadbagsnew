# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
# from odoo.tools.misc import datetime
from datetime import datetime


class PurchaseOrderInh(models.Model):
    _inherit = 'purchase.order'

    payment_count = fields.Integer(compute='compute_payments')
    advance_payment = fields.Integer("Advance Payment", compute='compute_payments')

    @api.depends("partner_id")
    def compute_payments(self):
        obj = self.env['account.payment'].search_count([('po_number', '=', self.name)])
        if obj:
            self.payment_count = obj
        else:
            self.payment_count = 0
        count = self.env['account.payment'].search([('po_number', '=', self.name)],limit=1)
        self.advance_payment = count.amount

    def action_register_payment(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Apply Advance Payments',
            'view_id': self.env.ref('purchase_order_payment.view_advance_payment_wizard_form', False).id,
            'context': {'default_ref': self.name, 'default_order_amount': self.amount_total, 'default_user_id': self.user_id.id},
            'target': 'new',
            'res_model': 'advance.payment.wizard',
            'view_mode': 'form',
        }

    def action_show_payments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Advance Payments',
            'view_id': self.env.ref('account.view_account_payment_tree', False).id,
            'target': 'current',
            'domain': [('ref', '=', self.name)],
            'res_model': 'account.payment',
            'views': [[False, 'tree'], [False, 'form']],
        }

    def action_confirm(self):
        flag = 0
        for rec in self:
            payments = self.env['account.payment'].search([('partner_id', '=', rec.partner_id.id), ('communication', '=', rec.name)])
            partner = self.env['res.partner'].search([('id', '=', rec.partner_id.id)], limit=1)
            print(partner.total_due)
            received_payment = 0
            for payment in payments:
                received_payment = received_payment + payment.amount
            if received_payment >= (rec.amount_total/2) or (partner.total_due*-1) >= (rec.amount_total/2):
                res = super(PurchaseOrderInh, self).action_confirm()
                flag = 1

        if flag == 0:
            raise UserError('There is no enough Advance Payment available to Confirm this Purchase Order.')

class AccountMoveInh(models.Model):
    _inherit = 'account.move'

    advance_payment = fields.Float('Advance Payment', compute='compute_advance_payment')

    def compute_advance_payment(self):
        for rec in self:
            sale = self.env['sale.order'].search([('name', '=', rec.invoice_origin)])
            rec.advance_payment = sale.advance_payment


class AccountPaymentInh(models.Model):
    _inherit = 'account.payment'

    user_id = fields.Many2one('res.users')
    wiz_description = fields.Text('Description')
    cheque_no = fields.Char(string ='Cheque no')
    paid_by = fields.Char(string='Paid by')
    received_by = fields.Char(string='Received By')
    approved_by = fields.Char(string='Paid by')
    po_number = fields.Char(string='PO Number')
    memo = fields.Char(string='Memo')

    def get_amount_in_words(self,amount):
        amount_in_words = self.currency_id.amount_to_text(amount)
        amount_in_words = amount_in_words +" "+ "Only"
        return amount_in_words
