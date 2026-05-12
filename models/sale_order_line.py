from odoo import fields, models, api, _
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    special_item = fields.Boolean(
        related="product_id.product_tmpl_id.special_item",
        store=True,
        readonly=True
    )

    bom_id = fields.Many2one(
        'mrp.bom',
        string="BOM"
    )
    special_clicked = fields.Boolean(string="Special Clicked", default=False)

    bom_count = fields.Integer(related='product_id.bom_count')

    def action_special_item(self):
        for line in self:
            line.special_clicked = True

    def action_bom(self):
        self.ensure_one()

        bom = self.env['mrp.bom'].search([
            '|',
            ('product_id', '=', self.product_id.id),
            ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),
            ('master_bom', '=', True)
        ], limit=1)

        if not bom:
            raise UserError("No Master BOM found.")

        new_bom = bom.copy({
            'master_bom': False,
            'code': bom.code,
        })

        new_lines = []

        def explode_bom(product, qty, visited=None):
            if visited is None:
                visited = set()

            if product.id in visited:
                return []

            visited.add(product.id)

            bom_map = self.env['mrp.bom']._bom_find(product)
            child_bom = bom_map.get(product)

            if not child_bom or not child_bom.master_bom:

                return [{
                    'product_id': product.id,
                    'product_qty': qty,
                    'product_uom_id': product.uom_id.id,
                }]

            result = []

            for line in child_bom.bom_line_ids:
                sub_qty = qty * line.product_qty

                result += explode_bom(line.product_id, sub_qty, visited)

            return result


        for line in bom.bom_line_ids:
            if line.product_id.bom_count != 0:
                exploded = explode_bom(line.product_id, line.product_qty)
                for vals in exploded:
                    new_lines.append((0, 0, vals))

        new_bom.write({
            'bom_line_ids': new_lines
        })

        self.bom_id = new_bom.id

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.bom',
            'view_mode': 'form',
            'res_id': new_bom.id,
            'target': 'new',
        }
















    # def _prepare_mo_vals(self):
    #     vals = super()._prepare_mo_vals()
    #
    #     latest_bom = self.env['mrp.bom'].search([
    #         ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id)
    #     ], order='id desc', limit=1)
    #
    #     if latest_bom:
    #         vals['bom_id'] = latest_bom.id
    #
    #     return vals