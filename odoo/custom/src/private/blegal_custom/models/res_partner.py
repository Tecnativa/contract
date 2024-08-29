from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    registration_date = fields.Datetime(copy=False, tracking=True)
    cancellation_date = fields.Datetime(copy=False, tracking=True)
    cnae_code = fields.Char(copy=False, tracking=True)
