# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.tests import Form
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


class BaseExternalModelImporterA3(BaseExternalModelImporter):
    _external_key = "a3_key"

    def execute_query(self, sql, params, metadata=True):
        return self.dbsource.execute_mssql(sql, params, metadata)


class BaseExternalDbsourceBOne(models.Model):
    """It provides logic for connection to a MsSQL data source."""

    _inherit = "base.external.dbsource"

    def get_a3_companies(self):
        return {
            "G01": self.env["res.company"].browse(9),  # BLEGAL BARCELONA SL
            "G02": self.env["res.company"].browse(
                7
            ),  # CLARIS SERVEIS PER L'EMPRESA, S.L.
            # 'G03': self.env['res.company'].browse(7), # CLARIS
            # 'G04': self.env['res.company'].browse(7), # EMPRESA PRUEBAS SL
            # 'G05': self.env['res.company'].browse(7), #
            # CONS.LEGALS PER L'EMP.MARESME, SL
            "G06": self.env["res.company"].browse(6),  # GESPRAT ASSESSORS EMPRESA SL
            "G07": self.env["res.company"].browse(5),  # ASSESSORS I CONSULTORS MARESME,
            "G08": self.env["res.company"].browse(8),  # INVERSIONES COSTA CARIBE
            "G09": self.env["res.company"].browse(1),  # BGBL GLOBAL, S.L.
        }

    @ormcache("code")
    def get_company_odoo_company_id(self, code):
        a3_companies = self.get_a3_companies()
        return a3_companies[code].id if code in a3_companies else False

    @property
    def importer(self):
        return BaseExternalModelImporterA3(dbsource=self)

    @ormcache("value")
    def get_country(self, value):
        return self.env["res.country"].search([("code", "=", value)]).id

    @ormcache("value")
    def get_partner_bank_id(self, value):
        return self.env["res.partner.bank"].search(
            [("partner_id", "=", value)], limit=1
        )

    @ormcache("value")
    def get_user_id_by_code(self, value):
        return self.env["res.users"].search([("a3_key", "=", f"RES-{value}")]).id

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

    def _prepare_customer_data_a3(  # noqa: C901
        self, row, partner, a3_partners=False
    ):
        zip_code = row.CODIGO_POSTAL_FIS
        if zip_code:
            zip_code = zip_code.zfill(5)
        (
            state_id,
            country_id,
            country_code,
            zip_id,
            city_id,
        ) = self._state_country_from_zip(zip_code, "ES")
        via_publica = str2capitalize(f"{row.SIGLAS_FIS} {row.VIA_PUBLICA_FIS.strip()}")
        street_number = self._prepare_customer_address(
            row.NUMERO_FIS.strip(),
            row.ESCALERA_FIS.strip(),
            row.PISO_FIS.strip(),
            row.PUERTA_FIS.strip(),
        )
        vals = {
            "a3_key": f"{row.CODIGO}",
            "ref": row.CODIGO,
            "street": f"{via_publica} - {street_number}",
            "city": str2capitalize(row.MUNICIPIO_FIS) if row.MUNICIPIO_FIS else "",
            "zip": zip_code,
            "zip_id": zip_id,
            "city_id": city_id,
            "state_id": state_id,
            "country_id": country_id,
            "name": row.RAZON_SOCIAL.strip(),
            "is_company": True if row.TIPO_PERSONA == "J" else False,
            "vat": row.NIF,
            "customer_rank": 1,
            "email": row.E_MAIL,
            "lang": "es_ES",
            "phone": row.TELEFONO_FIS,
            "registration_date": row.FECHA_ALTA,
            "cancellation_date": row.FECHA_BAJA,
            "user_id": self.importer.get_m2_odoo_id(
                "res.users", f"RES-{row.COD_RESPONSABLE}"
            ),
            "active": False if row.FECHA_BAJA else True,
            "property_payment_term_id": self._get_payment_term(
                f"{int(row.FORMA_PAGO)}-{int(row.DIA_PAGO_1)}"
            ),
        }
        vals = self._validate_vat(vals, self.env.ref("base.es").code)
        if row.OBSERVACIONES:
            vals["comment"] = plaintext2html(row.OBSERVACIONES)
        if row.CODIGO_CNAE:
            vals["cnae_code"] = row.CODIGO_CNAE

        return vals

    def action_import_customer_a3(self):
        fields_sql = """
        gc.RAZON_SOCIAL,gc.NIF,gc.CODIGO,gc.TIPO_PERSONA,gc.E_MAIL,
        gc.OBSERVACIONES,gc.FORMA_PAGO, gc.CODIGO_POSTAL_FIS,gc.VIA_PUBLICA_FIS,
        gc.NUMERO_FIS,gc.ESCALERA_FIS,gc.PISO_FIS,gc.PUERTA_FIS,
        gc.MUNICIPIO_FIS,gc.PROVINCIA_FIS,gc.TELEFONO_FIS,
        gc.FECHA_ALTA,gc.FECHA_BAJA,gc.CODIGO_CNAE,gc.COD_RESPONSABLE, gc.SIGLAS_FIS,
        gc.REMESAS, gc.MOD_ADEUDO, gc.SECUENCIA, gc.COD_BANCO_1, gc.DIA_PAGO_1,
        gc.DIA_PAGO_2, gc.DTO_CLIENTE
        """
        table = "dbo.GES_CLIENTES gc"
        where = """
            --WHERE CODIGO = 'G00026'
        """
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
            where=where,
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
                vals = self._prepare_customer_data_a3(
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
            # Set Payment term for every a3 company present in Odoo
            a3_companies_dic = self.get_a3_companies()
            for company in a3_companies_dic.values():
                partner.sudo().with_company(
                    company
                ).property_payment_term_id = self._get_payment_term(
                    f"{int(ext_rec.FORMA_PAGO)}-{int(ext_rec.DIA_PAGO_1)}"
                )
            odoo_companies = self.env["res.company"].sudo().search([])
            for company in odoo_companies:
                payment_mode = "Transfer"
                if ext_rec.REMESAS == "1" and ext_rec.COD_BANCO_1 > 0:
                    if ext_rec.MOD_ADEUDO == "CORE":
                        payment_mode = "SEPA"
                    else:
                        payment_mode = "SEPA-B2B"
                odoo_payment_mode_id = self.sudo().importer.get_m2_odoo_id(
                    "account.payment.mode", f"{company.id}-{payment_mode}"
                )
                partner.sudo().with_company(
                    company
                ).customer_payment_mode_id = odoo_payment_mode_id

    def _prepare_customer_delivery_address(self, row):
        partner_id = self.importer.get_m2_odoo_id("res.partner", f"{row.CODIGO}")
        partner = self.env["res.partner"].browse(partner_id)
        zip_code = row.CODIGO_POSTAL_ENV
        if zip_code:
            zip_code = zip_code.zfill(5)
        (
            state_id,
            country_id,
            country_code,
            zip_id,
            city_id,
        ) = self._state_country_from_zip(zip_code, "ES")
        via_publica = str2capitalize(f"{row.SIGLAS_ENV} {row.VIA_PUBLICA_ENV.strip()}")
        street_number = self._prepare_customer_address(
            row.NUMERO_ENV.strip(),
            row.ESCALERA_ENV.strip(),
            row.PISO_ENV.strip(),
            row.PUERTA_ENV.strip(),
        )
        if not partner:
            _logger.warning(f"Parent partner not found with code {row.CODIGO}")
        vals = {
            "name": partner.name + "- Dir entrega",
            "type": "delivery",
            "parent_id": partner.id,
            "street": f"{via_publica} - {street_number}",
            "a3_key": f"DE-{row.CODIGO}",
            "city": str2capitalize(row.MUNICIPIO_ENV) if row.MUNICIPIO_ENV else "",
            "zip": zip_code,
            "zip_id": zip_id,
            "city_id": city_id,
            "state_id": state_id,
            "country_id": country_id,
            "phone": row.TELEFONO_1_ENV,
            "active": partner.active,
        }
        return vals

    def action_import_delivery_a3(self):
        fields_sql = """gc.CODIGO,
        gc.VIA_PUBLICA_ENV,gc.NUMERO_ENV,gc.ESCALERA_ENV,gc.PISO_ENV,gc.PUERTA_ENV,
        gc.MUNICIPIO_ENV, gc.PROVINCIA_ENV,gc.TELEFONO_1_ENV,gc.CODIGO_POSTAL_ENV,
        gc.SIGLAS_ENV
        """
        table = "dbo.GES_CLIENTES gc"
        where = """
            WHERE gc.VIA_PUBLICA_ENV is not null
                    and (
                        gc.VIA_PUBLICA_ENV <> gc.VIA_PUBLICA_FIS
                        or gc.MUNICIPIO_ENV <> gc.MUNICIPIO_FIS
                        or gc.PROVINCIA_ENV <> gc.PROVINCIA_FIS
                    )
        """
        ext_records, records, records_dic = self.importer.load_data(
            "res.partner", table, fields=fields_sql, where=where
        )
        for ext_rec in ext_records:
            _logger.info(f"Import delivery address: {ext_rec.CODIGO}")
            vals = self._prepare_customer_delivery_address(ext_rec)
            self.importer.upsert(vals["a3_key"], records, records_dic, vals)

    def _prepare_supplier_data_a3_OLD(  # noqa: C901
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

    def action_import_supplier_a3_OLD(self):
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
                vals = self._prepare_supplier_data_a3(
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

    def _prepare_supplier_data_a3(  # noqa: C901
        self, row, partner, a3_partners=False
    ):
        zip_code = row.CODIGOPOSTAL
        if zip_code:
            zip_code = zip_code.zfill(5)
        (
            state_id,
            country_id,
            country_code,
            zip_id,
            city_id,
        ) = self._state_country_from_zip(zip_code, "ES")
        via_publica = str2capitalize(f"{row.DIRECCION.strip()}")
        street_number = self._prepare_customer_address(
            row.NUMERO.strip(),
            row.ESCALERA.strip(),
            row.PISO.strip(),
            row.PUERTA.strip(),
        )

        vals = {
            "a3_key": f"P-{row.CODIGO}",
            "ref": row.CODIGO,
            "street": f"{via_publica} - {street_number}",
            "city": str2capitalize(row.MUNICIPIO) if row.MUNICIPIO else "",
            "zip": zip_code,
            "zip_id": zip_id,
            "city_id": city_id,
            "state_id": state_id,
            "country_id": country_id,
            "name": row.NOMBRE,
            "is_company": True,
            "vat": row.NIF,
            "supplier_rank": 1,
            "email": row.EMAIL,
            "lang": "es_ES",
            "phone": row.TELEFONO,
            # "property_supplier_payment_term_id": self.importer.get_m2_odoo_id(
            #     "account.payment.term", row.IDFORPAG
            # ),
        }
        vals = self._validate_vat(vals, self.env["res.country"].browse(country_id).code)
        return vals

    def action_import_supplier_a3(self):
        fields_sql = """
            ID, CODIGO, T.NIF, NOMBRE, DIRECCION, NUMERO, ESCALERA,
            PISO, PUERTA, PROVINCIA, MUNICIPIO , CODIGOPOSTAL,
            TELEFONO, EMAIL
        """
        table = "dbo.TERCEROS t"
        where = """
                WHERE CODIGO IN (SELECT CODIGOTERCEROS FROM CUENTAS c
                        where (codempresa IN (
                             'E00004'  -- Gesprat
                            ,'E00005' -- Claris
                            ,'E00011' -- BL
                            ,'E00012' -- ACM
                            ,'E00170' -- ICC
                            ,'E00736' -- BGA
                            ,'E00737' -- BGBL
                            ,'E10080' -- CORR
                        )
                and EJERCICIO >= 2020
                and CUENTAMAYOR in ('4000', '4100'))
                or (codempresa = 'E00623' -- GF
                    and ejercicio <= 2023
                    and CUENTAMAYOR in ('4000', '4100')
                    )
                )
        """
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
            where=where,
            load_all_odoo_records=True,
        )
        records_to_nif = records.filtered(lambda p: p.vat and not p.parent_id)
        nif_dic = {c.vat: c for c in records_to_nif.sorted(lambda p: (p.active, p.id))}
        for ext_rec in ext_records:
            _logger.info(f"Import partner: {ext_rec.CODIGO}")
            partner = False
            codigo = ext_rec.CODIGO if ext_rec != "0" else ext_rec.CODIGO
            if codigo:
                partner = records.filtered(lambda p, er=ext_rec: p.a3_key == codigo)[:1]  # noqa: B023
            if not partner:
                vals = self._prepare_supplier_data_a3(
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

    def _prepare_res_users_data_a3(self, row):
        # Ensure that spanish language is installed
        vals = {
            "a3_key": f"RES-{row.CODIGO}",
            "name": row.NOMBRE,
            "login": row.NOMBRE,
            "lang": "es_ES",
        }
        return vals

    def action_import_users_a3(self):
        importer = BaseExternalModelImporterA3(dbsource=self)
        fields_sql = """
            o.CODIGO, o.NOMBRE
        """
        table_name = """
            dbo.GES_TABLA_RESPONSABLES o
        """
        where = """
            where CODIGO <> ''
        """
        ext_records, records, records_dic = importer.load_data(
            "res.users", table_name, fields=fields_sql, where=where
        )
        for ext_rec in ext_records:
            user = records.search([("name", "ilike", ext_rec.NOMBRE)], limit=1)
            vals = self._prepare_res_users_data_a3(ext_rec)
            if user:
                user.a3_key = vals["a3_key"]
                continue
            _logger.info("USUSARIO: {} - {}".format(vals["login"], vals.get("name")))
            user = self.importer.upsert(vals["a3_key"], records, records_dic, vals)
            # Update the partner that Odoo crates automatically
            user.partner_id.a3_key = vals["a3_key"]

    def _prepare_category_data_a3(self, row):
        vals = {
            "a3_key": row.CODIGO_SECCIONSTD,
            "name": row.NOMBRE_SECCIONSTD,
        }
        return vals

    def action_import_product_category_a3(self):
        importer = BaseExternalModelImporterA3(dbsource=self)
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
            vals = self._prepare_category_data_a3(ext_rec)
            if category:
                category.a3_key = vals["a3_key"]
                continue
            self.importer.upsert(vals["a3_key"], records, records_dic, vals)

    def _prepare_product_data_a3(self, row):
        vals = {
            "a3_key": row.CODIGO,
            "name": row.DESCRIPCION.strip(),
            "detailed_type": "service",
            "default_code": row.CODIGO,
            "list_price": row.IMPORTE,
            "sale_ok": 1,
            "purchase_ok": 1,
            "categ_id": self.env.ref("product.product_category_all").id,
        }
        return vals

    def action_import_product_a3(self):
        importer = BaseExternalModelImporterA3(dbsource=self)
        fields_sql = """
             c.CODIGO, c.DESCRIPCION, c.IVA, gt.IMPORTE
        """
        table = """
            dbo.GES_TABLA_CONCEPTOS_FRA c, GES_TARIFAS gt
        """
        where = """
            WHERE c.CODIGO = gt.CODIGO_CONCEPTO
                AND c.CODIGO NOT IN ('CTABL', 'CTABGL', 'CTASUP', 'CTAACM')
                --and c.CODIGO = 'CTABL'
        """
        ext_records, records, records_dic = importer.load_data(
            "product.product", table, fields=fields_sql, where=where
        )
        for ext_rec in ext_records:
            category = records.search([("default_code", "=", ext_rec.CODIGO)], limit=1)
            vals = self._prepare_product_data_a3(ext_rec)
            if category:
                category.a3_key = vals["a3_key"]
                continue
            product = self.importer.upsert(vals["a3_key"], records, records_dic, vals)
            # Set taxes for every company
            a3_companies_dic = self.get_a3_companies()
            tax_list = []
            for company in a3_companies_dic.values():
                if company.id == 8:
                    # INVERSIONES COSTA CARIBE
                    # Todos los productos son exentos de IVA
                    tax_list.append(
                        self.env.ref(
                            f"account.{company.id}_account_tax_template_s_iva_e"
                        ).id
                    )
                    continue
                if ext_rec.IVA == 1:
                    tax_list.append(
                        self.env.ref(
                            f"account.{company.id}_account_tax_template_s_iva21s"
                        ).id
                    )
                if ext_rec.IVA == 0:
                    tax_list.append(
                        self.env.ref(
                            f"account.{company.id}_account_tax_template_s_iva_ns"
                        ).id
                    )
            # This customer does not use variants so we can update the created template
            product.product_tmpl_id.sudo().write(
                {
                    "a3_key": vals["a3_key"],
                    "taxes_id": [(5, 0), (6, 0, tax_list)],
                }
            )

    def _prepare_partner_bank_data_a3(self, row, second_bank, bank, acc_number):
        iban = self.calcularIBAN(acc_number)
        partner_id = self.importer.get_m2_odoo_id("res.partner", f"{row.CODIGO}")
        partner = self.env["res.partner"].browse(partner_id)
        vals = {
            "bank_id": bank,
            "acc_number": iban,
            "partner_id": partner.commercial_partner_id.id,
            "a3_key": f"{row.CODIGO}-{acc_number}",
            "company_id": False,
        }
        return vals

    def format_number_bank_code(self, bank_code):
        bank_code = int(bank_code)
        return str(bank_code).zfill(4)

    def action_import_partner_bank_a3(self):
        fields_sql = """
            c.CODIGO, c.COD_BANCO_1, c.COD_AGENCIA_1, c.DIGITO_CTA_1, c.CTA_CORRIENTE_1,
            c.COD_BANCO_2, c.COD_AGENCIA_2, c.DIGITO_CTA_2, c.CTA_CORRIENTE_2
        """
        table = """
            dbo.GES_CLIENTES c
        """
        where = """
            WHERE (c.COD_BANCO_1 > 0 or c.COD_BANCO_2 > 0)
            --and CODIGO = 'G00031'
        """
        ext_records, records, records_dic = self.importer.load_data(
            "res.partner.bank", table, fields=fields_sql, where=where
        )

        for ext_rec in ext_records:
            if ext_rec.COD_BANCO_1 > 1:
                format_bank = self.format_number_bank_code(ext_rec.COD_BANCO_1)
                format_agencia = self.format_number_bank_code(ext_rec.COD_AGENCIA_1)
                bank_account = (
                    f"{format_bank}{format_agencia}"
                    f"{ext_rec.DIGITO_CTA_1}{ext_rec.CTA_CORRIENTE_1}"
                )
                bank = self.get_bank_id_by_code(format_bank)
                if bank:
                    vals = self._prepare_partner_bank_data_a3(
                        ext_rec, False, bank, bank_account
                    )
                    if not vals.get("partner_id", False):
                        continue
                    _logger.info(f"Importing res.partner.bank values: {vals}")
                    bank1 = self.importer.upsert(
                        vals["a3_key"], records, records_dic, vals
                    )
                    bank1._onchange_acc_number_base_bank_from_iban()
            if (
                ext_rec.COD_BANCO_2 > 0
                and ext_rec.CTA_CORRIENTE_2 != ext_rec.CTA_CORRIENTE_1
            ):
                format_bank = self.format_number_bank_code(ext_rec.COD_BANCO_2)
                format_agencia = self.format_number_bank_code(ext_rec.COD_AGENCIA_2)
                bank_account = (
                    f"{format_bank}{format_agencia}"
                    f"{ext_rec.DIGITO_CTA_2}{ext_rec.CTA_CORRIENTE_2}"
                )
                bank = self.get_bank_id_by_code(format_bank)
                if bank:
                    vals = self._prepare_partner_bank_data_a3(
                        ext_rec, True, bank, bank_account
                    )
                    if not vals.get("partner_id", False):
                        continue
                    _logger.info(f"Importing res.partner.bank 2 values: {vals}")
                    bank2 = self.importer.upsert(
                        vals["a3_key"], records, records_dic, vals
                    )
                    bank2._onchange_acc_number_base_bank_from_iban()

    def _prepare_partner_bank_mandate(self, row, bank_account):
        vals = {
            "unique_mandate_reference": row.COD_MANDATO.strip(),
            "format": "sepa",
            "company_id": 1,
            "partner_bank_id": self.importer.get_m2_odoo_id(
                "res.partner.bank", f"{row.CODIGO}-{bank_account}"
            ),
            "signature_date": row.FECHA_MANDATO,
            "scheme": row.MOD_ADEUDO.strip(),
            "a3_key": row.COD_MANDATO.strip(),
            "state": "valid",
            "type": "recurrent",
            "last_debit_date": fields.Date.today(),
        }
        if row.SECUENCIA == "RCUR":
            vals["recurrent_sequence_type"] = "recurring"
        else:
            vals["recurrent_sequence_type"] = "first"
        return vals

    def action_import_partner_bank_mandate_a3(self):
        fields_sql = """
            c.CODIGO, c.COD_MANDATO, c.FECHA_MANDATO,
            c.MOD_ADEUDO, c.SECUENCIA, COD_BANCO_1, COD_AGENCIA_1, DIGITO_CTA_1,
            CTA_CORRIENTE_1
        """
        table = """
            dbo.GES_CLIENTES c
        """
        where = """
            WHERE c.COD_MANDATO is not null and c.COD_BANCO_1 > 0
            --and CODIGO = 'G00032'
        """
        ext_records, records, records_dic = self.importer.load_data(
            "account.banking.mandate", table, fields=fields_sql, where=where
        )

        for ext_rec in ext_records:
            format_bank = self.format_number_bank_code(ext_rec.COD_BANCO_1)
            format_agencia = self.format_number_bank_code(ext_rec.COD_AGENCIA_1)
            bank_account = (
                f"{format_bank}{format_agencia}"
                f"{ext_rec.DIGITO_CTA_1}{ext_rec.CTA_CORRIENTE_1}"
            )
            bank = self.get_bank_id_by_code(format_bank)
            if bank:
                _logger.info(
                    f"Importing account.banking.mandate values: {ext_rec.COD_MANDATO}"
                )
                vals = self._prepare_partner_bank_mandate(ext_rec, bank_account)
                self.importer.upsert(vals["a3_key"], records, records_dic, vals)

    def _prepare_analytic_account_a3(self, row):
        company_id = self.get_company_odoo_company_id(row.COD_EMPRESA)
        partner_id = self.importer.get_m2_odoo_id("res.partner", f"{row.COD_CLIENTE}")
        vals = {
            "a3_key": f"{int(row.COD_EXPEDIENTE)}",
            "company_id": company_id,
            "code": row.CLAVE_EXPEDIENTE.strip(),
            "name": row.TITULO.strip(),
            "partner_id": partner_id,
            "plan_id": self.env.ref("analytic.analytic_plan_projects").id,
        }
        return vals

    def action_import_analytic_account_a3(self):
        fields_sql = """
            COD_EMPRESA, COD_EXPEDIENTE, COD_CLIENTE, EJERCICIO, CLAVE_EXPEDIENTE,
            TITULO, TIPO, COD_RESPONSABLE, COD_COMERCIAL, FECHA_APERTURA, FECHA_CIERRE
        """
        table = """
            dbo.GES_EXPEDIENTES c
        """
        where = """
            WHERE COD_CLIENTE IN (SELECT CODIGO FROM GES_CLIENTES gc)
                AND c.COD_EMPRESA NOT IN ('G03', 'G04', 'G05')
                AND COD_EXPEDIENTE IN (SELECT EXPEDIENTE from GES_CUOTAS)
                --AND CLAVE_EXPEDIENTE = 'C/000063'
                --AND c.COD_EMPRESA = 'G01'
                --AND c.COD_EXPEDIENTE = 3928
                --AND c.COD_EXPEDIENTE = 3911
                --AND c.COD_EXPEDIENTE = 32
        """
        ext_records, records, records_dic = self.sudo().importer.load_data(
            "account.analytic.account", table, fields=fields_sql, where=where
        )

        for ext_rec in ext_records:
            _logger.info(
                f"Importing analytic account values: {int(ext_rec.COD_EXPEDIENTE)}"
            )
            vals = self._prepare_analytic_account_a3(ext_rec)
            self.sudo().importer.upsert(vals["a3_key"], records, records_dic, vals)

    def _prepare_contract_a3(self, row):
        company_id = self.get_company_odoo_company_id(row.COD_EMPRESA)
        company = self.env["res.company"].browse(company_id)
        partner_id = self.importer.get_m2_odoo_id("res.partner", f"{row.COD_CLIENTE}")
        partner = self.env["res.partner"].with_company(company).browse(partner_id)
        fiscal_position = partner.env["account.fiscal.position"]._get_fiscal_position(
            partner
        )
        vals = {
            "a3_key": f"{int(row.COD_EXPEDIENTE)}",
            "company_id": company_id,
            "code": row.CLAVE_EXPEDIENTE.strip(),
            "name": row.TITULO.strip(),
            "partner_id": partner_id,
            "date_start": row.FECHA_APERTURA,
            "date_end": row.FECHA_CIERRE,
            "pricelist_id": partner.property_product_pricelist.id,
            "fiscal_position_id": fiscal_position.id,
            "payment_term_id": partner.property_payment_term_id.id,
            "invoice_partner_id": partner_id,
            "line_recurrence": True,
        }
        return vals

    def action_import_contract_a3(self):
        fields_sql = """
            COD_EMPRESA, COD_EXPEDIENTE, COD_CLIENTE, EJERCICIO, CLAVE_EXPEDIENTE,
            TITULO, TIPO, COD_RESPONSABLE, COD_COMERCIAL, FECHA_APERTURA, FECHA_CIERRE
        """
        table = """
            dbo.GES_EXPEDIENTES c
        """
        where = """
            WHERE COD_CLIENTE IN (SELECT CODIGO FROM GES_CLIENTES gc)
                AND c.COD_EMPRESA NOT IN ('G03', 'G04', 'G05')
                AND COD_EXPEDIENTE IN (SELECT EXPEDIENTE from GES_CUOTAS)
                --AND CLAVE_EXPEDIENTE = 'C/000063'
                --AND c.COD_EMPRESA = 'G01'
                --AND c.COD_EXPEDIENTE = 3928
                --AND c.COD_EXPEDIENTE = 3911
                --AND c.COD_EXPEDIENTE = 32
        """
        ext_records, records, records_dic = self.sudo().importer.load_data(
            "contract.contract", table, fields=fields_sql, where=where
        )

        for ext_rec in ext_records:
            _logger.info(f"Importing contract values: {int(ext_rec.COD_EXPEDIENTE)}")
            vals = self._prepare_contract_a3(ext_rec)
            self.sudo().importer.upsert(vals["a3_key"], records, records_dic, vals)

    def _prepare_contract_line_a3(self, row):
        company_id = self.get_company_odoo_company_id(row.COD_EMPRESA)
        company = self.env["res.company"].browse(company_id)
        product_id = self.importer.get_m2_odoo_id(
            "product.product", f"{row.COD_CONCEPTO_FACT.strip()}"
        )
        product = self.env["product.product"].with_company(company).browse(product_id)
        contract_id = self.with_company(company).importer.get_m2_odoo_id(
            "contract.contract", f"{int(row.EXPEDIENTE)}"
        )
        contract = (
            self.env["contract.contract"].with_company(company).browse(contract_id)
        )
        if row.PERIODO == "S":
            recurring_rule_type = "weekly"
            line_date_start = row.FECHA_PROX_GENERACION - relativedelta(weeks=1)
        elif row.PERIODO == "M":
            recurring_rule_type = "monthly"
            line_date_start = row.FECHA_PROX_GENERACION - relativedelta(months=1)
        elif row.PERIODO == "T":
            recurring_rule_type = "quarterly"
            line_date_start = row.FECHA_PROX_GENERACION - relativedelta(months=3)
        elif row.PERIODO == "C":
            recurring_rule_type = "semesterly"
            line_date_start = row.FECHA_PROX_GENERACION - relativedelta(months=6)
        elif row.PERIODO == "A":
            recurring_rule_type = "yearly"
            line_date_start = row.FECHA_PROX_GENERACION - relativedelta(years=1)
        else:
            recurring_rule_type = "monthly"
            line_date_start = row.FECHA_PROX_GENERACION - relativedelta(months=1)
        line_date_start = fields.Date.from_string(line_date_start)
        vals = {
            "a3_key": f"{int(row.EXPEDIENTE)}-{int(row.NUMERO_ORDEN)}",
            "contract_id": contract_id,
            "product_id": product.id,
            "name": row.DESCRIPCION.strip(),
            "quantity": row.UNIDADES,
            "price_unit": row.IMPORTE,
            "sequence": row.NUMERO_ORDEN,
            "recurring_interval": 1,
            "recurring_rule_type": recurring_rule_type,
            "date_start": line_date_start,
            "date_end": fields.Date.from_string(row.FECHA_FIN_GENERACION),
        }
        vals["last_date_invoiced"] = fields.Date.from_string(
            row.FECHA_PROX_GENERACION
        ) - relativedelta(days=1)
        if row.FECHA_FIN_GENERACION and contract.date_start > fields.Date.from_string(
            row.FECHA_FIN_GENERACION
        ):
            vals["date_end"] = contract.date_start
            vals["last_date_invoiced"] = fields.Date.from_string(
                row.FECHA_FIN_GENERACION
            )
        if vals["date_end"] and vals["date_start"] > vals["date_end"]:
            vals["date_end"] = vals["date_start"]
        if (
            vals["last_date_invoiced"]
            and vals["last_date_invoiced"] < vals["date_start"]
        ):
            vals["last_date_invoiced"] = vals["date_start"]
        if (
            vals["last_date_invoiced"]
            and vals["date_end"]
            and vals["last_date_invoiced"] > vals["date_end"]
        ):
            vals["date_end"] = vals["last_date_invoiced"]
        # Assign analytic distribution
        # distribution_model.analytic_distribution = {f"{test_account.id}": 100}
        analytic_account_id = self.with_company(company).importer.get_m2_odoo_id(
            "account.analytic.account", f"{int(row.EXPEDIENTE)}"
        )
        if analytic_account_id:
            vals["analytic_distribution"] = {f"{analytic_account_id}": 100}
        return vals

    def action_import_contract_line_a3(self):
        fields_sql = """
            EXPEDIENTE, COD_CONCEPTO_FACT, DESCRIPCION, CODIGO_CLIENTE, IMPORTE,
            PERIODO, FECHA_PROX_GENERACION, FECHA_FIN_GENERACION, UNIDADES,
            COD_EMPRESA, NUMERO_ORDEN,
            (SELECT TOP 1 con.FECHA_FACTURA
            	FROM GES_CONCEPTOS con
            	WHERE con.EXPEDIENTE = c.EXPEDIENTE
            	    and con.CODIGO = c.COD_CONCEPTO_FACT
            	    and ES_CUOTA = 'S'
            	ORDER BY con.FECHA_FACTURA DESC
            	) AS ULTIMA_FECHA_FACTURA
        """
        table = """
            dbo.GES_CUOTAS c
        """
        where = """
            WHERE c.CODIGO_CLIENTE IN (SELECT CODIGO FROM GES_CLIENTES gc)
                --AND c.COD_EMPRESA = 'G01'
                AND c.COD_EMPRESA NOT IN ('G03', 'G04', 'G05')
                AND c.COD_CONCEPTO_FACT NOT IN ('CTABL', 'CTABGL', 'CTASUP', 'CTAACM')
                --AND c.EXPEDIENTE = 1359
                --AND c.EXPEDIENTE = 32
                --AND c.COD_CONCEPTO_FACT='CUOFIS'
                --AND c.CODIGO_CLIENTE = 'G00810'
                --AND c.CODIGO_CLIENTE = 'G00818'
            ORDER BY c.COD_EMPRESA, c.EXPEDIENTE, c.NUMERO_ORDEN
        """
        ext_records, records, records_dic = self.sudo().importer.load_data(
            "contract.line", table, fields=fields_sql, where=where
        )

        for ext_rec in ext_records:
            _logger.info(
                f"Importing contract LINE Expediente: {int(ext_rec.EXPEDIENTE)} "
                f"Linea: {int(ext_rec.NUMERO_ORDEN)}"
            )
            vals = self._prepare_contract_line_a3(ext_rec)
            contract_line = self.sudo().importer.upsert(
                vals["a3_key"], records, records_dic, vals
            )
            if contract_line.date_end:
                if contract_line.is_stop_allowed:
                    contract_line.stop(date_end=contract_line.date_end)
                if not contract_line.is_canceled:
                    contract_line.is_canceled = True

    def action_update_mandate_company_from_contract(self):
        mandates = self.env["account.banking.mandate"].sudo().search([])
        contracts = (
            self.env["contract.contract"]
            .sudo()
            .search([("partner_id", "in", mandates.partner_id.ids)])
        )
        for mandate in mandates:
            contract = contracts.filtered(
                lambda ct, m=mandate: ct.partner_id == m.partner_id
            )
            if contract:
                _logger.info(
                    f"Mandate {mandate.unique_mandate_reference} company updated "
                    f"to: {contract[:1].company_id.name}"
                )
                mandate.sudo().company_id = contract[:1].company_id

    def _prepare_sale_order_a3(self, row):
        company_id = self.get_company_odoo_company_id(row.COD_EMPRESA)
        company = self.env["res.company"].browse(company_id)
        partner_id = self.importer.get_m2_odoo_id("res.partner", f"{row.COD_CLIENTE}")
        partner = self.env["res.partner"].with_company(company).browse(partner_id)
        fiscal_position = partner.env["account.fiscal.position"]._get_fiscal_position(
            partner
        )
        vals = {
            "a3_key": f"{int(row.COD_EXPEDIENTE)}",
            "company_id": company_id,
            "analytic_account_id": self.with_company(company).importer.get_m2_odoo_id(
                "account.analytic.account", f"{int(row.COD_EXPEDIENTE)}"
            ),
            "partner_id": partner_id,
            "date_order": row.FECHA_APERTURA,
            "pricelist_id": partner.property_product_pricelist.id,
            "fiscal_position_id": fiscal_position.id,
            "payment_term_id": partner.property_payment_term_id.id,
            "origin": row.CLAVE_EXPEDIENTE.strip(),
            # "tag_ids": [(6, 0, [])]
        }
        return vals

    def action_import_sale_order_from_contract_a3(self):
        fields_sql = """
            COD_EMPRESA, COD_EXPEDIENTE, COD_CLIENTE, EJERCICIO, CLAVE_EXPEDIENTE,
            TITULO, TIPO, COD_RESPONSABLE, COD_COMERCIAL, FECHA_APERTURA, FECHA_CIERRE
        """
        table = """
            dbo.GES_EXPEDIENTES c
        """
        where = """
            WHERE COD_CLIENTE IN (SELECT CODIGO FROM GES_CLIENTES gc)
                AND c.COD_EMPRESA NOT IN ('G03', 'G04', 'G05')
                AND COD_EXPEDIENTE IN (SELECT EXPEDIENTE from GES_CUOTAS)
                --AND CLAVE_EXPEDIENTE = 'C/000063'
                --AND c.COD_EMPRESA = 'G01'
                --AND c.COD_EXPEDIENTE = 3928
                --AND c.COD_EXPEDIENTE = 3911
                --AND c.COD_EXPEDIENTE = 32
        """
        ext_records, records, records_dic = self.sudo().importer.load_data(
            "sale.order", table, fields=fields_sql, where=where
        )

        for ext_rec in ext_records:
            _logger.info(f"Importing sale order values: {int(ext_rec.COD_EXPEDIENTE)}")
            vals = self._prepare_sale_order_a3(ext_rec)
            self.sudo().importer.upsert(vals["a3_key"], records, records_dic, vals)

    def _prepare_sale_order_line_a3(self, row):
        company_id = self.get_company_odoo_company_id(row.COD_EMPRESA)
        company = self.env["res.company"].browse(company_id)
        product_id = self.importer.get_m2_odoo_id(
            "product.product", f"{row.COD_CONCEPTO_FACT.strip()}"
        )
        product = self.env["product.product"].with_company(company).browse(product_id)
        contract_id = self.with_company(company).importer.get_m2_odoo_id(
            "contract.contract", f"{int(row.EXPEDIENTE)}"
        )
        contract_line_id = self.with_company(company).importer.get_m2_odoo_id(
            "contract.line", f"{int(row.EXPEDIENTE)}-{int(row.NUMERO_ORDEN)}"
        )
        sale_order_id = self.with_company(company).importer.get_m2_odoo_id(
            "sale.order", f"{int(row.EXPEDIENTE)}"
        )
        sale_order = self.env["sale.order"].with_company(company).browse(sale_order_id)
        order_form = Form(sale_order)
        with order_form.order_line.new() as sol_form:
            sol_form.product_id = product
            vals = sol_form._get_all_values()
        vals.update(
            {
                "a3_key": f"{int(row.EXPEDIENTE)}-{int(row.NUMERO_ORDEN)}",
                "order_id": sale_order_id,
                "contract_id": contract_id,
                "contract_line_id": contract_line_id,
            }
        )
        # Assign analytic distribution
        # distribution_model.analytic_distribution = {f"{test_account.id}": 100}
        analytic_account_id = self.with_company(company).importer.get_m2_odoo_id(
            "account.analytic.account", f"{int(row.EXPEDIENTE)}"
        )
        if analytic_account_id:
            vals["analytic_distribution"] = {f"{analytic_account_id}": 100}
        return vals

    def action_import_sale_order_line_from_cuotas_a3(self):
        fields_sql = """
            EXPEDIENTE, COD_CONCEPTO_FACT, DESCRIPCION, CODIGO_CLIENTE, IMPORTE,
            PERIODO, FECHA_PROX_GENERACION, FECHA_FIN_GENERACION, UNIDADES,
            COD_EMPRESA, NUMERO_ORDEN,
            (SELECT TOP 1 con.FECHA_FACTURA
            	FROM GES_CONCEPTOS con
            	WHERE con.EXPEDIENTE = c.EXPEDIENTE
            	    and con.CODIGO = c.COD_CONCEPTO_FACT
            	    and ES_CUOTA = 'S'
            	ORDER BY con.FECHA_FACTURA DESC
            	) AS ULTIMA_FECHA_FACTURA
        """
        table = """
            dbo.GES_CUOTAS c
        """
        where = """
            WHERE c.CODIGO_CLIENTE IN (SELECT CODIGO FROM GES_CLIENTES gc)
                --AND c.COD_EMPRESA = 'G01'
                AND c.COD_EMPRESA NOT IN ('G03', 'G04', 'G05')
                AND c.COD_CONCEPTO_FACT NOT IN ('CTABL', 'CTABGL', 'CTASUP', 'CTAACM')
                --AND c.EXPEDIENTE = 1359
                --AND c.EXPEDIENTE = 32
                --AND c.COD_CONCEPTO_FACT='CUOFIS'
                --AND c.CODIGO_CLIENTE = 'G00810'
                --AND c.CODIGO_CLIENTE = 'G00818'
            ORDER BY c.COD_EMPRESA, c.EXPEDIENTE, c.NUMERO_ORDEN
        """
        ext_records, records, records_dic = self.sudo().importer.load_data(
            "sale.order.line", table, fields=fields_sql, where=where
        )

        for ext_rec in ext_records:
            _logger.info(
                f"Importing sale order line from Expediente: {int(ext_rec.EXPEDIENTE)} "
                f"Linea: {int(ext_rec.NUMERO_ORDEN)}"
            )
            vals = self._prepare_sale_order_line_a3(ext_rec)
            self.sudo().importer.upsert(vals["a3_key"], records, records_dic, vals)

    @api.model
    @ormcache("pay_term")
    def _get_payment_term(self, pay_term):
        # Only mapped the records used in origin
        # SELECT * FROM GES_TABLA_FORMAS_PAGO gtfp
        # WHERE CODIGO IN (SELECT gc.FORMA_PAGO FROM GES_CLIENTES gc)
        values = {
            "0-0": self.env.ref("account.account_payment_term_immediate").id,
            "1-0": self.env.ref("account.account_payment_term_immediate").id,
            "1-1": self.env.ref(
                "blegal_custom.account_payment_term_immediate_day_1"
            ).id,
            "1-2": self.env.ref(
                "blegal_custom.account_payment_term_immediate_day_2"
            ).id,
            "1-5": self.env.ref(
                "blegal_custom.account_payment_term_immediate_day_5"
            ).id,
            "1-10": self.env.ref(
                "blegal_custom.account_payment_term_immediate_day_10"
            ).id,
            "1-15": self.env.ref(
                "blegal_custom.account_payment_term_immediate_day_15"
            ).id,
            "1-20": self.env.ref(
                "blegal_custom.account_payment_term_immediate_day_20"
            ).id,
            "1-25": self.env.ref(
                "blegal_custom.account_payment_term_immediate_day_25"
            ).id,
            "1-30": self.env.ref(
                "blegal_custom.account_payment_term_immediate_day_30"
            ).id,
            "5-0": self.env.ref("account.account_payment_term_30days").id,
            "5-1": self.env.ref("blegal_custom.account_payment_term_30days_day_1").id,
            "5-5": self.env.ref("blegal_custom.account_payment_term_30days_day_5").id,
            "5-10": self.env.ref("blegal_custom.account_payment_term_30days_day_10").id,
            "5-20": self.env.ref("blegal_custom.account_payment_term_30days_day_20").id,
            "5-25": self.env.ref("blegal_custom.account_payment_term_30days_day_25").id,
            "5-30": self.env.ref("blegal_custom.account_payment_term_30days_day_30").id,
            "6-0": self.env.ref("blegal_custom.account_payment_term_90days").id,
            "6-25": self.env.ref("blegal_custom.account_payment_term_90days_day_25").id,
            "7-0": self.env.ref("blegal_custom.account_payment_term_end_quarter").id,
            "7-1": self.env.ref(
                "blegal_custom.account_payment_term_end_quarter_day_1"
            ).id,
            "8-0": self.env.ref(
                "blegal_custom.account_payment_term_30_60_90_120_150days"
            ).id,
            "8-30": self.env.ref(
                "blegal_custom.account_payment_term_30_60_90_120_150days_day_30"
            ).id,
        }
        return values[pay_term]

    def calcularIBAN(self, ccc, pais="es"):
        def limpiar(numero):
            return numero.replace("IBAN", "").replace(" ", "").replace("-", "")

        def valorCifras(cifras):
            LETRAS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"  # A=10, B=11, ... Z=35
            items = []
            for cifra in cifras:
                posicion = LETRAS.find(cifra)
                items.append(str(posicion) if posicion >= 0 else "-")
            return "".join(items)

        def modulo(cifras, divisor):
            """
            El entero más grande en Python es 9.223.372.036.854.775.807 (2**63-1)
            que tiene 19 cifras, de las cuales las 18 últimas pueden tomar cualquier
            valor.
            El divisor y el resto tendrán 2 cifras. Por lo tanto CUENTA como tope
            puede ser de 16 cifras (18-2) y como mínimo de 1 cifra.
            """
            CUENTA, resto, i = 13, 0, 0
            while i < len(cifras):
                dividendo = str(resto) + cifras[i : i + CUENTA]
                resto = int(dividendo) % divisor
                i += CUENTA
            return resto

        def cerosIzquierda(cifras, largo):
            cantidad = largo - len(cifras)
            ceros = "0" * cantidad
            return ceros + cifras

        ccc = limpiar(ccc)
        pais = pais.upper()
        cifras = ccc + valorCifras(pais) + "00"
        resto = modulo(cifras, 97)
        return pais + cerosIzquierda(str(98 - resto), 2) + ccc
