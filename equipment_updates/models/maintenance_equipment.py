from ast import literal_eval
from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging
from collections import defaultdict
_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"
CLOSED_STATES = {
    '1_done': 'Done',
    '1_canceled': 'Canceled',
}


class maintenance_equipment(models.Model):
    _inherit = "maintenance.equipment"

    is_product = fields.Boolean('Is Product')
    product_product_id = fields.Many2one('product.product', 'Product')
    is_employee = fields.Boolean('Is Timesheet')
    hr_employee_id= fields.Many2one('hr.employee', 'Employee')
    equipment_user_id = fields.Many2one('res.users', 'Equipment User')
    has_timesheet = fields.Boolean(compute='_compute_has_timesheet')
    task_state = fields.Selection([
        ('01_in_progress', 'In Progress'),
        ('02_changes_requested', 'Changes Requested'),
        ('03_approved', 'Approved'),
        *CLOSED_STATES.items(),
        ('04_waiting_normal', 'Waiting'),
    ], string='Task State', compute="get_task_state"
    )
    service_count = fields.Integer(compute="_compute_count_all", string='Services')
    contract_count = fields.Integer(compute="_compute_count_all", string='Contract Count')
    def _compute_count_all(self):
        for vehicle in self:
            vehicle.service_count = self.env['equipment.vehicle.log.services'].search_count([('maintenance_equipment_id', 'in', self.ids)])
            vehicle.contract_count =self.env['equipment.vehicle.log.contract'].search_count([('maintenance_equipment_id', 'in', self.ids)])

    def return_action_to_open(self):
        """ This opens the xml view specified in xml_id for the current vehicle """
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id:

            res = self.env['ir.actions.act_window']._for_xml_id('equipment_updates.%s' % xml_id)
            res.update(
                context=dict(self.env.context, default_maintenance_equipment_id=self.id,maintenance_equipment_id=self.id, group_by=False),
                domain=[('maintenance_equipment_id', '=', self.id)]
            )
            return res
        return False

    def get_task_state(self):
        for record in self:
            record.task_state = ''
            if record.is_employee and record.hr_employee_id and record.hr_employee_id.user_id:
                project_task_objs = self.env['project.task'].sudo().search(
                    [('equipment_user_ids', '=', record.hr_employee_id.user_id.id)], limit=1)
                if project_task_objs:
                    record.task_state = project_task_objs.state

    def _compute_has_timesheet(self):
        self.env.cr.execute("""
            SELECT id, EXISTS(SELECT 1 FROM account_analytic_line WHERE project_id IS NOT NULL AND employee_id = e.id limit 1)
              FROM hr_employee e
             WHERE id in %s
            """, (tuple(self.ids),))

        result = {eid[0]: eid[1] for eid in self.env.cr.fetchall()}

        for employee in self:
            employee.has_timesheet = result.get(employee.id, False)

    def create_equipment_product(self):
        if self.product_product_id:
            self.product_product_id.write(
                {'name': self.name, 'is_equipment': True, 'maintenance_equipment_id': self.id, 'detailed_type':'service', 'service_policy': 'delivered_timesheet'})
        else:
            product_product_obj = self.env['product.product'].sudo().create(
                {'name': self.name, 'is_equipment': True, 'maintenance_equipment_id': self.id, 'detailed_type':'service', 'service_policy': 'delivered_timesheet'})
            self.product_product_id = product_product_obj.id

        return True
    def create_equipment_employee(self):
        companyname = self.env.user.company_id.name
        if self.equipment_user_id:
            self.equipment_user_id.write({
                'name': self.name, 'login': self.name + "@" + companyname + ".com",
                'email': self.name + "@" + companyname + ".com",
                'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
            })
        else:
            equipment_user_obj = self.env['res.users'].sudo().create({
                'name': self.name, 'login': self.name + "@" + companyname + ".com",
                'email': self.name + "@" + companyname + ".com",
                'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
            })
            self.equipment_user_id = equipment_user_obj.id
        if self.hr_employee_id:
            self.hr_employee_id.write(
                {'name': self.name, 'is_equipment': True, 'employee_equipment_id': self.id,
                 'employee_type': 'equipment', 'user_id': self.equipment_user_id.id})
        else:
            hr_employee_obj = self.env['hr.employee'].sudo().create(
                {'name': self.name, 'is_equipment': True, 'employee_equipment_id': self.id,
                 'employee_type': 'equipment', 'user_id': self.equipment_user_id.id})
            self.hr_employee_id = hr_employee_obj.id
        return True

    def action_timesheet_from_employee(self):
        action = self.env["ir.actions.act_window"]._for_xml_id("hr_timesheet.timesheet_action_from_employee")
        context = literal_eval(action['context'].replace('active_id', str(self.id)))
        context['create'] = context.get('create', True) and self.active
        context['domain'] = [('project_id', '!=', False), ('employee_id', '=', self.hr_employee_id.id)]
        context['grid_range'] = "week"
        action['context'] = context
        return action
