# geo_address/models/hooks/hooks.py
from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


def assign_capitals(env):
    """Post-init hook that properly assigns capital cities with recursion protection"""
    try:
        City = env["res.city"]

        # 1. Process country capitals
        country_capitals = City.search([("is_country_capital", "=", True)])
        for city in country_capitals:
            if city.country_id and not city.country_id.capital_id:
                city.country_id.sudo().with_context(updating_capital=True).write(
                    {"capital_id": city.id}
                )

        # 2. Process state capitals
        state_capitals = City.search([("is_state_capital", "=", True)])
        for city in state_capitals:
            if city.state_id and not city.state_id.capital_id:
                city.state_id.sudo().with_context(updating_capital=True).write(
                    {"capital_id": city.id}
                )

        # 3. Process county capitals
        if "is_county_capital" in City._fields:
            county_capitals = City.search([("is_county_capital", "=", True)])
            for city in county_capitals:
                if city.county_id and not city.county_id.capital_id:
                    city.county_id.sudo().with_context(updating_capital=True).write(
                        {"capital_id": city.id}
                    )

        env.cr.commit()
    except Exception as e:
        env.cr.rollback()
        _logger.error("Failed to assign capitals: %s", str(e), exc_info=True)
        raise


def create_gist_indexes(env):
    """Create GiST indexes required for range exclusion."""
    env.cr.execute(
        """
        DROP INDEX IF EXISTS bldg_score_no_int_overlap_idx;
        CREATE INDEX IF NOT EXISTS bldg_score_no_int_overlap_idx
        ON bldg_score
        USING gist(attribute_id, int4range(range_min::int, range_max::int, '[)'))
        WHERE data_type = 'integer';
    """
    )
    env.cr.execute(
        """
        DROP INDEX IF EXISTS bldg_score_no_float_overlap_idx;
        CREATE INDEX IF NOT EXISTS bldg_score_no_float_overlap_idx
        ON bldg_score
        USING gist(attribute_id, numrange(range_min, range_max, '[)'))
        WHERE data_type = 'float';
    """
    )


def pre_init_hook(env):
    """Create the PostgreSQL extension before any table is created."""
    env.cr.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")


def post_init_hook(env):
    """Main post-install hook that runs all initialization tasks"""
    try:
        assign_capitals(env)
        create_gist_indexes(env)
    except Exception as e:
        _logger.error("Post-init hook failed: %s", str(e), exc_info=True)
        raise
