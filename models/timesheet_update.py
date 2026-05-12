from odoo import models, fields, api
from odoo.exceptions import UserError

class TimesheetUpdate(models.Model):
    _name = 'timesheet.update'
    _description = 'Timesheet Update'

    order_id = fields.Many2one(
        'sale.order',
        string="Order Reference"
    )

    task_name = fields.Char()

    project_id = fields.Many2one(
        'project.project',
        string="Project"
    )

    task_id = fields.Many2one(
        'project.task',
        string="Task"
    )

    parent_id = fields.Many2one(
        'project.task',
        string="Parent Task"
    )

    allocation_source = fields.Selection([
        ('manual', 'Manual'),
        ('sale_order', 'Sale Order'),
        ('project', 'Project'),
    ], string="Allocation Source")

    source_allocated_hours = fields.Float(
        string="Source Allocated Hours"
    )

    allocated_hours = fields.Float(
        string="Allocated Hours"
    )

    total_used_hours = fields.Float(
        string="Total Used Hours"
    )

    used_last_month = fields.Float(
        string="Total Used Last Month"
    )

    used_hours_period = fields.Float(
        string="Used Hours (Period)"
    )

    remaining_hours_custom = fields.Float(
        string="Remaining Hours"
    )

    effective_hours = fields.Float()

    period_used_hours = fields.Float(
        string='Used Hours (Period)',
        compute='_compute_period_used_hours',
        store=False
    )

    @api.depends('order_id')
    def _compute_period_used_hours(self):

        for record in self:

            record.period_used_hours = 0.0

            if not record.order_id:
                continue

            start_date = record.order_id.start_date
            end_date = record.order_id.stop_date

            if not start_date or not end_date:
                continue

            timesheets = self.env['account.analytic.line'].search([
                ('task_id', '=', record.task_id.id),
                ('date', '>=', start_date),
                ('date', '<=', end_date),
            ])

            record.period_used_hours = sum(
                timesheets.mapped('unit_amount')
            )
            print(record.period_used_hours)