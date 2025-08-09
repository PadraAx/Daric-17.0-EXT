from odoo import http
from odoo.http import request
import os
import tempfile

class PumlDownloadController(http.Controller):
    @http.route('/download/puml', type='http', auth='user')
    def download_puml(self, **kwargs):
        """
        Serve the generated odoo_models_relationship.puml file for download.
        """
        # Path to the generated .puml file
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, "odoo_models_relationship.puml")

        # Ensure the file exists
        if not os.path.exists(file_path):
            return request.not_found()

        # Read and serve the file
        with open(file_path, 'rb') as file:
            file_content = file.read()
            headers = [
                ('Content-Type', 'text/plain'),
                ('Content-Disposition', 'attachment; filename="odoo_models_relationship.puml"')
            ]
            return request.make_response(file_content, headers)