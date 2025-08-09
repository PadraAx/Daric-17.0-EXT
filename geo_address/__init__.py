# geo_address/__init__.py
from . import models
from . import wizard

# import the actual function objects
from .models.hooks.hooks import (
    post_init_hook as _post_init_hook,
    pre_init_hook as _pre_init_hook,
)

# expose them with the exact names Odoo expects
pre_init_hook = _pre_init_hook
post_init_hook = _post_init_hook
