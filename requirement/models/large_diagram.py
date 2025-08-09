from odoo import models, fields
import base64
from graphviz import Digraph

class LargeDiagram(models.Model):
    _name = 'large.diagram'
    _description = 'Large Diagram Storage'

    name = fields.Char(string="Name")
    file_data = fields.Binary(string="Diagram File")
    file_name = fields.Char(string="File Name")
    
   
    
    def generate_diagram_action(self):
        self.generate_diagram()



class DiagramGenerator(models.Model):
    _inherit = 'large.diagram'

    def generate_diagram(self):
        # Generate the diagram
        graph = Digraph(comment="Sample Diagram")
        graph.node("A", "Start")
        graph.node("B", "End")
        graph.edge("A", "B")
        
        # Render the graph
        file_name = "diagram_output"
        file_path = graph.render(file_name, format='svg', cleanup=True)

        # Read the file and encode it
        with open(file_path, "rb") as file:
            file_data = file.read()
        
        # Save the file in the model
        self.file_data = base64.b64encode(file_data).decode('utf-8')
        self.file_name = f"{file_name}.svg"
