
from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError

class VendorBill(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        purchase_order = self.env['purchase.order'].search([('id', '=', vals['purchase_id'])])
        if purchase_order:
            total_qty = 0
            total_invoice_qty = 0
            purchase_invoices = self.env['account.move'].search([('purchase_id', '=', purchase_order.id),('state', '=', 'posted')])
            if purchase_invoices:
                for rec in purchase_invoices.invoice_line_ids:
                    total_invoice_qty = total_invoice_qty + rec.quantity
            for line in purchase_order.order_line:
                total_qty = total_qty + line.qty_received
            if total_invoice_qty != total_qty:
                raise UserError(_('Billed Quantity Should Not Be Changed'))
        res= super(VendorBill,self).create(vals)
        return res


    # @api.model
    # def create(self, vals):
    #     for line in vals['invoice_line_ids']:
    #         rec = self.env['purchase.order.line'].browse(line[2].get('purchase_line_id'))
    #         if line[2].get('quantity') != rec.qty_received:
    #             raise UserError(_('Billed Quantity Should Not Be Changed'))
    #     res= super(VendorBill,self).create(vals)
    #     return res

    # @api.model
    # def create(self, vals):
    #     res= super(VendorBill,self).create(vals)
    #     for line in res.invoice_line_ids:
    #         if line.quantity != line.purchase_line_id.product_qty:
    #             raise UserError(_('Billed Quantity Should Not Be Changed'))
    #     return res

    # def action_post(self):
    #     if self.purchase_id:
    #         purchase_order = self.env['purchase.order'].search([('id', '=', self.purchase_id.id)])
    #         if purchase_order:
    #             if self.type == 'in_invoice':
    #                 total_qty = 0
    #                 total_invoice_qty = 0
    #                 # commnets
    #                 purchase_invoices = self.env['account.move'].search([('purchase_id', '=', purchase_order.id),
    #                                                                      ('state', '=', 'posted')])
    #                 if purchase_invoices:
    #                     for rec in purchase_invoices.invoice_line_ids:
    #                         total_invoice_qty = total_invoice_qty + rec.quantity
    #                 # comments ends
    #                 for line in purchase_order.order_line:
    #                     total_qty = total_qty + line.qty_received
    #                 for invoice_line in self.invoice_line_ids:
    #                     total_invoice_qty = total_invoice_qty + invoice_line.quantity
    #                 if total_invoice_qty == total_qty:
    #                     record = super(VendorBill, self).action_post()
    #                 else:
    #                     raise UserError('Billed Quantity Should Be Equal To Purchase Order Quantity')



class VendorBillInh(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('quantity')
    def onchange_done_qty(self):
        reciept = self.env['stock.picking'].search([('purchase_id', '=', self.purchase_line_id.order_id.id), ('state', '=', 'done')])
        for do_line in reciept.move_ids_without_package:
            print(do_line.quantity_done)
            if self.product_id.id == do_line.product_id.id:
                if not self.quantity == do_line.quantity_done:
                    raise UserError('Quantity Should be Equal to Reserved')


    # @api.onchange('quantity')
    # def check_qty(self):
    #     if self.move_id.purchase_id:
    #         purchase_order = self.env['purchase.order'].search([('id', '=', self.move_id.purchase_id.id)])
    #         if purchase_order:
    #             if self.move_id.type == 'in_invoice':
    #                 total_qty = 0
    #                 total_invoice_qty = 0
    #                 purchase_invoices = self.env['account.move'].search([('purchase_id', '=', purchase_order.id),
    #                                                                      ('state', '=', 'posted')])
    #                 if purchase_invoices:
    #                     for rec in self.move_id.invoice_line_ids:
    #                         total_invoice_qty = total_invoice_qty + rec.quantity
    #                 for line in purchase_order.order_line:
    #                     total_qty = total_qty + line.qty_received
    #                 for invoice_line in self.move_id.invoice_line_ids:
    #                     total_invoice_qty = total_invoice_qty + invoice_line.quantity
    #                 if total_invoice_qty == total_qty:
    #                     pass
    #                 else:
    #                     raise UserError('Billed Quantity Should Not Be Changed')
