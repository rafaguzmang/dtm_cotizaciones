from odoo import fields,models


class ContactosAnexos(models.Model):
    _name = "dtm.contactos.anexos"
    _description = "Se almacenan únicamente el nombre de las empresas"

    name = fields.Char()
    correo = fields.Char()
    telefono = fields.Char()
