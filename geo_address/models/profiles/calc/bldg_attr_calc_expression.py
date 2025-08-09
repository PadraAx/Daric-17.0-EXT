# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import operator
import math

# ------------------------------------------------------------------
# Constants & Operator Implementations
# ------------------------------------------------------------------
OPERATOR_ARITY = {
    "+": 2,
    "-": 2,
    "*": 2,
    "/": 2,
    "^": 2,
    "mod": 2,
    "nCr": 2,
    "nPr": 2,
    "√": 1,
    "x²": 1,
    "x³": 1,
    "10^x": 1,
    "e^x": 1,
    "log": 1,
    "ln": 1,
    "1/x": 1,
    "abs": 1,
    "!": 1,
    "sin": 1,
    "cos": 1,
    "tan": 1,
}

OPERATOR_SELECTION = [(k, k) for k in OPERATOR_ARITY]

OPS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "^": operator.pow,
    "mod": lambda a, b: a % b,
    "nCr": lambda n, k: math.comb(int(n), int(k)),
    "nPr": lambda n, k: math.perm(int(n), int(k)),
    "√": math.sqrt,
    "x²": lambda x: x * x,
    "x³": lambda x: x**3,
    "10^x": lambda x: 10**x,
    "e^x": math.exp,
    "log": math.log10,
    "ln": math.log,
    "1/x": lambda x: 1.0 / x if x else 0.0,
    "abs": abs,
    "!": lambda x: math.factorial(int(x)),
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
}


# ------------------------------------------------------------------
# Calculation Group  (Expression Node)
# ------------------------------------------------------------------
class BldgCalcGroup(models.Model):
    _name = "bldg.calc.group"
    _description = "Calculation Group (Expression Node)"
    _order = "sequence, id"

    # ------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------
    name = fields.Char(
        string="Group Code",
        compute="_compute_name",
        store=True,
        help="Technical identifier generated from the target attribute and operator.",
    )
    code = fields.Char(
        string="Code",
        compute="_compute_code",
        store=True,
        readonly=True,
        index=True,
        help="Auto-generated code based on target attribute and sequence position",
    )

    target_param_id = fields.Many2one(
        "bldg.attr",
        required=True,
        string="Target Attribute",
        help="Attribute whose value will be set by evaluating this group.",
    )
    target_param_computation_type = fields.Selection(
        related="target_param_id.computation_type",
        store=True,
        readonly=True,
    )
    target_param_value = fields.Float(
        string="Computed Target Value",
        compute="_compute_target_param_value",
        store=True,
        help="Evaluated value of the expression for the given profile.",
    )

    operator = fields.Selection(
        OPERATOR_SELECTION,
        required=True,
        string="Operator",
        help="Operator to apply on operands (parameters + sub-groups).",
    )

    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Order within the parent group or tree view.",
    )

    parent_id = fields.Many2one(
        "bldg.calc.group", string="Parent Group", index=True, ondelete="cascade"
    )

    child_ids = fields.One2many("bldg.calc.group", "parent_id", string="Sub-Groups")

    param_ids = fields.One2many("bldg.calc.param", "group_id", string="Parameters")

    # ------------------------------------------------------------------
    # Computes / Inverses
    # ------------------------------------------------------------------
    @api.depends("target_param_id.name", "operator")
    def _compute_name(self):
        for rec in self:
            base = rec.target_param_id.name or "?"
            rec.name = f"{base}.{rec.operator}"

    @api.depends("target_param_id", "parent_id")
    def _compute_code(self):
        for rec in self:
            if not rec.target_param_id or rec.parent_id:
                rec.code = False
                continue

            # Fetch top-level expressions (no parent) under the same attribute
            siblings = self.search(
                [
                    ("target_param_id", "=", rec.target_param_id.id),
                    ("parent_id", "=", False),
                ],
                order="id",
            )

            # Compute position among siblings
            index = 0
            for i, expr in enumerate(siblings):
                if expr.id == rec.id:
                    index = i
                    break

            sequence = str(index + 1).zfill(2)
            rec.code = f"{rec.target_param_id.code}{sequence}"

    def compute_and_store_value(self, profile):
        """
        Evaluate the expression for a given profile and store the result
        in the attribute line corresponding to the target_param_id.
        """
        self.ensure_one()

        if not self.target_param_id:
            return  # No target defined, nothing to store

        value = self.evaluate(profile)
        attr = self.target_param_id

        # Locate the line in the profile
        line = profile.attribute_line_ids.filtered(
            lambda l: l.attribute_id.id == attr.id
        )

        if not line:
            # Create the line if missing
            line = self.env["bldg.profile.attribute.line"].create(
                {
                    "profile_id": profile.id,
                    "attribute_id": attr.id,
                }
            )

        # Set value depending on data type
        if attr.data_type == "float":
            line.value_float = value
        elif attr.data_type == "integer":
            line.value_integer = int(value)

    # ------------------------------------------------------------------
    # Constraints
    # ------------------------------------------------------------------
    @api.constrains("operator", "param_ids", "child_ids")
    def _check_operand_count_and_operator(self):
        for rec in self:
            arity = OPERATOR_ARITY.get(rec.operator, 0)
            total = len(rec.param_ids) + len(rec.child_ids)

            if total != arity:
                raise ValidationError(
                    f"{rec.name or 'New'}: operator '{rec.operator}' "
                    f"requires exactly {arity} operand(s), found {total}."
                )

    # ------------------------------------------------------------------
    # Evaluation  (placeholder)
    # ------------------------------------------------------------------
    def evaluate(self, record=None):
        """
        Recursively evaluate this expression node and return a numeric result.
        :param record: the profile (bldg.prof) whose attribute values are used
        """
        self.ensure_one()
        record = record or self.env["bldg.prof"]  # fallback to empty recordset

        # Evaluate parameters (attribute lines) in sequence order
        param_values = []
        for param in sorted(self.param_ids, key=lambda p: p.sequence):
            line = param.calc_param_id
            if line.attribute_id.data_type == "float":
                value = line.value_float
            elif line.attribute_id.data_type == "integer":
                value = line.value_integer
            else:
                value = 0  # fallback for unexpected types
            param_values.append(value)

        # Evaluate child groups recursively
        child_values = [
            child.evaluate(record)
            for child in sorted(self.child_ids, key=lambda g: g.sequence)
        ]

        operands = param_values + child_values
        return self._apply_operator(self.operator, operands)

    def _get_param_value(self, param, record):
        """
        Return the numeric value of the parameter for the given profile.
        """
        line = record.attribute_line_ids.filtered(
            lambda l: l.attribute_id == param.calc_param_id
        )
        if not line:
            return 0.0

        if param.calc_param_id.data_type == "integer":
            return float(line.value_integer or 0)
        elif param.calc_param_id.data_type == "float":
            return line.value_float or 0.0
        return 0.0

    def _apply_operator(self, op, operands):
        """Return numeric result for operator *op* and *operands*."""
        if op in OPS:
            return float(OPS[op](*operands))
        raise ValueError(f"Unsupported operator: {op}")

    @api.depends(
        "param_ids.value_integer",
        "param_ids.value_float",
        "child_ids.target_param_value",
    )
    def _compute_target_param_value(self):
        for rec in self:
            profile = rec.env["bldg.prof"]  # Or pass in dynamically if needed
            try:
                rec.target_param_value = rec.evaluate(profile)
            except Exception:
                rec.target_param_value = 0.0  # fallback if expression fails
