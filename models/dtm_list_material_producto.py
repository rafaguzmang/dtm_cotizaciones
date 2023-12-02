from odoo import api, fields, models


class ListaMaterialProducto(models.Model):
    _name = "dtm.list.material.producto"


    material_servicio = fields.Selection(strin="Servicio", selection=[('material', 'Material'),('servicio', 'Servicio') ])
    descripcion = fields.Text(string="Descripción")
    cantidad = fields.Integer(string = "Cantidad")
    precio = fields.Float(string = "Precio")
    servicio_id = fields.Integer()


    @api.model  #--------------- Sirve para ver los campos cuando se presiona el botón de crear/guardar
    def create(self,vals):
        res = super(ListaMaterialProducto, self).create(vals)
        print("res list material-------->",res)
        print("vals list material------->",vals)
        print("self list material------->",self)
        return res