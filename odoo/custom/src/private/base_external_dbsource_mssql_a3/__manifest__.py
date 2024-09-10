# Copyright 2024 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Base External Dbsource MsSql A3",
    "summary": "Import data from A3 ERP",
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
        "account",
        "account_banking_mandate",
        "base_external_dbsource_importer",
        "base_external_dbsource_mssql",
        "blegal_custom",
        "contacts",
        "contract",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/base_external_dbsource_view.xml",
        "views/product_views.xml",
        "views/res_users_view.xml",
    ],
}
