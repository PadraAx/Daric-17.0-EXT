from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BldgAttrDocumentScoringRule(models.Model):
    _name = "bldg.attr.document.scoring.rule"
    _description = _("Scoring Rules for Document Group Attributes")
    _order = "attribute_id, sequence"
    _rec_name = "display_name"

    _sql_constraints = [
        (
            "unique_document_per_attr",
            "UNIQUE(attribute_id, document_key)",
            _("Each document key must be unique per attribute."),
        ),
    ]

    # --------------------------------------------------
    # CORE FIELDS
    # --------------------------------------------------
    display_name = fields.Char(
        string="Display Name", compute="_compute_display_name", store=True
    )
    code = fields.Char(
        string="Code",
        compute="_compute_code",
        store=True,
        readonly=True,
        index=True,
        help="Auto-generated code based on attribute and rule sequence",
    )

    attribute_id = fields.Many2one(
        "bldg.attr",
        required=True,
        ondelete="cascade",
        domain=[("data_type", "=", "document_group")],
    )

    sequence = fields.Integer(
        default=10, help="Controls display order in the interface"
    )

    document_key = fields.Char(
        string=_("Document Key"),
        required=True,
        help="Technical identifier for the document (e.g., 'final_permit')",
    )

    document_label = fields.Char(
        string=_("Document Label"),
        required=True,
        help="Human-readable label (e.g., 'Municipal Final Certificate')",
    )

    points = fields.Float(
        string=_("Points"),
        required=True,
        help="Scoring points assigned when this document is present",
    )

    required = fields.Boolean(
        string=_("Required"),
        default=False,
        help="Indicates if this document is mandatory for completeness",
    )

    active = fields.Boolean(
        default=True, help="If unchecked, this rule will be ignored"
    )

    description = fields.Text(
        string=_("Internal Note"), help="Optional notes for internal use"
    )

    # --------------------------------------------------
    # DISPLAY NAME COMPUTATION
    # --------------------------------------------------
    @api.depends("attribute_id", "document_label")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = (
                f"{rec.attribute_id.name or _('(No attribute)')}: {rec.document_label}"
            )

    # --------------------------------------------------
    # MATCHING LOGIC
    # --------------------------------------------------
    @api.model
    def match_rules(self, attribute_record, present_keys):
        """
        Return all document scoring rules that match the provided document keys.

        :param attribute_record: A bldg.attr record with data_type = document_group
        :param present_keys: A list of document keys (e.g., ['final_permit', 'compliance_cert'])
        :return: recordset of matching rules
        """
        if not attribute_record or attribute_record.data_type != "document_group":
            return self.browse()
        if not isinstance(present_keys, (list, tuple)):
            return self.browse()
        return self.search(
            [
                ("attribute_id", "=", attribute_record.id),
                ("document_key", "in", present_keys),
                ("active", "=", True),
            ]
        )

    @api.depends("attribute_id")
    def _compute_code(self):
        for rec in self:
            if not rec.attribute_id or not rec.attribute_id.code:
                rec.code = False
                continue

            # Get all rules under this attribute (current model only), ordered by id
            sibling_rules = self.search(
                [("attribute_id", "=", rec.attribute_id.id)], order="id"
            )

            # Determine index of this record among siblings
            index = 0
            for i, rule in enumerate(sibling_rules):
                if rule.id == rec.id:
                    index = i
                    break

            rec.code = f"{rec.attribute_id.code}{str(index + 1).zfill(2)}"
