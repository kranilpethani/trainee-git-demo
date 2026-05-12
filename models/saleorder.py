from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, time
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection([
        ('draft', "Quotation"),
        ('sent', "Quotation Sent"),
        ('manager_approve', 'Manager Approved'),
        ('boss_approve', 'Boss Approved'),
        ('sale', "Sales Order"),
        ('done', "Locked"),
        ('cancel', "Cancelled"),
    ], string="Status", readonly=True, copy=False, tracking=True)

    custom_line_ids = fields.One2many(
        'custom.line',
        'order_id',
        string="Custom Lines"
    )

    timesheet_update_ids = fields.One2many(
        'timesheet.update',
        'order_id',
        string="Custom Lines"
    )

    special_item = fields.Boolean()
    start_time = fields.Datetime()
    stop_time = fields.Datetime()
    start_date = fields.Date()
    stop_date = fields.Date()

    timesheet_html = fields.Html(
        compute="_compute_timesheet_html",
        sanitize=False,
    )

    @api.depends('timesheet_update_ids')
    def _compute_timesheet_html(self):

        for order in self:

            def float_to_time(value):
                hours = int(value)
                minutes = round((value - hours) * 60)
                return "%02d:%02d" % (hours, minutes)

            rows = ""

            total_source = 0.0
            total_allocated = 0.0
            total_used = 0.0
            total_last = 0.0
            total_period = 0.0
            total_remaining = 0.0

            for line in order.timesheet_update_ids:
                total_source += line.source_allocated_hours
                total_allocated += line.allocated_hours
                total_used += line.total_used_hours
                total_last += line.used_last_month
                total_period += line.used_hours_period
                total_remaining += line.remaining_hours_custom

                rows += f"""
                        <tr>
                            <td>{line.task_name or ''}</td>
                            <td>{line.parent_id.name if line.parent_id else ''}</td>
                            <td>{line.allocation_source or ''}</td>

                            <td class="num">
                                {float_to_time(line.source_allocated_hours)}
                            </td>

                            <td class="num">
                                {float_to_time(line.allocated_hours)}
                            </td>

                            <td class="num">
                                {float_to_time(line.total_used_hours)}
                            </td>

                           <td class="num">
                                {float_to_time(line.used_last_month)}
                            </td>
                            
                            <td class="num">
                                {float_to_time(line.used_hours_period)}
                            </td>
                            
                            <td class="num">
                                {float_to_time(line.remaining_hours_custom)}
                            </td>
                        </tr>
                    """

            order.timesheet_html = f"""
                    <style>
                        .ts-table {{
                            width: 100%;
                            border-collapse: collapse;
                            font-size: 14px;
                        }}

                        .ts-table th,
                        .ts-table td {{
                            border-bottom: 1px solid #ddd;
                            padding: 10px;
                            text-align: center;
                        }}

                        .ts-table th {{
                            background: #f5f5f5;
                            font-weight: 600;
                        }}

                        .ts-table .num {{
                            text-align: center;
                        }}

                        .ts-table tfoot td {{
                            font-weight: bold;
                            background: #fafafa;
                        }}
                    </style>

                    <table class="ts-table">

                        <thead>
                            <tr>
                                <th>Task Name</th>
                                <th>Parent Task</th>
                                <th>Allocation Source</th>
                                <th>Source Allocated Hours</th>
                                <th>Allocated Hours</th>
                                <th>Total Used Hours</th>
                                <th>Total Used Last month</th>
                                <th>Used Hours</th>
                                <th>Remaining Hours</th>
                            </tr>
                        </thead>

                        <tbody>
                            {rows}
                        </tbody>

                        <tfoot>
                            <tr>
                                <td>Total</td>
                                <td colspan="2"></td>
                                
                                <td class="num">{float_to_time(total_source)}</td>
                                <td class="num">{float_to_time(total_allocated)}</td>
                                <td class="num">{float_to_time(total_used)}</td>
                                <td class="num">{float_to_time(total_last)}</td>
                                <td class="num">{float_to_time(total_period)}</td>
                                <td class="num">{float_to_time(total_remaining)}</td>
                            </tr>
                        </tfoot>

                    </table>
                """


    @api.onchange('partner_id')
    def onchange_custom(self):
        for order in self:

            lines_data = []

            all_lines = self.env['sale.order.line'].search([
                ('order_id.partner_id', '=', order.partner_id.id),
                ('order_id.state', 'in', ['sale', 'done'])
            ])

            for line in all_lines:
                lines_data.append((0, 0, {
                    'product_id': line.product_id.id,
                    'quantities': line.product_uom_qty,
                    'price': line.price_unit,
                    'subtotal': line.price_subtotal,
                    'sale_order': line.order_id,
                }))

            order.custom_line_ids = lines_data

    def action_reorder(self):
        for order in self:
            selected_lines = order.custom_line_ids.filtered(lambda l: l.select_line)

            for line in selected_lines:
                if not line.product_id:
                    continue

                self.env['sale.order.line'].create({
                    'order_id': order.id,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantities or 1,
                    'price_unit': line.price,
                    'name': line.product_id.name,
                    'product_uom_id': line.product_id.uom_id.id,
                })

            selected_lines.write({'select_line': False})

    def action_manager_approve(self):
        for order in self:
            order.state = 'manager_approve'

    def action_boss_approve(self):
        for order in self:
            order.state = 'boss_approve'
            # order.state = 'sale'
        # return super().action_confirm( )

    def action_confirm(self):
        for order in self:
            total_limit = order.partner_id.sale_order_total + order.amount_total
            if order.partner_id.limit and order.partner_id.credit_limit <= total_limit:
                raise UserError("User Limit Across")

            # special_lines = order.order_line.filtered(
            #     lambda l: l.product_id.product_tmpl_id.special_item
            # )
            # #
            # for rec in special_lines:
            #     if rec.special_clicked == False:
            #         raise UserError("First Verify Special Item")
            #
            # params = self.env['ir.config_parameter'].sudo()

            # min_val = float(params.get_param('custom.min', 0))
            # max_val = float(params.get_param('custom.max', 0))

            # if order.amount_total > min_val :
            #     if order.amount_total > max_val:
            #         if order.state != 'boss_approve' :
            #             raise UserError("Order must be Boss Approved before confirmation.")
            #     elif order.state not in ['manager_approve', 'boss_approve']:
            #         raise UserError("Order must be Manager Or Boss Approved before confirmation.")
            #
            # if special_lines and order.state != 'boss_approve' :
            #             raise UserError("Order must be verify by boss.")
            #
            # for item in order.order_line:
            #     if item.discount >= 50 and order.state != 'boss_approve':
            #         raise UserError("Some Product Discount is Above 50%, Order must be verify by boss.")

        return super().action_confirm()

    def _confirmation_error_message(self):
        self.ensure_one()

        allowed_states = [
            'draft',
            'sent',
            'manager_approve',
            'boss_approve',
        ]

        if self.state not in allowed_states:
            return _("This order cannot be confirmed from its current state.")

        if any(
                not line.display_type
                and not line.is_downpayment
                and not line.product_id
                for line in self.order_line
        ):
            return _("Some order lines are missing a product, you need to correct them before going further.")

        return False

    def action_start(self):
        self.start_time = datetime.now()

    def action_cron_stop(self):
        params = self.env['ir.config_parameter'].sudo()

        times_val = float(params.get_param('custom.times', 0)) * 60
        product_param = params.get_param('custom.product_id')

        if not product_param or not product_param.isdigit():
            return

        product = self.env['product.product'].browse(int(product_param))

        records = self.env['sale.order'].search([
            ('start_time', '!=', False),
            ('stop_time', '=', False)
        ])

        now = fields.Datetime.now()

        for rec in records:
            rec.stop_time = now

            start = fields.Datetime.to_datetime(rec.start_time)
            stop = fields.Datetime.to_datetime(rec.stop_time)

            time_qty = (stop - start).total_seconds() / 60

            if time_qty >= times_val:

                self.env['sale.order.line'].create({
                    'order_id': rec.id,
                    'product_id': product.id,
                    'product_uom_qty': round(time_qty),
                    'price_unit': product.lst_price,
                    'name': product.name,
                    'product_uom_id': product.uom_id.id,
                })

    def action_stop(self):
        for rec in self:
            rec.stop_time = datetime.now()

            params = self.env['ir.config_parameter'].sudo()
            times_val = float(params.get_param('custom.times', 0)) * 60
            product_param = params.get_param('custom.product_id')

            if not product_param or not product_param.isdigit():
                continue

            product = self.env['product.product'].browse(int(product_param))

            if not rec.start_time:
                continue

            time_qty = (rec.stop_time - rec.start_time).total_seconds() / 60

            if time_qty >= times_val:
                time_qty = times_val

            self.env['sale.order.line'].create({
                'order_id': rec.id,
                'product_id': product.id,
                'product_uom_qty': round(time_qty),
                'price_unit': product.lst_price,
                'name': product.name,
                'product_uom_id': product.uom_id.id,
            })





            # for line in order.order_line:
            #     if line.product_id.id == product_param:
            #         print(round(time_qty))
            #         if round(time_qty) >= times_val:
            #             line.product_uom_qty = times_val
            #         else:
            #             line.product_uom_qty = round(time_qty)






















    # @api.constrains('amount_total')
    # def _check_amount_range(self):
    #     for order in self:
    #         params = self.env['ir.config_parameter'].sudo()
    #
    #         min_val = float(params.get_param('custom.min', 0))
    #         max_val = float(params.get_param('custom.max', 0))
    #
    #         if order.amount_total < min_val:
    #             raise ValidationError(
    #                 f"Order amount must be greater than {min_val}"
    #             )
    #
    #         if order.amount_total > max_val :
    #             raise ValidationError("Boss Approval Is Required")









            # for line in order.custom_line_ids:
            #
            #     if not line.product_id:
            #         continue
            #
            #     self.env['sale.order.line'].create({
            #         'order_id': order.id,
            #         'product_id': line.product_id.id,
            #         'product_uom_qty': line.quantities or 1,
            #         'name': line.product_id.name,
            #         'product_uom_id': line.product_id.uom_id.id,
            #     })
            #
            #
            # return {
            #     'type': 'ir.actions.act_window',
            #     'res_model': 'sale.order',
            #     'view_mode': 'form',
            #     'res_id': self.id,
            # }
