# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MailMessage(models.Model):
    _inherit = 'mail.message'

    def message_format(self):
        result = super().message_format()
        contract_modification = self.env['ir.model.data'].xmlid_to_res_id(
            'contract.mail_message_subtype_contract_modification'
        )
        for message in result:
            message.update({
                'is_discussion': message['is_discussion'] or (
                    message['subtype_id'] and
                    message['subtype_id'][0] == contract_modification
                )
            })
