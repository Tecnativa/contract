# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductCategory(models.Model):
    """It provides logic for connection to a MsSQL data source."""

    _inherit = ["product.category", "dbsource.a3.mixin"]
    _name = "product.category"


class ProductProduct(models.Model):
    """It provides logic for connection to a MsSQL data source."""

    _inherit = ["product.product", "dbsource.a3.mixin"]
    _name = "product.product"


class ProductTemplate(models.Model):
    """It provides logic for connection to a MsSQL data source."""

    _inherit = ["product.template", "dbsource.a3.mixin"]
    _name = "product.template"

    # User can update the key directly from template because he does not use variants
    # TT50002
    a3_key = fields.Char(related="product_variant_ids.a3_key", readonly=False)
