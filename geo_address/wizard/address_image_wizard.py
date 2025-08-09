from odoo import models, fields, api


class AddressImageWizard(models.TransientModel):
    _name = "res.address.image.wizard"
    _description = "Address Image Upload Wizard"

    image = fields.Binary(string="Image", required=True)
    address_id = fields.Many2one("res.address", string="Address")

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if self._context.get("default_address_id"):
            res["address_id"] = self._context["default_address_id"]
        return res

    def action_upload(self):
        self.ensure_one()
        if self.address_id:
            self.address_id.write({"image_1024": self.image})
        return {"type": "ir.actions.act_window_close"}
