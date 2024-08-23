# Copyright 2024 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Base External Dbsource A3 Business One",
    "summary": "Import data from A3 Hana Business One",
    "version": "17.0.1.0.0",
    "development_status": "Alpha",
    "category": "Tools",
    "website": "https://github.com/OCA/server-backend",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "external_dependencies": {
        "python": [
            "sqlalchemy",
            "pymssql",
            "xlrd",
        ],
    },
    "depends": [
        "account_banking_mandate",
        "account_banking_sepa_direct_debit",
        "base_external_dbsource_importer",
        "base_external_dbsource_mssql",
        "l10n_es_partner",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/base_external_dbsource.xml",
        "views/base_external_dbsource_view.xml",
    ],
}
