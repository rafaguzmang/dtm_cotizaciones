from odoo import api,models, fields


class Herencia(models.Model):
    _inherit = 'dtm.client.needs'

    no_cotizacion = fields.Char(readonly=True) 

    cliente_ids = fields.Many2one(readonly=True)

    atencion = fields.Many2many(readonly=True)

    date = fields.Date(readonly=True)   

    attachment_ids = fields.Many2many(readonly=True)

    #list_materials_ids = fields.One2many(readonly=True)

class OtraHerencia(models.Model):
    _inherit = 'cot.list.material'

    name = fields.Char(readonly=True)
    descripcion = fields.Text(readonly=True)
    cantidad = fields.Integer(readonly=True)
    attachment_ids = fields.Many2many(readonly=True)
    #material_serv_ids = fields.Many2many(readonly=False)

    #prueba = fields.Char(string='Esta es una prueba')

   

    
    