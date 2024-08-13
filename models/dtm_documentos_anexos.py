from odoo import fields,models

class Documentos(models.Model):
    _name = "dtm.documentos.anexos"
    _description = "Modelo para almacenar archivos"

    documentos = fields.Binary(string="Documentos")
    nombre = fields.Char()
