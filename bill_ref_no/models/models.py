# -*- coding: utf-8 -*-

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
            if self.ref:
                raise UserError('This Invoice number has already been used in '+(self.name)+'/'+(self.ref).upper()+' Please type unique value')

    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, '%s ' % (rec.name)))
        return res

    @api.constrains('ref', 'type', 'partner_id', 'journal_id', 'invoice_date')
    def _check_duplicate_supplier_reference(self):
        moves = self.filtered(lambda move: move.is_purchase_document() and move.ref)
        if not moves:
            return

        self.env["account.move"].flush([
            "ref", "type", "invoice_date", "journal_id",
            "company_id", "partner_id", "commercial_partner_id",
        ])
        self.env["account.journal"].flush(["company_id"])
        self.env["res.partner"].flush(["commercial_partner_id"])

        # /!\ Computed stored fields are not yet inside the database.
        self._cr.execute('''
                SELECT move2.id
                FROM account_move move
                JOIN account_journal journal ON journal.id = move.journal_id
                JOIN res_partner partner ON partner.id = move.partner_id
                INNER JOIN account_move move2 ON
                    move2.ref = move.ref
                    AND move2.company_id = journal.company_id
                    AND move2.commercial_partner_id = partner.commercial_partner_id
                    AND move2.type = move.type
                    AND (move.invoice_date is NULL OR move2.invoice_date = move.invoice_date)
                    AND move2.id != move.id
                WHERE move.id IN %s
            ''', [tuple(moves.ids)])
        duplicated_moves = self.browse([r[0] for r in self._cr.fetchall()])
        print('aa', duplicated_moves.name)
        if duplicated_moves:
            raise UserError(
                'This Invoice number has already been used in '+(duplicated_moves.name)+'/' + (duplicated_moves.ref).upper() + ' Please type unique value')





