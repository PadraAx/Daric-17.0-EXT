# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval
import logging

_logger = logging.getLogger(__name__)
_logger.warning("🧠 bldg_attr_formula_wizard.py is loaded!")


class BldgAttrFormulaWizard(models.TransientModel):
    _name = "bldg.attr.formula.wizard"
    _description = "Formula Calculator for Building Attribute"

    # ------------------------------------------------------------------
    # BASIC INFO
    # ------------------------------------------------------------------
    attribute_id = fields.Many2one(
        "bldg.attr", string="Target Attribute", required=True, readonly=True
    )

    operand_ids = fields.Many2many(
        "bldg.attr",
        "bldg_attr_formula_wizard_operand_rel",
        "wizard_id",
        "attr_id",
        string="Operands",
        help="Select attributes to use in the formula.",
    )

    # ------------------------------------------------------------------
    # LIVE DISPLAY & SYMBOL MAPPING
    # ------------------------------------------------------------------
    expression_manual = fields.Text(
        string="Formula",
        help="Live editable formula built by the calculator or typed manually.",
    )

    symbol_line_ids = fields.One2many(
        "bldg.attr.formula.wizard.symbol.line",
        "wizard_id",
        string="Symbol Mapping",
        readonly=False,
    )

    # ------------------------------------------------------------------
    # COMPUTE SYMBOL TABLE
    # ------------------------------------------------------------------
    @api.depends("operand_ids")
    def _compute_symbol_lines(self):
        """Create / update the symbol table (one row per operand)."""
        for wiz in self:
            current = {sl.attribute_id.id: sl for sl in wiz.symbol_line_ids}
            lines = []
            for attr in wiz.operand_ids:
                if attr.id in current:
                    line = current[attr.id]
                else:
                    symbol = re.sub(r"\W|^(?=\d)", "_", attr.name or "x")
                    line = self.env["bldg.attr.formula.wizard.symbol.line"].new(
                        {"attribute_id": attr.id, "symbol": symbol}
                    )
                lines.append(line.id)
            wiz.symbol_line_ids = [(6, 0, lines)]

    # ------------------------------------------------------------------
    # KEYPAD EVENT HANDLERS
    # ------------------------------------------------------------------
    def _append_text(self, text):
        """Append string to the current expression."""
        for wiz in self:
            wiz.expression_manual = (wiz.expression_manual or "") + str(text)

    def btn_plus(self):
        self._append_text(" + ")

    def btn_minus(self):
        self._append_text(" - ")

    def btn_mult(self):
        self._append_text(" * ")

    def btn_div(self):
        self._append_text(" / ")

    def btn_power(self):
        self._append_text(" ** ")

    def btn_sqrt(self):
        self._append_text(" sqrt(")

    def btn_log(self):
        self._append_text(" log(")

    def btn_left_paren(self):
        self._append_text("(")

    def btn_right_paren(self):
        self._append_text(")")

    def btn_del(self):
        """Delete last character."""
        for wiz in self:
            wiz.expression_manual = (wiz.expression_manual or "")[:-1]

    def btn_clear(self):
        """Clear entire expression."""
        for wiz in self:
            wiz.expression_manual = ""

    def btn_const(self):
        """Open a popup (client-side JS) to enter a constant; value is injected."""
        # Value comes from JS client action; see XML button for details.
        return {
            "type": "ir.actions.client",
            "tag": "bldg_formula_const_input",
            "target": "new",
        }

    def btn_insert_operand(self):
        symbol = self.env.context.get("symbol")
        line_id = self.env.context.get("line_id")

        for wiz in self:
            if not symbol or not line_id:
                continue
            # Append symbol to formula
            wiz.expression_manual = (wiz.expression_manual or "") + symbol
            # Remove the line from symbol_line_ids
            wiz.symbol_line_ids = [(3, int(line_id))]

    # ------------------------------------------------------------------
    # CONFIRM
    # ------------------------------------------------------------------
    def action_confirm(self):
        self.ensure_one()
        expr = (self.expression_manual or "").strip()
        if not expr:
            raise ValidationError(_("Formula is empty."))

        # Validate symbols
        symbols = {sl.symbol for sl in self.symbol_line_ids}
        for sym in symbols:
            if not sym.isidentifier():
                raise ValidationError(
                    _("Symbol “%s” is not a valid Python identifier.") % sym
                )

        # Validate Python syntax
        try:
            safe_eval(expr, {s: 1 for s in symbols}, mode="eval")
        except Exception as e:
            raise ValidationError(_("Invalid formula: %s") % e)

        # Write to bldg.attr
        self.attribute_id.formula = expr
        self.attribute_id.operand_ids.unlink()
        self.attribute_id.operand_ids = [
            (
                0,
                0,
                {
                    "parameter_id": sl.attribute_id.id,
                    "operand_name": sl.symbol,
                },
            )
            for sl in self.symbol_line_ids
        ]
        return {"type": "ir.actions.act_window_close"}

    def btn_insert_selected_symbol(self):
        self.ensure_one()
        active_ids = self.env.context.get("active_ids", [])
        lines = self.env["bldg.attr.formula.wizard.symbol.line"].browse(active_ids)
        # Filter lines belonging to this wizard only
        lines = lines.filtered(lambda l: l.wizard_id.id == self.id)
        for line in lines:
            self.expression_manual = (self.expression_manual or "") + (
                line.symbol or ""
            )


class BldgAttrFormulaWizardSymbolLine(models.TransientModel):
    _name = "bldg.attr.formula.wizard.symbol.line"
    _description = "Symbol Mapping Helper"

    wizard_id = fields.Many2one("bldg.attr.formula.wizard", ondelete="cascade")
    attribute_id = fields.Many2one("bldg.attr", required=True, ondelete="cascade")
    symbol = fields.Char(required=True)

    def btn_insert_symbol_line(self):
        for line in self:
            if line.symbol and line.wizard_id:
                line.wizard_id.expression_manual = (
                    line.wizard_id.expression_manual or ""
                ) + line.symbol
                line.unlink()
