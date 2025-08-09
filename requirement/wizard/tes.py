import os
import ast
import jpype
import jpype.imports
from jpype.types import *

def extract_relationships(addons_path):
    """
    Extract model relationships from Python files in the given addons path.
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
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Assign):
                                for target in node.targets:
                                    if isinstance(target, ast.Name):
                                        if hasattr(node.value, "func") and isinstance(node.value.func, ast.Attribute):
                                            field_type = node.value.func.attr
                                            if field_type in ["Many2one", "One2many", "Many2many"]:
                                                relationships.append({
                                                    "model": os.path.basename(root),
                                                    "field": target.id,
                                                    "type": field_type,
                                                    "target": node.value.args[0].s if node.value.args else "unknown"
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



# Replace the `addons_path` with the path to your Odoo addons folder
addons_path = "/path/to/odoo/addons"

if not os.path.exists(addons_path):
    raise FileNotFoundError(f"The provided addons path does not exist: {addons_path}")

relationships = extract_relationships(addons_path)
if not relationships:
    print("No relationships found.")
else:
    # Generate PlantUML script
    plantuml_script = generate_plantuml(relationships)

    # Path to save the generated UML diagram
    output_file = "odoo_models_relationship.png"

    # Render the UML diagram
    render_uml_with_java(plantuml_script, output_file)





# Prerequisites:
# Install Flask:

# pip install flask
# Setup PlantUML Jar and Java:
# Ensure the plantuml.jar file path is correctly specified in the startJVM call.
# Running the Code:
# Update odoo_conf_path with the path to your odoo.conf file.
# Run the script, select the modules, and wait for the URL token.
# Open the provided URL in your browser to view the UML diagram.