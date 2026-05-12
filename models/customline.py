from odoo import models, fields
from odoo.exceptions import UserError

class CustomLine(models.Model):
    _name = 'custom.line'
    _description = 'Custom Line'

    order_id = fields.Many2one('sale.order', string="Order Reference")
    sale_order = fields.Many2one('sale.order')
    select_line = fields.Boolean(string="Select")
    subtotal = fields.Float(string="Amount")
    product_id = fields.Many2one(
        'product.product',
        ondelete='set null',
    )

    price = fields.Float(string="Unit Price")
    quantities = fields.Float(string="Quantity")

    def action_reorder_line(self):
        self.ensure_one()

        if not self.product_id:
            raise UserError("Please select a product.")

        sale_order = self.order_id

        self.env['sale.order.line'].create({
            'order_id': sale_order.id,
            'product_id': self.product_id.id,
            'name': self.product_id.name,
            'product_uom_qty': self.quantities or 1,
            'product_uom_id': self.product_id.uom_id.id,
            'price_unit': self.price,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': sale_order.id,
        }