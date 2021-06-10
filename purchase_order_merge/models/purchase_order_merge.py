# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class POInherit(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('merge', 'Merged'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    

    # def action_merge_rfq(self):
    #     selected_ids = self.env.context.get('active_ids', [])
    #     selected_records = self.env['purchase.order'].browse(selected_ids)
    #     total_list = []
    #     for record in selected_records:
    #         for line in record.order_line:
    #             line_data = (0, 0, {
    #                 'product_id': line.product_id.id,
    #                 'name': line.product_id.name,
    #                 'product_qty': line.product_qty,
    #                 'price_unit': line.price_unit,
    #                 'price_subtotal': line.price_subtotal,
    #                 'product_uom': line.product_uom.id,
    #                 'date_planned': line.date_planned
    #             })
    #             total_list.append(line_data)
    #
    #     return {
    #         'name': 'Generated Documents',
    #         'res_model': 'purchase.order',
    #         'views': [[False, "form"]],
    #         'type': 'ir.actions.act_window',
    #         'context': {'default_order_line': total_list}
    #     }



class MaterialRequisitionInherit(models.Model):
    _inherit = 'material.purchase.requisition'


    def action_merge_requisition(self):
        selected_ids = self.env.context.get('active_ids', [])
        selected_records = self.env['material.purchase.requisition'].browse(selected_ids)
        total_list = []
        names = []
        for record in selected_records:
            if not record.state in ['stock','po_pick']:
                raise UserError(('States Must Be: "Purchase Order Created" or "PO/IP Created"'))
            else:
                names.append(record.name)
                for line in record.requisition_line_ids:
                    if line.requisition_type == 'purchase':
                        line_data = (0, 0, {
                            # 'requisition_type': line.requisition_type,
                            'product_id': line.product_id.id,
                            'name': line.product_id.name,
                            'product_qty': line.qty,
                            'product_uom': line.uom.id,
                            'price_unit': line.product_id.lst_price,
                            'date_planned': fields.Date.today()
                        })
                        total_list.append(line_data)
                recs = self.env['purchase.order'].search([('custom_requisition_id', '=', record.id)])
                for rec in recs:
                    rec.state = 'merge'
        my_string = ','.join(names)
        return {
            'name': 'Generated Documents',
            'res_model': 'purchase.order',
            'views': [[False, "form"]],
            'type': 'ir.actions.act_window',
            'context': {'default_order_line': total_list, 'default_origin': my_string}
        }
