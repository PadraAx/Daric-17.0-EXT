from odoo import models, fields, api


class ResReligion(models.Model):
    _name = "demog.religion"
    _description = "Religion"
    _order = "sequence, name"

    name = fields.Char(
        string="Religion Name", required=True, translate=True, index=True
    )
    code = fields.Char(string="Code", index=True)
    description = fields.Text(string="Description", translate=True)
    sequence = fields.Integer(default=10, help="Determines the display order")

    _sql_constraints = [
        ("name_uniq", "unique (name)", "Religion name must be unique!"),
        ("code_uniq", "unique (code)", "Religion code must be unique!"),
    ]

    @api.depends("name", "code")
    def name_get(self):
        result = []
        for record in self:
            name = record.name
            if record.code:
                name = f"[{record.code}] {name}"
            result.append((record.id, name))
        return result
