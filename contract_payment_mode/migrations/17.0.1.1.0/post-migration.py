# Copyright 2026 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

MAPPING_TABLE = "ilex_payment_mode_map"


def _migrate_contract_payment_modes(env):
    """Populate contract payment modes from the preserved values."""
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE contract_contract AS contract
        SET payment_mode_id = mapping.account_payment_mode_id
        FROM {MAPPING_TABLE} AS mapping
        WHERE contract.old_payment_mode_id = mapping.payment_mode_id
          AND contract.payment_mode_id IS NULL
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _migrate_contract_payment_modes(env)
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "contract_payment_mode.inherit_contract_contract_payment_mode",
        ],
    )
