from odoo import api,models,fields

class Requerimientos(models.Model):
    _name = 'dtm.requerimientos'

    servicio = fields.Char(string='Servicio')
    nombre = fields.Char(string='Nombre')
    cantidad = fields.Integer(string='Cantidad')
    descripcion = fields.Char(string='descripcion')
    material_servicio_id = fields.One2many('dtm.list.material.producto','model_id',string='Material/Servicio')

    anexos_id = fields.Many2many('dtm.documentos.anexos', compute='_compute_fill_anexos')

    def _compute_fill_anexos(self):
        get_id = self.env['cot.list.material'].search([('name','=',self.nombre),('descripcion','=',self.descripcion),('cantidad','=',self.cantidad)])
        lines = []
        lines.append((5,0,{}))
        for result in get_id.attachment_ids:
            print(result.nombre)
            line = (4,result.id,{})
            lines.append(line)
        self.anexos_id = lines    
    
    def action_save(self):
        # print("Button press")
        # print(self.id)
        # print(self.servicio)
        vals = {

            'model': self.id
        }
        self.env['dtm.list.material.producto'].write(vals)
        return {'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'dtm.precotizacion',
                'terget':'new',
                'res_id':self.id
                }

class MaterialServicio(models.Model):
    _name = 'dtm.list.material.producto'

    model_id = fields.Many2one('dtm.requerimientos')
    material_servicio = fields.Selection(strin="Servicio", selection=[('material', 'Material'),('servicio', 'Servicio') ])
    descripcion = fields.Text(string="Descripción")
    cantidad = fields.Integer(string = "Cantidad")
    precio = fields.Float(string = "Precio")


    