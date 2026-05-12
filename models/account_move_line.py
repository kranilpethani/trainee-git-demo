from odoo import fields, models, api, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )

    courier_charge = fields.Monetary(
        string="Courier Charge",
        currency_field='currency_id',
        compute = '_compute_courier_charge'
    )

    @api.onchange('move_id.split_method','move_id.courier_charges','move_id.invoice_line_ids.quantity','quantity','move_id.amount_untaxed')
    def _compute_courier_charge(self):

        for line in self:
            move = line.move_id
            line.courier_charge = 0
            if move.split_method == 'by_qty':
                total = self._compute_total_quantity()
                line.courier_charge = (move.courier_charges/total) * line.quantity

            if move.split_method == 'by_volume':
                total = self._compute_total_volume()
                print(total)
                line.courier_charge = (move.courier_charges / total) * (line.product_id.volume * line.quantity)

            if move.split_method == 'by_weight':
                total = self._compute_total_weight()
                line.courier_charge = (move.courier_charges / total) * (line.product_id.weight * line.quantity)

            if move.split_method == 'by_amount':
                total = move.amount_untaxed
                print(total)
                line.courier_charge = (move.courier_charges / total) * line.price_subtotal

    def _compute_total_quantity(self):
        total_qty = 0
        for line in self:
            total_qty += line.quantity

        return total_qty

    def _compute_total_volume(self):
        total_volume = 0
        for line in self:
            total_volume += line.product_id.volume * line.quantity

        return total_volume

    def _compute_total_weight(self):
        total_weight = 0
        for line in self:
            total_weight += line.product_id.weight * line.quantity

        return total_weight

