# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    _logger.info(">> Pre-Migration 12.0.4.0.0")
    cr = env.cr
    openupgrade.logged_query(
        cr,
        """
        DROP TABLE IF EXISTS account_analytic_invoice_line_wizard
        """
    )
    models_to_rename = [
        # Contract Line Wizard
        ('account.analytic.invoice.line.wizard', 'contract.line.wizard'),
        # Abstract Contract
        ('account.abstract.analytic.contract', 'contract.abstract.contract'),
        # Abstract Contract Line
        ('account.abstract.analytic.contract.line',
         'contract.abstract.contract.line'),
        # Contract Line
        ('account.analytic.invoice.line', 'contract.line'),
        # Contract Template
        ('account.analytic.contract', 'contract.template'),
        # Contract Template Line
        ('account.analytic.contract.line', 'contract.template.line'),
    ]
    tables_to_rename = [
        # Contract Template
        ('account_analytic_contract', 'contract_template'),
        # Contract Template Line
        ('account_analytic_contract_line', 'contract_template_line'),
    ]
    xmlids_to_rename = [
        ('contract.account_analytic_cron_for_invoice',
         'contract.contract_cron_for_invoice'),
        ('contract.account_analytic_contract_manager',
         'contract.contract_template_manager'),
        ('contract.account_analytic_contract_user',
         'contract.contract_template_user'),
        ('contract.account_analytic_invoice_line_manager',
         'contract.contract_line_manager'),
        ('contract.account_analytic_invoice_line_user',
         'contract.contract_line_user'),
        ('contract.account_analytic_contract_line_manager',
         'contract.contract_template_line_manager'),
        ('contract.account_analytic_contract_line_user',
         'contract.contract_template_line_user'),
    ]
    openupgrade.rename_models(cr, models_to_rename)
    openupgrade.rename_tables(cr, tables_to_rename)
    openupgrade.rename_xmlids(cr, xmlids_to_rename)
    # A temporary column is needed to avoid breaking the foreign key constraint
    # The temporary column is dropped in the post-migration script
    openupgrade.logged_query(
        cr,
        """
        ALTER TABLE account_invoice_line
        ADD COLUMN contract_line_id_tmp INTEGER
        """
    )
    if openupgrade.column_exists(cr, 'account_invoice_line', 'contract_line_id'):
        openupgrade.logged_query(
            cr,
            """
            UPDATE account_invoice_line
            SET contract_line_id_tmp = contract_line_id
            """
        )
        openupgrade.logged_query(
            cr,
            """
            UPDATE account_invoice_line SET contract_line_id = NULL
            """
        )
    openupgrade.logged_query(
        cr,
        """
        ALTER TABLE account_invoice
        ADD COLUMN old_contract_id_tmp INTEGER
        """
    )
    openupgrade.logged_query(
        cr,
        """
        UPDATE account_invoice
        SET old_contract_id_tmp = contract_id
        """
    )

    if version == '12.0.1.0.0':
        _logger.info("Move contract data to line level")
        openupgrade.logged_query(
            cr,
            """
        ALTER TABLE account_analytic_invoice_line
            ADD COLUMN IF NOT EXISTS recurring_rule_type         VARCHAR(255),
            ADD COLUMN IF NOT EXISTS recurring_invoicing_type    VARCHAR(255),
            ADD COLUMN IF NOT EXISTS recurring_interval          INTEGER,
            ADD COLUMN IF NOT EXISTS recurring_next_date         DATE,
            ADD COLUMN IF NOT EXISTS date_start                  DATE,
            ADD COLUMN IF NOT EXISTS date_end                    DATE
        """,
        )

        openupgrade.logged_query(
            cr,
            """
            UPDATE account_analytic_invoice_line AS contract_line
            SET 
                recurring_rule_type=contract.recurring_rule_type,
                recurring_invoicing_type=contract.recurring_invoicing_type,
                recurring_interval=contract.recurring_interval,
                recurring_next_date=contract.recurring_next_date,
                date_start=contract.date_start,
                date_end=contract.date_end
            FROM 
                account_analytic_account AS contract
            WHERE 
                contract.id=contract_line.analytic_account_id
            """,
        )