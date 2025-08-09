# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import logging
import operator
import os
import glob
from tempfile import TemporaryFile
from os.path import splitext
from pathlib import Path
from odoo import api, fields, models, tools, sql_db, _
from odoo.exceptions import UserError
from odoo.tools.translate import TranslationImporter
import io
import ast
# import subprocess
from plantuml import PlantUML
import jpype
import jpype.imports
from jpype.types import *
import tempfile
from odoo import http
from odoo.http import request
import xmlrpc.client
from graphviz import Digraph

_logger = logging.getLogger(__name__)
addons_path = "/odoo17/odoo/addons"

def odoouser():
        # Configuration
        odoo_url = "http://localhost:8071/"
        db_name = "test12"
        username = "admin"
        password = "a"

        # Connect to Odoo
        common = xmlrpc.client.ServerProxy(f"{odoo_url}/xmlrpc/2/common")
        uid = common.authenticate(db_name, username, password, {})
        models = xmlrpc.client.ServerProxy(f"{odoo_url}/xmlrpc/2/object")

        if not uid:
            print("Authentication failed.")
            exit()

        # Fetch data
        print("Fetching data from Odoo...")
        users = models.execute_kw(db_name, uid, password, 'res.users', 'search_read', [[], ['name', 'groups_id', 'partner_id']])
        partners = models.execute_kw(db_name, uid, password, 'res.partner', 'search_read', [[], ['id', 'name', 'category_id']])
        groups = models.execute_kw(db_name, uid, password, 'res.groups', 'search_read', [[], ['name', 'implied_ids']])
        access_rights = models.execute_kw(db_name, uid, password, 'ir.model.access', 'search_read', [[], ['group_id', 'model_id', 'perm_read', 'perm_write', 'perm_create', 'perm_unlink']])
        record_rules = models.execute_kw(db_name, uid, password, 'ir.rule', 'search_read', [[], ['name', 'model_id', 'domain_force', 'groups']])
        models_list = models.execute_kw(db_name, uid, password, 'ir.model', 'search_read', [[], ['name', 'model']])
        partner_categories = models.execute_kw(db_name, uid, password, 'res.partner.category', 'search_read', [[], ['id', 'name']])

        # Prepare data mappings
        group_names = {group['id']: group['name'] for group in groups}
        model_names = {model['id']: model['model'] for model in models_list}
        partner_names = {partner['id']: partner['name'] for partner in partners}
        partner_categories_map = {cat['id']: cat['name'] for cat in partner_categories}

        user_groups = {user['name']: [group_names[gid] for gid in user['groups_id']] for user in users}
        user_partner_categories = {
            user['name']: [partner_categories_map[cat_id] for cat_id in partners if cat_id in user['partner_id']] if user['partner_id'] else []
            for user in users
        }

        # Create a graph
        graph = Digraph(comment="Odoo Access Rights and Record Rules Visualization")

        # Add users and their groups and partner tags
        for user, groups in user_groups.items():
            partner_tags = ", ".join(user_partner_categories.get(user, []))
            user_label = f"{user}\nTags: {partner_tags}" if partner_tags else user
            graph.node(user, shape='ellipse', color='blue', label=user_label)
            for group in groups:
                graph.node(group, shape='box', color='green')
                graph.edge(user, group)

        # Add groups and their models with permissions
        for access in access_rights:
            try:
                group_name = group_names.get(access['group_id'][0], "Unknown Group")
                model_name = model_names.get(access['model_id'][0], "Unknown Model")

                if group_name and model_name:
                    permission_label = "".join([
                        "R" if access['perm_read'] else "",
                        "W" if access['perm_write'] else "",
                        "C" if access['perm_create'] else "",
                        "D" if access['perm_unlink'] else ""
                    ])
                
                graph.node(model_name, shape='folder', color='orange')
                graph.edge(group_name, model_name, label=permission_label)
            except Exception as e:
                    print(f"Error processing file : {e}")


        # Add record rules
        for rule in record_rules:
            rule_name = rule['name']
            model_name = model_names.get(rule['model_id'][0], "Unknown Model")
            domain = rule['domain_force']
            group_ids = rule['groups']
            group_names_for_rule = [group_names[gid] for gid in group_ids if gid in group_names]

            rule_label = f"/{rule_name}\nDomain: {domain}/"
            graph.node(rule_name, shape='note', color='red', label=rule_label)
            if model_name:
                graph.edge(rule_name, model_name, label="/Applies to/")
            for group_name in group_names_for_rule:
                graph.edge(group_name, rule_name, label="/Has Rule/")

        # Save and render the graph
        output_file = "odoo_access_rights_record_rules"
        print(graph)
        print(f"Generating visualization at {output_file}.png")
        graph.render(output_file, format='png', cleanup=True)

        print("Visualization generated successfully.")

def extract_relationships(addons_path):
    """
    Extract model relationships (Many2one, One2many, Many2many) from Python files in the given addons path.
    Only include valid relations with a proper target model (no "unknown" or None).
    """
    relationships = []

    for root, _, files in os.walk(addons_path):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        file_content = f.read()
                        tree = ast.parse(file_content)

                        # Track model name
                        current_model_name = None

                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                current_model_name = None

                                # Extract `_name`
                                for body_item in node.body:
                                    if isinstance(body_item, ast.Assign):
                                        for target in body_item.targets:
                                            if (
                                                isinstance(target, ast.Name)
                                                and target.id == "_name"
                                                and isinstance(body_item.value, ast.Constant)
                                            ):
                                                current_model_name = body_item.value.value
                                        if current_model_name == None:
                                            for target in body_item.targets:
                                                if (
                                                    isinstance(target, ast.Name)
                                                    and target.id == "_inherit"
                                                    and isinstance(body_item.value, ast.Constant)
                                                ):
                                                    current_model_name = body_item.value.value
                                # Parse fields within the class
                                for body_item in node.body:
                                    if isinstance(body_item, ast.Assign):
                                        for target in body_item.targets:
                                            if (
                                                isinstance(target, ast.Name)
                                                and hasattr(body_item.value, "func")
                                                and isinstance(body_item.value.func, ast.Attribute)
                                            ):
                                                field_type = body_item.value.func.attr
                                                if field_type in ["Many2one", "One2many", "Many2many"]:
                                                    target_model = None

                                                    # Check positional arguments for target model
                                                    if body_item.value.args and isinstance(body_item.value.args[0], ast.Constant):
                                                        target_model = body_item.value.args[0].value

                                                    # Check keyword arguments for "comodel_name"
                                                    for keyword in body_item.value.keywords:
                                                        if keyword.arg == "comodel_name" and isinstance(keyword.value, ast.Constant):
                                                            target_model = keyword.value.value

                                                    # Only add if a valid target model is found
                                                    if target_model:
                                                        relationships.append({
                                                            "model": current_model_name,
                                                            "field": target.id,
                                                            "type": field_type,
                                                            "target": target_model,
                                                        })
                except Exception as e:
                    print(f"Error processing file {filepath}: {e}")

    return relationships
def generate_plantuml(relationships):
        """
        Generate a PlantUML diagram script from the extracted relationships.
        """
        plantuml = "@startuml\n"
        classes = set()
        for relation in relationships:
            model = relation["model"]
            field = relation["field"]
            target = relation["target"]
            field_type = relation["type"]
            classes.add(model)
            classes.add(target)
            if field_type == "Many2one":
                plantuml += f"{model} --> {target} : {field}\n"
            elif field_type == "One2many":
                plantuml += f"{model} --> {target} : {field}\n"
            elif field_type == "Many2many":
                plantuml += f"{model} --* {target} : {field}\n"
        for cls in classes:
            plantuml += f"class {cls} {{}}\n"
        plantuml += "@enduml"
        return plantuml
def convert_puml_to_png(puml_file):
    """
    Convert the given .puml file to a .png using the plantuml Python package.
    """
    # Initialize PlantUML object (it assumes PlantUML is installed in the system)
    plantuml = PlantUML(url='http://www.plantuml.com/plantuml/img')
    
    # Convert the .puml file to .png (the same name as the .puml file, but with .png extension)
    plantuml.processes_file(puml_file)
    print(f"Successfully converted {puml_file} to PNG.")

def convert_puml_to_png_local(puml_file):
    """
    Convert the given .puml file to a .png using local PlantUML installation.
    """
    # Specify the path to the local PlantUML executable (or JAR file)
    plantuml = PlantUML(executable='plantuml/plantuml-asl-1.2024.8.jar')  # or use path to the JAR file
    plantuml.processes_file(puml_file)
    print(f"Successfully converted {puml_file} to PNG.")

   

def render_uml_with_java(plantuml_script, output_path):
    """
    Render the UML diagram using PlantUML's Java API.
    """
    test = None
    # Start the JVM if not already started
    # jvm_path = os.path.join(os.environ['JAVA_HOME'], 'bin', 'server', 'jvm.dll')
    # jpype.startJVM(jvm_path)
    if not jpype.isJVMStarted():
        jpype.startJVM(classpath=["plantuml/plantuml-asl-1.2024.8.jar"])

    # jpype.startJVM(classpath=["plantuml/plantuml-asl-1.2024.8.jar"])

    # Import PlantUML's Java classes
    from net.sourceforge.plantuml import SourceStringReader

    try:
        # Create a SourceStringReader from the PlantUML script
        reader = SourceStringReader(plantuml_script)

        # Write the output diagram to the file
        with open(output_path, "wb") as output_stream:
            reader.outputImage(output_stream)
        print(f"UML diagram generated successfully: {output_path}")
    except Exception as e:
        print(f"Error rendering UML diagram: {e}")
    finally:
        # Shutdown the JVM
        jpype.shutdownJVM()

class ExtractRelationshipsWizard(models.TransientModel):
    _name = "extract.relationships.wizard"
    _description = "Extract Relationships Wizard"
  
    name = fields.Char(string='addons path', required='True')
    
    # /odoo17/odoo/oriel/customized/requirement
    # D:\odoo17\odoo\oriel\customized\erm
    
    def extract(self):
            """
            Extract relationships from Odoo models and generate a PlantUML script.
            Then convert the PlantUML file to a PNG image.
            """
            if not os.path.exists(self.name):
                raise FileNotFoundError(f"The provided addons path does not exist: {self.name}")

            # Extract model relationships
            relationships = extract_relationships(self.name)
            
            if not relationships:
                print("No relationships found.")
                return {
                    'type': 'ir.actions.client',
                    'tag': 'reload',
                }

            # Generate PlantUML script
            plantuml_script = generate_plantuml(relationships)
            # Path to save the generated UML diagram
            output_file = "odoo_models_relationship.png"

            # Render the UML diagram
            # render_uml_with_java(plantuml_script, output_file)


            temp_dir = tempfile.gettempdir()
            file_name = "odoo_models_relationship.puml"
            file_path = os.path.join(temp_dir, file_name)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(plantuml_script)

            # odoouser()
            # convert_puml_to_png_local(file_path)
            # Return a download response
            return {
                'type': 'ir.actions.act_url',
                'url': f'/download/puml?file_name={file_name}',
                'target': 'self',
            }
            
