# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import models
from odoo.tools import ormcache
from odoo.tools.mail import plaintext2html

from odoo.addons.base_external_dbsource_importer.models.base_external_dbsource import (
    BaseExternalModelImporter,
)

_logger = logging.getLogger(__name__)

# noqa: F601
MAP_STATES = {
    "BARCELONA": "Barcelona",  # noqa: F601
    "A CORU¥A": "A Coruña (La Coruña)",
    "SEVILLA": "Sevilla",
    "LLEIDA": "Lleida (Lérida)",
    "LAS PALMAS": "Las Palmas",
    "STA.C. TENERIFE": "Santa Cruz de Tenerife",
    "MALAGA": "Málaga",
    "CADIZ": "Cádiz",  # noqa: F601
    "TARRAGONA": "Tarragona",
    "MADRID": "Madrid",
    "ALMERIA": "Almería",
    "VALENCIA": "València (Valencia)",
    "ZARAGOZA": "Zaragoza",
    "BARCELONA": "Barcelona",  # noqa: F601
    "CASTELLON": "Castelló (Castellón)",
    "BALEARES": "Illes Balears (Islas Baleares)",
    "CACERES": "Cáceres",
    "HUESCA": "Huesca",
    "GIRONA": "Girona (Gerona)",
    "VALLADOLID": "Valladolid",
    "CADIZ": "Cádiz",  # noqa: F601
    "Barcelona": "Barcelona",  # noqa: F601
    "BORGES BLANQUES (LES": "Lleida (Lérida)",
    "PRAT DE LLOBREGAT (E": "Barcelona",
    "MATARÓ": "Barcelona",  # noqa: F601
    "Mataró ": "Barcelona",  # noqa: F601
    "BADALONA": "Barcelona",  # noqa: F601
    "Badalona": "Barcelona",  # noqa: F601
}


def str2capitalize(text):
    return text.capitalize() if text else text


def str2title(text):
    return text.title() if text else text


class BaseExternalModelImporterBOne(BaseExternalModelImporter):
    _external_key = "a3_key"

    def execute_query(self, sql, params, metadata=True):
        return self.dbsource.execute_mssql(sql, params, metadata)


class BaseExternalDbsourceBOne(models.Model):
    """It provides logic for connection to a MsSQL data source."""

    _inherit = "base.external.dbsource"

    @property
    def importer(self):
        return BaseExternalModelImporterBOne(dbsource=self)

    @ormcache("value")
    def get_country(self, value):
        return self.env["res.country"].search([("code", "=", value)]).id

    @ormcache("value")
    def get_partner_by_code(self, value):
        return (
            self.env["res.partner"]
            .with_context(active_test=False)
            .search([("a3_key", "=", value)])
        )

    @ormcache("value")
    def get_partner_bank_id(self, value):
        return self.env["res.partner.bank"].search(
            [("partner_id", "=", value)], limit=1
        )

    @ormcache("value")
    def get_user_id_by_code(self, value):
        return self.env["res.users"].search([("a3_key", "=", value)]).id

    @ormcache("value")
    def get_bank_id_by_code(self, value):
        return self.env["res.bank"].search([("code", "=", value)]).id

    @ormcache("value")
    def get_state_id_by_name(self, value):
        return self.env["res.country.state"].search([("name", "=", value)]).id

    def _prepare_customer_address(self, numero, escalera, piso, puerta):
        street2 = ""
        if numero:
            street2 += "Nro: " + numero + " "
        if escalera:
            street2 += "Escalera: " + escalera + " "
        if piso:
            street2 += "Piso: " + piso + " "
        if puerta:
            street2 += "Puerta: " + puerta + " "
        return street2.strip()

    def _prepare_customer_delivery_address(self, row):
        partner = self.get_partner_by_code(row.CODIGO)
        vals = {
            "name": partner.name + "- Dir entrega",
            "type": "delivery",
            "parent_id": partner.id,
            "street": str2capitalize(row.VIA_PUBLICA_ENV)
            if row.VIA_PUBLICA_ENV
            else "",
            "street2": self._prepare_customer_address(
                row.NUMERO_ENV.strip(),
                row.ESCALERA_ENV.strip(),
                row.PISO_ENV.strip(),
                row.PUERTA_ENV.strip(),
            ),
            "a3_key": row.CODIGO + "DE",
            "city": str2capitalize(row.MUNICIPIO_ENV) if row.MUNICIPIO_ENV else "",
            "state_id": self.get_state_id_by_name(
                MAP_STATES.get(row.PROVINCIA_ENV.strip(), "")
            )
            if row.PROVINCIA_ENV.strip() in MAP_STATES
            else False,
            "zip": row.CODIGO_POSTAL_ENV,
            "phone": row.TELEFONO_1_ENV,
            "active": partner.active,
        }
        return vals

    def _prepare_customer_data_bone(  # noqa: C901
        self, row, partner, a3_partners=False
    ):
        is_company = True if row.TIPO_PERSONA == "J" else False
        user_id = self.get_user_id_by_code(row.COD_RESPONSABLE)
        vals = {
            "ref": row.CODIGO,
            "street": str2capitalize(row.VIA_PUBLICA_FIS)
            if row.VIA_PUBLICA_FIS
            else "",
            "street2": self._prepare_customer_address(
                row.NUMERO_FIS.strip(),
                row.ESCALERA_FIS.strip(),
                row.PISO_FIS.strip(),
                row.PUERTA_FIS.strip(),
            ),
            "city": str2capitalize(row.MUNICIPIO_FIS) if row.MUNICIPIO_FIS else "",
            "state_id": self.get_state_id_by_name(
                MAP_STATES.get(row.PROVINCIA_FIS.strip(), "")
            )
            if row.PROVINCIA_FIS.strip() in MAP_STATES
            else False,
            "zip": row.CODIGO_POSTAL_FIS,
            "name": row.RAZON_SOCIAL.strip(),
            "is_company": is_company,
            "vat": row.NIF,
            "customer_rank": 1,
            "email": row.E_MAIL,
            "comment": plaintext2html(row.OBSERVACIONES),
            "lang": "es_ES",
            "country_id": self.env.ref("base.es").id,
            "a3_key": row.CODIGO,
            "phone": row.TELEFONO_FIS,
            "registration_date": row.FECHA_ALTA,
            "cancellation_date": row.FECHA_BAJA,
            "cnae_code": row.CODIGO_CNAE,
            "user_id": user_id,
            "active": False if row.FECHA_BAJA else True,
            "property_payment_term_id": self.importer.get_m2_odoo_id(
                "account.payment.term", row.FORMA_PAGO
            ),
        }
        vals = self._validate_vat(vals, self.env.ref("base.es").code)
        return vals

    def _update_vals_customer_data_bone(self, record, vals_orig):
        vals = {}
        fields_to_update = self.fields_to_update_ids.filtered(
            lambda x: x.model_id.model == "res.partner"
        ).mapped("field_ids.name")
        for k, v in vals_orig.items():
            if not record[k] or k in fields_to_update:
                vals[k] = v
        vals.update(
            {
                "a3_key": record.a3_key,
                "phone": "/".join(filter(None, {record.phone, vals_orig["phone"]})),
                "email": ",".join(filter(None, {record.email, vals_orig["email"]})),
                "comment": plaintext2html(
                    "\n".join(filter(None, {record.comment, vals_orig["comment"]}))
                ),
            }
        )
        return vals

    def _prepare_payment_term_data_bone(self, row):
        vals = {
            "a3_key": row.CODIGO,
            "name": row.DESCRIPCION,
        }
        return vals

    def action_import_payment_term_bone(self):
        importer = BaseExternalModelImporterBOne(dbsource=self)
        fields_sql = """
            o.CODIGO, o.DESCRIPCION
        """
        table_name = """
            dbo.GES_TABLA_FORMAS_PAGO o
        """
        ext_records, records, records_dic = importer.load_data(
            "account.payment.term", table_name, fields=fields_sql
        )
        for ext_rec in ext_records:
            vals = self._prepare_payment_term_data_bone(ext_rec)
            importer.upsert(vals["a3_key"], records, records_dic, vals)

    def action_import_customer_bone(self):
        fields_sql = """gc.RAZON_SOCIAL,gc.NIF,gc.CODIGO,gc.TIPO_PERSONA,gc.E_MAIL,
        gc.OBSERVACIONES,gc.FORMA_PAGO, gc.CODIGO_POSTAL_FIS,gc.VIA_PUBLICA_FIS,
        gc.NUMERO_FIS,gc.ESCALERA_FIS,gc.PISO_FIS,gc.PUERTA_FIS,
        gc.MUNICIPIO_FIS,gc.PROVINCIA_FIS,gc.TELEFONO_FIS,
        gc.FECHA_ALTA,gc.FECHA_BAJA,gc.CODIGO_CNAE,gc.COD_RESPONSABLE"""
        table = "dbo.GES_CLIENTES gc"
        a3_partners = (
            self.env["res.partner"]
            .with_context(active_test=False)
            .search(
                [
                    ("vat", "!=", False),
                    ("a3_key", "=", False),
                ]
            )
        )
        PartnerMapped = self.env["res.partner.mapped"]
        mapped_records = PartnerMapped.search([])
        mapped_dic = {c.a3_key: c.mapped_key for c in mapped_records}
        ext_records, records, records_dic = self.importer.load_data(
            "res.partner",
            table,
            fields=fields_sql.strip(),
            where="",
            load_all_odoo_records=True,
        )
        records_to_nif = records.filtered(lambda p: p.vat and not p.parent_id)
        nif_dic = {c.vat: c for c in records_to_nif.sorted(lambda p: (p.active, p.id))}
        for ext_rec in ext_records:
            _logger.info(f"Import partner: {ext_rec.CODIGO}")
            partner = False
            if ext_rec.CODIGO:
                partner = records.filtered(lambda p, er=ext_rec: p.a3_key == er.CODIGO)[
                    :1
                ]
            if not partner:
                vals = self._prepare_customer_data_bone(
                    ext_rec, False, a3_partners=a3_partners
                )
                partner = self.importer.upsert(
                    vals["a3_key"], records, records_dic, vals
                )
                records |= partner
                if ext_rec.CODIGO:
                    nif_dic[ext_rec.CODIGO] = partner
            if partner:
                ext_rec_a3_key = ext_rec.CODIGO
                if ext_rec_a3_key not in mapped_dic:
                    PartnerMapped.create(
                        {
                            "partner_id": partner.id,
                            "mapped_key": partner.id,
                            "a3_key": ext_rec_a3_key,
                        }
                    )
                    mapped_dic[ext_rec_a3_key] = partner.a3_key

    def action_import_delivery_bone(self):
        fields_sql = """gc.CODIGO,
        gc.VIA_PUBLICA_ENV,gc.NUMERO_ENV,gc.ESCALERA_ENV,gc.PISO_ENV,gc.PUERTA_ENV,gc.MUNICIPIO_ENV,
        gc.PROVINCIA_ENV,gc.TELEFONO_1_ENV,gc.CODIGO_POSTAL_ENV"""
        table = "dbo.GES_CLIENTES gc"
        where = "WHERE gc.VIA_PUBLICA_ENV is not null"
        ext_records, records, records_dic = self.importer.load_data(
            "res.partner", table, fields=fields_sql, where=where
        )
        for ext_rec in ext_records:
            vals = self._prepare_customer_delivery_address(ext_rec)
            self.importer.upsert(vals["a3_key"], records, records_dic, vals)

    def _prepare_supplier_data_bone(  # noqa: C901
        self, row, partner, a3_partners=False
    ):
        city = row.POBPRO.strip() if row.POBPRO else ""
        country_id = self.get_country(row.CODPAIS.strip()) if row.CODPAIS else False
        vals = {
            "ref": row.CODPRO if row.CODPRO != "0" else row.IDPROVEEDOR,
            "street": str2capitalize(row.DIRPRO.strip()) if row.DIRPRO else "",
            "city": str2capitalize(city),
            "state_id": self.get_state_id_by_name(MAP_STATES.get(city, "")),
            "name": row.RAZON,
            "is_company": True,
            "vat": row.NIFPRO,
            "supplier_rank": 1,
            "email": row.E_MAIL,
            "lang": "es_ES",
            "comment": plaintext2html(row.OBSERVACIONES),
            "country_id": country_id,
            "a3_key": row.CODPRO if row.CODPRO != "0" else row.IDPROVEEDOR,
            "phone": row.TELPRO,
            "property_supplier_payment_term_id": self.importer.get_m2_odoo_id(
                "account.payment.term", row.IDFORPAG
            ),
        }
        vals = self._validate_vat(vals, self.env["res.country"].browse(country_id).code)
        return vals

    def action_import_supplier_bone(self):
        fields_sql = """
            ep.IDPROVEEDOR,ep.CODPRO,ep.NIFPRO,ep.RAZON,ep.DIRPRO,ep.POBPRO,ep.TELPRO,ep.E_MAIL,
            ep.CODPAIS,ep.IDFORPAG,ep.OBSERVACIONES
        """
        table = "dbo.ERP_PROVEEDORES ep"
        a3_partners = (
            self.env["res.partner"]
            .with_context(active_test=False)
            .search(
                [
                    ("vat", "!=", False),
                    ("a3_key", "=", False),
                ]
            )
        )
        PartnerMapped = self.env["res.partner.mapped"]
        mapped_records = PartnerMapped.search([])
        mapped_dic = {c.a3_key: c.mapped_key for c in mapped_records}
        ext_records, records, records_dic = self.importer.load_data(
            "res.partner",
            table,
            fields=fields_sql.strip(),
            where="",
            load_all_odoo_records=True,
        )
        records_to_nif = records.filtered(lambda p: p.vat and not p.parent_id)
        nif_dic = {c.vat: c for c in records_to_nif.sorted(lambda p: (p.active, p.id))}
        for ext_rec in ext_records:
            _logger.info(f"Import partner: {ext_rec.CODPRO}")
            partner = False
            codigo = ext_rec.CODPRO if ext_rec != "0" else ext_rec.IDPROVEEDOR
            if codigo:
                partner = records.filtered(lambda p, er=ext_rec: p.a3_key == codigo)[:1]  # noqa: B023
            if not partner:
                vals = self._prepare_supplier_data_bone(
                    ext_rec, False, a3_partners=a3_partners
                )
                partner = self.importer.upsert(
                    vals["a3_key"], records, records_dic, vals
                )
                records |= partner
                if codigo:
                    nif_dic[codigo] = partner
            if partner:
                ext_rec_a3_key = codigo
                if ext_rec_a3_key not in mapped_dic:
                    PartnerMapped.create(
                        {
                            "partner_id": partner.id,
                            "mapped_key": partner.id,
                            "a3_key": ext_rec_a3_key,
                        }
                    )
                    mapped_dic[ext_rec_a3_key] = partner.a3_key

    def _prepare_res_users_data_bone(self, row):
        vals = {
            "a3_key": row.CODIGO,
            "name": row.NOMBRE,
            "login": row.NOMBRE,
            "lang": "es_ES",
        }
        return vals

    def action_import_users_bone(self):
        importer = BaseExternalModelImporterBOne(dbsource=self)
        fields_sql = """
            gtr.CODIGO, gtr.NOMBRE
        """
        table_name = """
            dbo.GES_TABLA_RESPONSABLES gtr
        """
        ext_records, records, records_dic = importer.load_data(
            "res.users", table_name, fields=fields_sql
        )
        for ext_rec in ext_records:
            user = records.search([("name", "ilike", ext_rec.NOMBRE)], limit=1)
            vals = self._prepare_res_users_data_bone(ext_rec)
            if user:
                user.a3_key = vals["a3_key"]
                continue
            _logger.info("USUSARIO: {} - {}".format(vals["login"], vals.get("name")))
            self.importer.upsert(vals["a3_key"], records, records_dic, vals)

    def _prepare_category_data_bone(self, row):
        vals = {
            "a3_key": row.CODIGO_SECCIONSTD,
            "name": row.NOMBRE_SECCIONSTD,
        }
        return vals

    def action_import_product_category_bone(self):
        importer = BaseExternalModelImporterBOne(dbsource=self)
        fields_sql = """
             gss.CODIGO_SECCIONSTD, gss.NOMBRE_SECCIONSTD
        """
        table = """
            dbo.GES_SECCION_STD gss
        """
        ext_records, records, records_dic = importer.load_data(
            "product.category", table, fields=fields_sql
        )
        for ext_rec in ext_records:
            category = records.search(
                [("name", "=", ext_rec.NOMBRE_SECCIONSTD)], limit=1
            )
            vals = self._prepare_category_data_bone(ext_rec)
            if category:
                category.a3_key = vals["a3_key"]
                continue
            self.importer.upsert(vals["a3_key"], records, records_dic, vals)

    def _prepare_product_data_bone(self, row):
        vals = {
            "a3_key": row.CODIGO,
            "name": row.DESCRIPCION,
            "detailed_type": "service",
            "default_code": row.CODIGO,
            "list_price": row.IMPORTE,
            "sale_ok": 1,
            "purchase_ok": 1,
            "categ_id": self.env.ref("product.product_category_all").id,
        }
        return vals

    def action_import_product_bone(self):
        importer = BaseExternalModelImporterBOne(dbsource=self)
        fields_sql = """
             c.CODIGO, c.DESCRIPCION, gt.IMPORTE
        """
        table = """
            dbo.GES_TABLA_CONCEPTOS_FRA c, GES_TARIFAS gt
        """
        where = """
            WHERE c.CODIGO = gt.CODIGO_CONCEPTO
        """
        ext_records, records, records_dic = importer.load_data(
            "product.product", table, fields=fields_sql, where=where
        )
        for ext_rec in ext_records:
            category = records.search([("default_code", "=", ext_rec.CODIGO)], limit=1)
            vals = self._prepare_product_data_bone(ext_rec)
            if category:
                category.a3_key = vals["a3_key"]
                continue
            self.importer.upsert(vals["a3_key"], records, records_dic, vals)

    def _prepare_partner_bank_data_bone(self, partner, bank, acc_number):
        vals = {
            "bank_id": bank,
            "acc_number": acc_number,
            "partner_id": partner.commercial_partner_id.id,
            "a3_key": str(bank) + acc_number,
            "company_id": False,
        }
        return vals

    def format_number_bank_code(self, bank_code):
        bank_code = int(bank_code)
        return str(bank_code).zfill(4)

    def action_import_partner_bank_bone(self):
        fields_sql = """
            c.CODIGO, c.COD_BANCO_1, c.COD_AGENCIA_1, c.DIGITO_CTA_1, c.CTA_CORRIENTE_1,
            c.COD_BANCO_2, c.COD_AGENCIA_2, c.DIGITO_CTA_2, c.CTA_CORRIENTE_2
        """
        table = """
            dbo.GES_CLIENTES c
        """
        where = """
            WHERE c.COD_BANCO_1 is not null or c.COD_BANCO_2 is not null
        """
        ext_records, records, records_dic = self.importer.load_data(
            "res.partner.bank", table, fields=fields_sql, where=where
        )

        for ext_rec in ext_records:
            partner = self.get_partner_by_code(ext_rec.CODIGO)
            if ext_rec.COD_BANCO_1:
                format_bank = self.format_number_bank_code(ext_rec.COD_BANCO_1)
                bank = self.get_bank_id_by_code(format_bank)
                if bank:
                    vals = self._prepare_partner_bank_data_bone(
                        partner, bank, ext_rec.CTA_CORRIENTE_1
                    )
                    if not vals.get("partner_id", False):
                        continue
                    _logger.info(f"Importing res.partner.bank values: {vals}")
                    bank1 = self.importer.upsert(
                        vals["a3_key"], records, records_dic, vals
                    )
                    bank1._onchange_acc_number_base_bank_from_iban()
            if ext_rec.COD_BANCO_2:
                format_bank = self.format_number_bank_code(ext_rec.COD_BANCO_2)
                bank = self.get_bank_id_by_code(format_bank)
                if bank:
                    vals = self._prepare_partner_bank_data_bone(
                        partner, bank, ext_rec.CTA_CORRIENTE_2
                    )
                    if not vals.get("partner_id", False):
                        continue
                    _logger.info(f"Importing res.partner.bank 2 values: {vals}")
                    bank2 = self.importer.upsert(
                        vals["a3_key"], records, records_dic, vals
                    )
                    bank2._onchange_acc_number_base_bank_from_iban()

    def _prepare_partner_bank_mandate(self, row, partner, partner_bank_id):
        vals = {
            "unique_mandate_reference": row.COD_MANDATO.strip(),
            "format": "sepa",
            "partner_id": partner.id,
            "company_id": 1,
            "partner_bank_id": partner_bank_id.id,
            "type": "recurrent" if row.SECUENCIA == "RCUR" else "oneoff",
            "signature_date": row.FECHA_MANDATO,
            "scheme": row.MOD_ADEUDO.strip(),
            "a3_key": row.COD_MANDATO.strip(),
            "state": "valid",
        }
        return vals

    def action_import_res_company_bone(self):
        fields_sql = """
            SELECT * FROM
        """
        table = """
            dbo.GES_EMPRESAS ge
        """
        where = """
            WHERE c.COD_MANDATO is not null and c.COD_BANCO_1 <> 0
        """
        ext_records, records, records_dic = self.importer.load_data(
            "account.banking.mandate", table, fields=fields_sql, where=where
        )

        for ext_rec in ext_records:
            partner = self.get_partner_by_code(ext_rec.CODIGO)
            partner_bank_id = self.get_partner_bank_id(partner.id)
            if partner_bank_id:
                vals = self._prepare_partner_bank_mandate(
                    ext_rec, partner, partner_bank_id
                )
                mandate = self.importer.upsert(
                    vals["a3_key"], records, records_dic, vals
                )
                _logger.info(f"Importing account.banking.mandate values: {mandate}")

    def action_import_partner_bank_mandate_bone(self):
        fields_sql = """
            c.CODIGO, c.COD_MANDATO, c.FECHA_MANDATO,
            c.MOD_ADEUDO, c.SECUENCIA, COD_BANCO_1
        """
        table = """
            dbo.GES_CLIENTES c
        """
        where = """
            WHERE c.COD_MANDATO is not null and c.COD_BANCO_1 <> 0
        """
        ext_records, records, records_dic = self.importer.load_data(
            "account.banking.mandate", table, fields=fields_sql, where=where
        )

        for ext_rec in ext_records:
            partner = self.get_partner_by_code(ext_rec.CODIGO)
            partner_bank_id = self.get_partner_bank_id(partner.id)
            if partner_bank_id:
                vals = self._prepare_partner_bank_mandate(
                    ext_rec, partner, partner_bank_id
                )
                mandate = self.importer.upsert(
                    vals["a3_key"], records, records_dic, vals
                )
                _logger.info(f"Importing account.banking.mandate values: {mandate}")
