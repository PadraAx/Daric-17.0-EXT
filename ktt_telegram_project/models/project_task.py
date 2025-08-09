from odoo import models, fields, api
import requests


class ProjectTask(models.Model):
    _inherit = 'project.task'

    telegram_message_id = fields.Integer(string="Thread Message")

    # Send message to telegram when is task created
    @api.model_create_multi
    def create(self, vals_list):
        res = super(ProjectTask, self).create(vals_list)
        for task in res:
            project = task.project_id
            if project and project.is_nof_telegram_task_created:
                response = task._send_message_telegram()
                if (response['ok']):
                    task.telegram_message_id = response['result']['message_id']
        return res

    def write(self, vals):
        # res = super(ProjectTask, self).write(vals)
        if ('stage_id' in vals):
            project = self.project_id
            if (project and project.is_nof_telegram_task_edited):
                from_stage = self.stage_id.name
                stage = self.env['project.task.type'].browse(vals['stage_id'])
                self._send_message_telegram(
                    action='edited', from_stage=from_stage, to_stage=stage.name)
        return super(ProjectTask, self).write(vals)

    def unlink(self):
        for task in self:
            project = task.project_id
            if (project and project.is_nof_telegram_task_deleted):
                task._send_message_telegram(action='deleted')
        return super(ProjectTask, self).unlink()

    def _send_message_telegram(self, action='created', **kwargs):
        """ Send a message to telegram
            :param action: Including created, edited, deleted.
            @return: Dictionary of method request post
        """
        project = self.project_id
        tele_token = project.telelegram_token
        tele_chat_id = project.chat_id
        if (not tele_token or not tele_chat_id):
            return
        reply_message_id = False
        task_url = self.prepare_url()
        user_name = self.env.user.name
        text = f'<b>{self.name}</b>\n{action.capitalize()} by {user_name}\n<a href="{task_url}">See task</a>'
        if (action == 'edited' or action == 'deleted'):
            reply_message_id = self.telegram_message_id
        if (action == 'edited'):
            text = f'<b>{self.name}</b>\nEdited by {user_name}\nChanged stage <u>{kwargs["from_stage"]}</u> → <u>{kwargs["to_stage"]}</u>\n<a href="{task_url}">See task</a>'
        if (action == 'deleted'):
            text = f'<del>{self.name} deleted by {user_name}</del>'
        data = {
            "chat_id": tele_chat_id,
            "parse_mode": "html",
            "reply_to_message_id": reply_message_id,
            "text": text
        }
        response = requests.post(
            f'https://api.telegram.org/bot{tele_token}/sendMessage', data=data).json()
        return response

    def prepare_url(self, view='form'):
        """
            # ** Description **
            # - Prepare path direction to form view task
            # - Combine params (menu,action,view,model,self)
            # @return: str(url)
        """
        action = self.env.ref('project.act_project_project_2_project_task_all')
        menu = self.env.ref("project.menu_main_pm")
        active = self._context.get('active_id')
        if not active:
            active = 1
        url = "%s/web#id=%s&menu_id=%s&cids=1&action=%s&model" \
              "=%s&view_type=%s&active_id=%s" \
              % (
                  self.env['ir.config_parameter'].sudo(
                  ).get_param('web.base.url'),
                  self.id,
                  menu.id,
                  action.id,
                  self._name,
                  view,
                  active,
              )
        return url
