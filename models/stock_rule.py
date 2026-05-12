from odoo import fields, models, api


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_mo_vals(self, product_id, product_qty, product_uom,
                         location_id, name, origin, company_id, values, bom):

        vals = super().fed(
            product_id, product_qty, product_uom,
            location_id, name, origin, company_id, values, bom
        )

        if not vals:
            return vals

        sale_line_id = values.get('sale_line_id')
        sale_line = self.env['sale.order.line'].browse(sale_line_id) if sale_line_id else False

        if sale_line and sale_line.bom_id:
            vals['bom_id'] = sale_line.bom_id.id

        return vals