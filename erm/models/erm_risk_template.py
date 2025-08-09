from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from odoo import http
from odoo.http import request


class ERMRiskTemplate(models.Model):
    _name = "erm.risk.template"
    _description = "Risk Template"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    @api.depends("state")
    def _compute_has_write_access(self):
        for rec in self:
            rec.has_write_access = True

    def _compute_is_manager(self):
        for rec in self:
            rec.is_manager = True
            # if rec.user_has_groups('risk.group_admin'):
            #     rec.is_manager = True

    def _get_default_favorite_user_ids(self):
        return [(6, 0, [self.env.uid])]

    @api.model
    def _search_is_favorite(self, operator, value):
        if operator not in ["=", "!="] or not isinstance(value, bool):
            raise NotImplementedError(_("Operation not supported"))
        return [
            (
                "favorite_user_ids",
                "in" if (operator == "=") == value else "not in",
                self.env.uid,
            )
        ]

    def _compute_is_favorite(self):
        for risk in self:
            risk.is_favorite = self.env.user in risk.favorite_user_ids

    def _inverse_is_favorite(self):
        favorite_risks = not_fav_risks = self.env["erm.risk"].sudo()
        for risk in self:
            if self.env.user in risk.favorite_user_ids:
                favorite_risks |= risk
            else:
                not_fav_risks |= risk
        not_fav_risks.write({"favorite_user_ids": [(4, self.env.uid)]})
        favorite_risks.write({"favorite_user_ids": [(3, self.env.uid)]})

    @api.depends("impact_id", "likelihood_id")
    def _compute_inherent_risk_score(self):
        for record in self:
            if record.impact_id and record.likelihood_id:
                record.inherent_risk_score = (
                    record.impact_id.value * record.likelihood_id.value
                )
            else:
                record.inherent_risk_score = 0

    # @api.depends('user_id')
    # def _compute_allowed_categories(self):
    #     for rec in self:
    #         if rec.user_has_groups('erm.erm_group_admin'):
    #             mapped_assignments = self.env['erm.risk.assignment'].search([('active', '=', True)])
    #             if mapped_assignments:
    #                 rec.allowed_category_ids = mapped_assignments.mapped('category_id').ids
    #                 rec.allowed_source_ids = mapped_assignments.mapped('risk_source_id').ids
    #                 rec.allowed_affected_area_ids = mapped_assignments.mapped('affected_area_ids').ids
    #             else:
    #                 rec.allowed_category_ids = False
    #                 rec.allowed_source_ids = False
    #                 rec.allowed_affected_area_ids = False
    #         elif rec.user_has_groups('erm.erm_group_manager'):
    #             if rec.user_id:
    #                 mapped_assignments = self.env['erm.risk.assignment'].search([('user_id', '=', rec.env.uid),('active', '=', True)])
    #                 if mapped_assignments:
    #                     rec.allowed_category_ids = mapped_assignments.mapped('category_id').ids
    #                     rec.allowed_source_ids = mapped_assignments.mapped('risk_source_id').ids
    #                     rec.allowed_affected_area_ids = mapped_assignments.mapped('affected_area_ids').ids
    #                 else:
    #                     rec.allowed_category_ids = False
    #                     rec.allowed_source_ids = False
    #                     rec.allowed_affected_area_ids = False
    #             else:
    #                 rec.allowed_category_ids = False
    #                 rec.allowed_source_ids = False
    #                 rec.allowed_affected_area_ids = False

    @api.depends("user_id")
    def _compute_allowed_categories(self):
        for rec in self:
            if rec.user_has_groups("erm.erm_group_admin"):
                mapped_assignments = self.env["erm.risk.category"].search([])
                if mapped_assignments:
                    rec.allowed_category_ids = mapped_assignments.mapped("id")
                else:
                    rec.allowed_category_ids = False
            elif rec.user_has_groups("erm.erm_group_manager"):
                if rec.user_id:
                    mapped_assignments = self.env["erm.risk.category"].search(
                        [("user_id", "=", self.env.uid)]
                    )
                    if mapped_assignments:
                        rec.allowed_category_ids = mapped_assignments.mapped("id")
                    else:
                        rec.allowed_category_ids = False
            elif rec.user_has_groups("erm.erm_group_owner"):
                if rec.user_id:
                    mapped_assignments = self.env["erm.risk.assignment"].search(
                        [("user_id", "=", rec.env.uid), ("active", "=", True)]
                    )
                    if mapped_assignments:
                        rec.allowed_category_ids = mapped_assignments.mapped(
                            "category_id"
                        ).ids
                    else:
                        rec.allowed_category_ids = False
            elif rec.user_has_groups("erm.erm_group_analyst"):
                if rec.user_id:
                    mapped_assignments = self.env["erm.risk.assignment"].search(
                        [("user_id", "=", rec.env.uid), ("active", "=", True)]
                    )
                    if mapped_assignments:
                        rec.allowed_category_ids = mapped_assignments.mapped(
                            "category_id"
                        ).ids
                    else:
                        rec.allowed_category_ids = False
                else:
                    rec.allowed_category_ids = False

    user_id = fields.Many2one(
        "res.users", string="User", default=lambda self: self.env.user
    )
    req_code = fields.Char(
        string="Code",
        required=False,
        readonly=True,
        store=True,
        index=True,
        copy=True,
        tracking=False,
    )
    name = fields.Char(
        string="Title",
        required=True,
        store=True,
        index=False,
        copy=True,
        tracking=False,
    )
    description = fields.Html(string="Description")
    state = fields.Selection(
        selection=[
            ("1", "Draft"),
            ("2", "Identification"),
            ("3", "Analysis"),
            ("4", "Assessment"),
            ("5", "Treatment"),
            ("6", "Monitoring"),
        ],
        string="Stage",
        default="1",
        readonly=True,
        tracking=True,
    )

    has_write_access = fields.Boolean(
        "Has write access",
        compute="_compute_has_write_access",
        default=True,
        readonly=True,
    )
    tag_ids = fields.Many2many("erm.risk.tag", string="Tags", tracking=True)
    is_manager = fields.Boolean(
        "Is manager", compute="_compute_is_manager", default=False, readonly=True
    )

    favorite_user_ids = fields.Many2many(
        "res.users",
        "risk_favorite_user_rel1",
        "risk_id",
        "user_id",
        default=_get_default_favorite_user_ids,
        string="Members",
    )
    is_favorite = fields.Boolean(
        compute="_compute_is_favorite",
        inverse="_inverse_is_favorite",
        search="_search_is_favorite",
        compute_sudo=True,
        string="Favorite",
    )
    active = fields.Boolean(string="Active", default=True, copy=False)
    allowed_category_ids = fields.Many2many(
        "erm.risk.category",
        compute="_compute_allowed_categories",
        string="Allowed Categories",
        readonly=True,
    )
    # allowed_source_ids = fields.Many2many('erm.risk.source', string='Allowed Source', readonly=True)
    # allowed_affected_area_ids = fields.Many2many('erm.risk.affected.area', string='Allowed Affected Areas', readonly=True)
    category_id = fields.Many2one(
        "erm.risk.category",
        "Category",
        required=True,
        domain="[('id', 'in', allowed_category_ids)]",
    )
    risk_source_id = fields.Many2one(
        "erm.risk.source", "Risk Source", domain="[('category_id', '=', category_id)]"
    )
    affected_area_id = fields.Many2one(
        "erm.risk.affected.area",
        string="Affected Area",
        required=True,
        domain="[('category_id', '=', category_id)]",
    )

    impact_id = fields.Many2one(
        "erm.risk.impact",
        help="The extent of consequences if the risk occurs.",
        string="Impact (Severity)",
    )
    likelihood_id = fields.Many2one(
        "erm.risk.likelihood",
        help="The chance of the risk occurring.",
        string="Likelihood (Probability)",
    )
    analysis_ids = fields.One2many("erm.risk", "parent_id", string="Analysis")
    analysis_ids_count = fields.Integer(
        string="analysis", compute="_compute_analysis_ids_count"
    )
    inherent_risk_score = fields.Integer(
        "Inherit Risk",
        compute="_compute_inherent_risk_score",
        store=True,
        readonly=True,
    )

    @api.onchange("category_id")
    def _onchange_category_id(self):
        for rec in self:
            allowed_source_ids = False
            # rec.risk_source_id = False
            # rec.affected_area_id = False
            if rec.user_has_groups("erm.erm_group_admin") or rec.user_has_groups(
                "erm.erm_group_manager"
            ):
                mapped_assignments = self.env["erm.risk.assignment"].search(
                    [("active", "=", True)]
                )
                if mapped_assignments:
                    allowed_source_ids = mapped_assignments.mapped("risk_source_id").ids
                    return {
                        "domain": {
                            "risk_source_id": [
                                ("id", "in", allowed_source_ids),
                                ("category_id", "=", rec.category_id.id),
                            ]
                        }
                    }
                else:
                    allowed_source_ids = False
                    return {"domain": {"risk_source_id": [("id", "=", 0)]}}
            elif rec.user_has_groups("erm.erm_group_analyst") or rec.user_has_groups(
                "erm.erm_group_owner"
            ):
                mapped_assignments = self.env["erm.risk.assignment"].search(
                    [("user_id", "=", rec.env.uid), ("active", "=", True)]
                )
                if mapped_assignments:
                    allowed_source_ids = mapped_assignments.mapped("risk_source_id").ids
                    return {
                        "domain": {
                            "risk_source_id": [
                                ("id", "in", allowed_source_ids),
                                ("category_id", "=", rec.category_id.id),
                            ]
                        }
                    }
                else:
                    allowed_source_ids = False
                    return {"domain": {"risk_source_id": [("id", "=", 0)]}}
            else:
                return {"domain": {"risk_source_id": [("id", "=", 0)]}}

    @api.onchange("risk_source_id")
    def _onchange_risk_source_id(self):
        for rec in self:
            allowed_affected_area_ids = False
            # rec.affected_area_id = False
            if rec.user_has_groups("erm.erm_group_admin") or rec.user_has_groups(
                "erm.erm_group_manager"
            ):
                mapped_assignments = self.env["erm.risk.assignment"].search(
                    [
                        ("active", "=", True),
                        ("risk_source_id", "=", rec.risk_source_id.id),
                    ]
                )
                if mapped_assignments:
                    allowed_affected_area_ids = mapped_assignments.mapped(
                        "affected_area_ids"
                    ).ids
                    return {
                        "domain": {
                            "affected_area_id": [
                                ("id", "in", allowed_affected_area_ids),
                                ("category_id", "=", rec.category_id.id),
                            ]
                        }
                    }
                else:
                    allowed_affected_area_ids = False
                    return {"domain": {"affected_area_id": [("id", "=", 0)]}}
            elif rec.user_has_groups("erm.erm_group_analyst") or rec.user_has_groups(
                "erm.erm_group_owner"
            ):
                mapped_assignments = self.env["erm.risk.assignment"].search(
                    [
                        ("user_id", "=", rec.env.uid),
                        ("active", "=", True),
                        ("risk_source_id", "=", rec.risk_source_id.id),
                    ]
                )
                if mapped_assignments:
                    allowed_affected_area_ids = mapped_assignments.mapped(
                        "affected_area_ids"
                    ).ids
                    return {
                        "domain": {
                            "affected_area_id": [
                                ("id", "in", allowed_affected_area_ids),
                                ("category_id", "=", rec.category_id.id),
                            ]
                        }
                    }
                else:
                    allowed_affected_area_ids = False
                    return {"domain": {"affected_area_id": [("id", "=", 0)]}}
            else:
                return {"domain": {"affected_area_id": [("id", "=", 0)]}}

    def action_send_for_analysis(self):
        for rec in self:
            if rec.state == "1":
                rec.state = "2"

    def action_view_analysis(self):
        return {
            "name": "Analysis",
            "domain": [("parent_id", "=", self.id)],
            "view_mode": "tree,form",
            "res_model": "erm.risk",
            "type": "ir.actions.act_window",
            "context": {"create": True, "delete": False},
        }

    def _compute_analysis_ids_count(self):
        self.analysis_ids_count = self.env["erm.risk"].search_count(
            [("parent_id", "=", self.id)]
        )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            category_id = vals.get("category_id")
            if category_id:
                category = self.env["erm.risk.category"].browse(category_id)
                if "req_code" not in vals:
                    seq_name = f"erm_risk.seq.{category.name}.{ category.id}"
                    sequence = (
                        self.env["ir.sequence"]
                        .sudo()
                        .search([("code", "=", seq_name)], limit=1)
                    )
                    if not sequence:
                        sequence = (
                            self.env["ir.sequence"]
                            .sudo()
                            .create(
                                {
                                    "name": seq_name,
                                    "code": seq_name,
                                    "padding": "4",  # Adjust padding as needed
                                    "implementation": "standard",
                                    "number_increment": "1",
                                    "number_next": "0",
                                }
                            )
                        )
                    vals["req_code"] = (
                        f"{ category.code}-{sequence.next_by_code(seq_name)}"
                    )
        return super(ERMRiskTemplate, self).create(vals_list)

    @api.model
    def openRisksList(self):
        return {
            "name": "Risks",
            "res_model": "erm.risk.template",
            "type": "ir.actions.act_window",
            "views": [[False, "tree"], [False, "form"], [False, "search"]],
            "target": "current",
            "context": {"search_default_filter_my_erm_risk_template": 1},
            "domain": [],
        }

    @api.model
    def getConsequences(self, fields=None):
        consequences = self.env["erm.risk.consequence"].search([])
        return consequences.read(fields)

    @api.model
    def getLikelihoods(self, fields=None):
        likelihoods = self.env["erm.risk.likelihood"].search([])
        return likelihoods.read(fields)

    @api.model
    def getImpacts(self, fields=None):
        impacts = self.env["erm.risk.impact"].search([])
        return impacts.read(fields)

    @api.model
    def getRisks(self, risk_order="inherent_risk_score desc"):
        risks = self.sudo().search([], order=risk_order)
        categories = self.env["erm.risk.category"].search([])
        result = []
        for category in categories:
            current_category_risks = []
            for risk in risks:
                if risk.category_id.id == category.id:
                    current_category_risks.append(
                        {
                            "id": risk.id,
                            "likelihood": risk.likelihood_id.value,
                            "impact": risk.impact_id.value,
                        }
                    )
            result.append(
                {
                    "category_name": category.name,
                    "risks": current_category_risks,
                }
            )
        return result

    def openRiskForm(self):
        return {
            "name": self.display_name,
            "type": "ir.actions.act_window",
            "res_model": "erm.risk.template",
            "res_id": self.id,
            "views": [[False, "form"]],
            "view_mode": "form",
            "context": {"create": False, "edit": False},
            "domain": [],
            "target": "current",
        }
