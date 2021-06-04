# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class QualityPoint(models.Model):

    _inherit = 'quality.point'
    product_tmpl = fields.Many2one(
        'product.template', 'Product', check_company=True,
        domain="[('type', 'in', ['consu', 'product']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")


class AttachmentFieldsInPurchaseOrderss(models.Model):
    _inherit = 'stock.picking'

    check = fields.Boolean('Check', compute="_compute_check_button_confirm")
    check_doc = fields.Boolean('Check Doc', compute='onchange_check_document_confirm')

#     @api.onchange('picking_type_id')
    def onchange_check_document_confirm(self):
        for rec in self:
            print('hhh', rec.picking_type_id.code)
            if rec.picking_type_id.code == 'incoming':
                rec.check_doc = True
            else:
                rec.check_doc = False

    def confirm_my_button(self):
        res = super(AttachmentFieldsInPurchaseOrderss, self).check_quality()
        for i in self:
            i.state = 'qc_inspection'
            for line in i.move_ids_without_package:
                line.state = 'assigned'
        return res

    def _compute_check_button_confirm(self):
        flag = 0
        for rec in self:
            quality = self.env['quality.check'].search([('picking_id', '=', rec.id)])
            for each in quality:
                if each.quality_state != 'pass':
                    flag = 1
            if flag == 0:
                rec.check = True
            else:
                rec.check = False



    def check_quality(self):
        res = super(AttachmentFieldsInPurchaseOrderss, self).check_quality()
        for i in self:
            i.state = 'qc_inspection'
            for line in i.move_ids_without_package:
                line.state = 'qc_inspection'
        return res

# 
#     def write(self, vals):
# #         if self.state == 'assigned':
# #             if 'state' not in vals:
# #                 vals['state'] = 'qc_inspection'
#         res = super(AttachmentFieldsInPurchaseOrderss, self).write(vals)
#       
#         print(self.state)
#         #     self.state = 'qc_inspection'
#         return res

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('qc_inspection', 'QC Inspection'),
        ('assigned', 'Ready'),

        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, tracking=True,
        help=" * Draft: The transfer is not confirmed yet. Reservation doesn't apply.\n"
             " * Waiting another operation: This transfer is waiting for another operation before being ready.\n"
             " * Waiting: The transfer is waiting for the availability of some products.\n(a) The shipping policy is \"As soon as possible\": no product could be reserved.\n(b) The shipping policy is \"When all products are ready\": not all the products could be reserved.\n"
             " * Ready: The transfer is ready to be processed.\n(a) The shipping policy is \"As soon as possible\": at least one product has been reserved.\n(b) The shipping policy is \"When all products are ready\": all product have been reserved.\n"
             " * Done: The transfer has been processed.\n"
             " * Cancelled: The transfer has been cancelled.")

    purchase_doc = fields.Boolean('Purchase Doc')
    fabric_lab_certificate = fields.Boolean('Fabric Lab Certificate')
    wire_mill_certificate = fields.Boolean('Wire Mill Certificate')

    def confirm_button(self):
        for rec in self:
            # if rec.state == 'confirmed':
            if rec.purchase_doc == True and rec.fabric_lab_certificate == True and rec.wire_mill_certificate == True:
                rec.state = 'qc_inspection'
                for line in rec.move_line_ids_without_package:
                    line.state = 'qc_inspection'
            else:
                raise UserError('All Documents needs to be checked')
            # else:
            #     rec.state = 'confirmed'


class AttachmentFieldsInPurchaseOrders(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        res = super(AttachmentFieldsInPurchaseOrders, self).button_confirm()
        for order in self:
            for picking in order.picking_ids:
                picking.state = 'confirmed'
                for res in picking.move_line_ids:
                    res.state = 'qc_inspection'
        return res


class AttachmentFieldsInPurchaseOrderInventory(models.Model):
    _inherit = 'stock.move'

    line_check = fields.Boolean("Check", related='picking_id.check_doc')

    accepted = fields.Float("Accepted")
    rejected = fields.Float("Rejected")
    
    state = fields.Selection([
        ('draft', 'New'), ('cancel', 'Cancelled'),
        ('waiting', 'Waiting Another Move'),
        ('confirmed', 'Waiting Availability'),
        ('partially_available', 'Partially Available'),
        ('qc_inspection', 'QC Inspection'),
        ('assigned', 'Available'),
        ('done', 'Done')], string='Status',
        copy=False, default='draft', index=True, readonly=True,
        help="* New: When the stock move is created and not yet confirmed.\n"
             "* Waiting Another Move: This state can be seen when a move is waiting for another one, for example in a chained flow.\n"
             "* Waiting Availability: This state is reached when the procurement resolution is not straight forward. It may need the scheduler to run, a component to be manufactured...\n"
             "* Available: When products are reserved, it is set to \'Available\'.\n"
             "* Done: When the shipment is processed, the state is \'Done\'.")

    @api.onchange('rejected')
    def accepted_qty(self):
        for rec in self:
            rec.accepted = rec.product_uom_qty - rec.rejected
            if rec.accepted > rec.product_uom_qty:
                raise UserError('You are adding more quantity than the initial demand')

    @api.onchange('accepted')
    def rejected_qty(self):
        for rec in self:
            rec.rejected = rec.product_uom_qty - rec.accepted
            if rec.rejected > rec.product_uom_qty:
                raise UserError('You are adding more quantity than the initial demand')

    # def _action_assign(self):
    #     for i in self:
    #         i.write({'state': 'confirmed'})
    #         res = super(AttachmentFieldsInPurchaseOrder, self)._action_assign()
    #         return res

    def _action_assign(self):
        res = super(AttachmentFieldsInPurchaseOrderInventory, self)._action_assign()
        if self.env.context.get('active_model',False) == 'purchase.order':
            if self.env.context.get('active_id',False):
                po = self.env['purchase.order'].search([('id', '=', self.env.context.get('active_id'))])
                if po.picking_ids:
                    if po.picking_ids[0].state == 'qc_inspection':
                        if po.picking_ids[0].move_ids_without_package:
                            for ol in po.picking_ids[0].move_ids_without_package:
                                ol.state = 'qc_inspection'
        print('asdf', self.picking_id.state)
        print(res)
        return res
