from odoo import fields,models


class ContactosAnexos(models.Model):
    _name = "dtm.contactos.anexos"

    name = fields.Char()
    correo = fields.Char()
    telefono = fields.Char()