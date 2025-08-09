from odoo import models, fields, api


class KttProject(models.Model):
    _inherit = 'project.project'
    
    # Fields for telegram api
    telelegram_token = fields.Char(string="Telegram Token")
    chat_id = fields.Char(string="Chanel/Group Telegram")
    is_nof_telegram_task_created = fields.Boolean(string="Notification Task Created", default=False, help="When task is created send notification to telegram.", compute="_compute_telegram_fields", store=True)
    is_nof_telegram_task_edited = fields.Boolean(string="Notification Task Edited", default=False, help="When task is edited send notification to telegram.", compute="_compute_telegram_fields", store=True)
    is_nof_telegram_task_deleted = fields.Boolean(string="Notification Task Deleted", default=False, help="When task is deleted send notification to telegram.", compute="_compute_telegram_fields", store=True)
    
    @api.depends('telelegram_token', 'chat_id')
    def _compute_telegram_fields(self):
        for project in self:
            if(not project.chat_id or not project.telelegram_token):
                project.is_nof_telegram_task_created = False
                project.is_nof_telegram_task_edited = False
                project.is_nof_telegram_task_deleted = False