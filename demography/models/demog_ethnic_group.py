from odoo import models, fields, api


class DemogEthnicGroup(models.Model):
    _name = "demog.ethnic.group"
    _description = "Ethnic Group"
    _order = "sequence, name"

    name = fields.Char(
        string="Ethnic Group Name", required=True, translate=True, index=True
    )
    code = fields.Char(string="Code", index=True)
    description = fields.Text(string="Description", translate=True)
    sequence = fields.Integer(default=10, help="Determines the display order")

    _sql_constraints = [
        ("name_uniq", "unique (name)", "Ethnic group name must be unique!"),
        ("code_uniq", "unique (code)", "Ethnic group code must be unique!"),
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
