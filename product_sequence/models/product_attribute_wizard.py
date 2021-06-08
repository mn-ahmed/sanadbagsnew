
from odoo import models, fields, api


class ProductAttributeWizard(models.TransientModel):
    _name = 'product.attribute.wizard'

    value_ids = fields.Many2many('product.attribute.value')
    attribute_id = fields.Many2one('product.attribute')

    def action_create_attribute(self):
        model = self.env.context.get('active_model')
        rec_model = self.env[model].browse(self.env.context.get('active_id'))
        for rec in rec_model.attribute_line_ids:
            if rec.attribute_id == self.attribute_id:
                att_list = []
                for attr in rec.value_ids:
                    att_list.append(attr.id)
                for x in self.value_ids:
                    att_list.append(x.id)
                rec.update({
                    'value_ids': att_list,
                })
    # @api.onchange('sale_id')
    # def onchange_sale_id(self):
    #     for res in self:
    #         val_list = []
    #         my_list = []
    #         for rec in res.product_lines:
    #             my_list.append(rec.sale_order)
    #
    #         for order in res.sale_id:
    #             if order.name not in my_list:
    #                 for line in order._origin.order_line:
    #                     val = {
    #                         'sale_id': res.id,
    #                         'sale_order': order.name,
    #                         'sr_no': line.number,
    #                         'qty': line.product_uom_qty,
    #                         'product_id': line.product_id.id,
    #                         'price': line.price_unit,
    #                     }
    #                     val_list.append(val)
    #         move = self.env['sale.order.wizard.line'].create(val_list)

