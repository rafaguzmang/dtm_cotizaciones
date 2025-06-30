from email.policy import default

from odoo import fields, models, api
from datetime import datetime

from pkg_resources import require


class Encuetas(models.Model):
    _name = 'dtm.cotizaciones.encuesta'
    _description = 'Modelo para llevar el registro de las encuestas telefónicas'
    _rec_name = "mes"

    mes = fields.Char(string="Mes",readonly=True)
    ano = fields.Char(string="Año",readonly=True)

    clientes_id = fields.One2many('dtm.cotizaciones.encuest.empresas', 'model_id', string='Encuestas')

    def get_view(self, view_id=None, view_type='form', **options):
        res = super(Encuetas, self).get_view(view_id, view_type, **options)
        if view_type == 'tree':
            get_this = self.env['dtm.cotizaciones.encuesta'].search([('mes','=',str(datetime.today().strftime("%B")).capitalize()),('ano','=',str(datetime.today().strftime("%Y")))])
            if not get_this:
                self.env['dtm.cotizaciones.encuesta'].create({'mes':str(datetime.today().strftime("%B")).capitalize(),'ano':str(datetime.today().strftime("%Y"))})


        return res

class Empresas(models.Model):
    _name = 'dtm.cotizaciones.encuest.empresas'
    _description = 'Modelo para llevar el registro de la satisfacción de los clientes'


    model_id = fields.Many2one('dtm.cotizaciones.encuesta')

    empresa = fields.Many2one("res.partner",string="Cliente", readonly=False, required=True)
    responde = fields.Char(string="Persona que responde", require=True)
    fecha = fields.Date(string="Fechas de la Compra/Servicio", require=True)

    pregunta1 = fields.Selection(string="¿Como calificaría la calidad general de los productos adquiridos?",
                                 selection=[('1', 'Nada de Acuerdo'), ('2', 'En Desacuerdo'), ('3', 'Indiferente'),
                                            ('4', 'De Acuerdo'), ('5', 'Muy de Acuerdo')],default='5')
    pregunta2 = fields.Selection(string="¿Hubo algún defecto en los productos entregados?",
                                 selection=[('1', 'Nada de Acuerdo'), ('2', 'En Desacuerdo'), ('3', 'Indiferente'),
                                            ('4', 'De Acuerdo'), ('5', 'Muy de Acuerdo')],default='5')
    pregunta3 = fields.Selection(string="¿Cómo calificaría el tiempo de entrega del producto?",
                                 selection=[('1', 'Nada de Acuerdo'), ('2', 'En Desacuerdo'), ('3', 'Indiferente'),
                                            ('4', 'De Acuerdo'), ('5', 'Muy de Acuerdo')],default='5')
    pregunta4 = fields.Selection(string="¿Se cumplió con la fecha de entrega acordada?",
                                 selection=[('1', 'Nada de Acuerdo'), ('2', 'En Desacuerdo'), ('3', 'Indiferente'),
                                            ('4', 'De Acuerdo'), ('5', 'Muy de Acuerdo')],default='5')
    pregunta5 = fields.Selection(string="¿Cómo calificaría la atención del personal de ventas?",
                                 selection=[('1', 'Nada de Acuerdo'), ('2', 'En Desacuerdo'), ('3', 'Indiferente'),
                                            ('4', 'De Acuerdo'), ('5', 'Muy de Acuerdo')],default='5')
    pregunta6 = fields.Selection(string="Cómo calificaría la relación calidad precio de los productos?",
                                 selection=[('1', 'Nada de Acuerdo'), ('2', 'En Desacuerdo'), ('3', 'Indiferente'),
                                            ('4', 'De Acuerdo'), ('5', 'Muy de Acuerdo')],default='5')
    pregunta7 = fields.Selection(string="¿Considera que el precio de los productos es competitivo en el mercado?",
                                 selection=[('1', 'Nada de Acuerdo'), ('2', 'En Desacuerdo'), ('3', 'Indiferente'),
                                            ('4', 'De Acuerdo'), ('5', 'Muy de Acuerdo')],default='5')
    pregunta8 = fields.Selection(string="¿Recomendaría nuestros productos/servicios a otros clientes?",
                                 selection=[('1', 'Nada de Acuerdo'), ('2', 'En Desacuerdo'), ('3', 'Indiferente'),
                                            ('4', 'De Acuerdo'), ('5', 'Muy de Acuerdo')],default='5')
    comentarios = fields.Text(string='Comentarios Adicionales')

