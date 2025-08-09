import os
import ast
from odoo import models, api, fields
from graphviz import Digraph
import logging

_logger = logging.getLogger(__name__)
class ReportGenerator(models.TransientModel):
    _name = 'report.generator'
    _description = 'Generate Report of Methods and Models'

    report_data = fields.Text(readonly=True)

    def generate_report(self):
        """
        Generate the report of methods and their usage
        """
        module_paths = self._get_module_paths()
        model_data = self._extract_model_data(module_paths)
        self._generate_uml(model_data)
        
        # Format and return the report as text for now
        report = self._format_report(model_data)
        self.write({'report_data': report})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'report.generator',
            'view_mode': 'form',
            'target': 'new',
        }

    def _get_module_paths(self):
        """
        Get the paths of all installed Odoo modules
        """
        module_paths = []
        base_path = self.env['ir.config_parameter'].sudo().get_param('addons_path')
        for module in self.env['ir.module.module'].search([('state', '=', 'installed')]):
            module_path = os.path.join(base_path, module.name)
            if os.path.isdir(module_path):
                module_paths.append(module_path)
        return module_paths

    def _extract_model_data(self, module_paths):
        """
        Extract data from model files
        """
        model_data = {}
        for path in module_paths:
            for root, _, files in os.walk(path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r') as f:
                            content = f.read()
                        try:
                            tree = ast.parse(content)
                            model_info = self._parse_ast(tree)
                            if model_info:
                                model_data.update(model_info)
                        except Exception as e:
                            self.env.cr.rollback()
                            _logger.error(f"Failed to parse {file_path}: {e}")
        return model_data

    def _parse_ast(self, tree):
        """
        Parse the AST of a Python file to find Odoo models and methods
        """
        model_info = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Attribute) and base.attr == 'Model':
                        class_name = node.name
                        methods = []
                        for subnode in node.body:
                            if isinstance(subnode, ast.FunctionDef):
                                methods.append(subnode.name)
                        model_info[class_name] = methods
        return model_info

    def _generate_uml(self, model_data):
        """
        Generate a UML diagram from the extracted data
        """
        dot = Digraph(comment='Model Methods UML')
        for model, methods in model_data.items():
            dot.node(model, model)
            for method in methods:
                dot.node(method, method)
                dot.edge(model, method)
        dot.render('/tmp/model_methods', view=True, format='png')

    def _format_report(self, model_data):
        """
        Format the extracted data into a text report
        """
        report = "Model Report:\n\n"
        for model, methods in model_data.items():
            report += f"Model: {model}\n"
            report += "Methods:\n"
            for method in methods:
                report += f"  - {method}\n"
            report += "\n"
        return report
