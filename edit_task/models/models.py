# -*- coding: utf-8 -*-

from odoo import models, fields, api
import calendar




class KnowledgeUsed(models.Model):
    _name = 'knowledge.used'
    _rec_name = 'name'
    _description = 'Knowledge used'

    name = fields.Char()



class ProjectTaskInh(models.Model):
    _inherit = 'project.task'

    task_solution = fields.Selection(
        [("0", 'Very Low'), ("1", 'Low'), ("2", 'Normal'), ("3", 'High'), ("4", 'Very High')],
        string='Solution', groups="edit_task.id_task_management_groups", default="0")
    speed = fields.Selection([("0", 'Very Low'), ("1", 'Low'), ("2", 'Normal'), ("3", 'High'), ("4", 'Very High')],
                             string='Speed', groups="edit_task.id_task_management_groups", default="0")
    code_clean = fields.Selection([("0", 'Very Low'), ("1", 'Low'), ("2", 'Normal'), ("3", 'High'), ("4", 'Very High')],
                                  string='Clean code', groups="edit_task.id_task_management_groups", default="0")
    thought = fields.Selection([("0", 'Very Low'), ("1", 'Low'), ("2", 'Normal'), ("3", 'High'), ("4", 'Very High')],
                               string='Developer thought', groups="edit_task.id_task_management_groups", default="0")
    knowledge_ids = fields.Many2many(comodel_name="knowledge.used", string="Knowledge used",
                                     groups="edit_task.id_task_management_groups")
    is_evaluation = fields.Boolean(string="",  )

class EvaluationReport(models.Model):
    _name = 'evaluation.report'
    _description = "Evaluation Report"

    start_date = fields.Date(required=True, default=fields.Date.today().replace(day=1))
    end_date = fields.Date(required=True,  default=fields.Date.today().replace(day=calendar.monthrange(fields.Date.today().year, fields.Date.today().month)[1]))
    user_id = fields.Many2one(comodel_name="res.users", string="Developer", required=False, )
    work_hours = fields.Integer()
    number_of_tasks = fields.Integer()
    speed = fields.Selection([("0", 'Very Low'), ("1", 'Low'), ("2", 'Normal'), ("3", 'High'), ("4", 'Very High')],
                             string='Average Speed', default="0")
    code_clean = fields.Selection([("0", 'Very Low'), ("1", 'Low'), ("2", 'Normal'), ("3", 'High'), ("4", 'Very High')],
                                  string='Average Clean code', default="0")
    thought = fields.Selection([("0", 'Very Low'), ("1", 'Low'), ("2", 'Normal'), ("3", 'High'), ("4", 'Very High')],
                               string='Average Developer thought', default="0")
    knowledge_ids = fields.Many2many(comodel_name="knowledge.used", string="Knowledge used")
    coupler = fields.Boolean(string="")
    user_ids = fields.Many2many(comodel_name="res.users", string="Developers")
    evaluation_report_ids = fields.Many2many(comodel_name="evaluation.report", relation="relation_evaluation_report",
                                             column1="column1_evaluation_report", column2="column2_evaluation_report",
                                             string="", )

    def get_int(self, numbers):
        return [int(no) for no in numbers]

    @api.onchange('start_date', 'end_date', 'user_id', 'user_ids')
    def get_evaluation(self):
        for rec in self:
            if rec.user_ids:
                rec.evaluation_report_ids = False
                rec.evaluation_report_ids = [(0, 0, {
                    "start_date": rec.start_date,
                    "end_date": rec.end_date,
                    "user_id": user.id,
                }) for user in rec.user_ids]
                rec.evaluation_report_ids.get_evaluation()
            elif rec.user_id:
                task_line = self.env['account.analytic.line'].sudo().search(
                    [('date', '>=', rec.start_date), ('date', '<=', rec.end_date),
                     ('task_id.user_ids', 'in', rec.user_id.ids), ])
                taskes = task_line.task_id
                if taskes:
                    rec.number_of_tasks = len(taskes)
                    rec.work_hours = sum(task_line.mapped('unit_amount'))
                    evaluation_taskes=taskes.filtered(lambda l: l.is_evaluation)
                    if evaluation_taskes:
                        taskes=evaluation_taskes
                        rec.speed = str(int(round(sum(rec.get_int(taskes.mapped('speed'))) / len(taskes), 0)))
                        rec.code_clean = str(int(round(sum(rec.get_int(taskes.mapped('code_clean'))) / len(taskes), 0)))
                        rec.thought = str(int(round(sum(rec.get_int(taskes.mapped('thought'))) / len(taskes), 0)))
                        rec.knowledge_ids = taskes.knowledge_ids.ids

    def action_Print(self):
        return self.env.ref('edit_task.id_evaluation_report').report_action(self)

    def view_tasks(self):
        if self.user_ids:
            task_line = self.env['account.analytic.line'].sudo().search(
                [('date', '>=', self.start_date), ('date', '<=', self.end_date),
                 ('task_id.user_ids', 'in', self.user_ids.ids), ])
            taskes = task_line.task_id
        elif self.user_id:
            task_line = self.env['account.analytic.line'].sudo().search(
                [('date', '>=', self.start_date), ('date', '<=', self.end_date),
                 ('task_id.user_ids', 'in', self.user_id.ids), ])
            taskes = task_line.task_id

        return {
            'name': 'Task',
            'domain': [('id', 'in', taskes.ids)],
            'res_model': 'project.task',
            'view_mode': 'kanban,tree,form,gantt,calendar,pivot,graph,activity',
            'type': 'ir.actions.act_window',
        }
