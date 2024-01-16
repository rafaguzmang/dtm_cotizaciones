from odoo import api,models,fields

class Requerimientos(models.Model):
    _name = 'dtm.requerimientos'
    _description = "Muestra los requerimientos del cliente para cotizar servicios"

    servicio = fields.Char(string='Servicio')

    nombre = fields.Char(string='Nombre')
    descripcion = fields.Char(string='Descripcion')
    cantidad = fields.Integer(string='Cantidad')
    #-----------------------------------------------------------------------------------------------------

    material_servicio_id = fields.One2many('dtm.list.material.producto','model_id',readonly=False)
    precio_unitario = fields.Float(string="Precio Unitario")
    precio_total = fields.Float(string="Precio Total")
    anexos_id = fields.Many2many('dtm.documentos.anexos', compute='_compute_fill_anexos')
    suma_total = fields.Float(string="TOTAL")

    # @api.depends("suma_total")
    # def _compute_presio_unitario(self):
    #     for result in self:
    #         print(result)

    def action_sumar(self):
        print(self.id)
        print(self.material_servicio_id)
        sum = 0
        for result in self.material_servicio_id:
            print(result.precio)
            sum += result.precio
        self.suma_total = sum


    def _compute_fill_anexos(self):
        get_id = self.env['cot.list.material'].search([('name','=',self.nombre),('descripcion','=',self.descripcion),('cantidad','=',self.cantidad)])
        lines = []
        lines.append((5,0,{}))
        for result in get_id.attachment_ids:
            # print(result.nombre)
            line = (4,result.id,{})
            lines.append(line)
        self.anexos_id = lines

class MaterialServicio(models.Model):
    _name = 'dtm.list.material.producto'
    _description = 'Se generan los servicios a realizar'

    model_id = fields.Many2one('dtm.requerimientos')
    material_servicio = fields.Selection(strin="Servicio", selection=[('material', 'Material'),('servicio', 'Servicio') ])
    descripcion = fields.Text(string="Descripción")
    cantidad = fields.Integer(string = "Cantidad")
    precio_unitario = fields.Float(string = "Precio/Unitario")
    precio = fields.Float(string = "Precio Total")



    @api.onchange("precio_unitario")
    def _onchange_precio_unitario(self):
        self.precio = self.precio_unitario * self.cantidad

    @api.onchange("cantidad")
    def _onchange_cantidad(self):
        self.precio = self.precio_unitario * self.cantidad


