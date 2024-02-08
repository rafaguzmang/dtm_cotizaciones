from odoo import fields,api,models

class Graph(models.Model):
    _name = "dtm.client.graph"
    _description = "Modulo para ayudar a graficar"


    nombre = fields.Char(string="Nombre")
    cantidad = fields.Integer(string="Cantidad")
    porcentaje = fields.Float(string="%")
