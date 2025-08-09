import logging
from odoo import SUPERUSER_ID

_logger = logging.getLogger(__name__)

def post_init_hook(cr, registry):
    from odoo.api import Environment
    env = Environment(cr, SUPERUSER_ID, {})
    default_standard = 'iso_31000'  # Default standard
    env['res.config.settings']._load_default_master_data(default_standard)
