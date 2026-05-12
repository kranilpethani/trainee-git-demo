from odoo import fields, models, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )

    courier_charges = fields.Monetary(
        string="Courier Charges",
        currency_field='currency_id'
    )
    split_method = fields.Selection([('by_qty', 'Qty'),
        ('by_volume', 'Volume'),
        ('by_weight', 'Weight'),
        ('by_amount', 'Amount'),])