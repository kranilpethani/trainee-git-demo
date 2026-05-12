from odoo import fields, models, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    sale_order_total = fields.Float(
        string="Total Sale Orders",
        compute="_compute_sale_order_total",
    )
    limit = fields.Boolean(default=False)
    credit_limit = fields.Float()

    @api.depends()
    def _compute_sale_order_total(self):
        for partner in self:
            partner.sale_order_total = sum(
                self.env['sale.order'].search([
                    ('partner_id', '=', partner.id),
                    ('state', 'not in', ['done'])
                ]).mapped('amount_total')
            )