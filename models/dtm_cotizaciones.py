from odoo import api,fields,models,_
import datetime

class DTMCotizaciones(models.Model):
    _name = "dtm.cotizaciones"
    _description = "Cotizaciones"

    no_cotizacion = fields.Char(string="No. De Cotización", readonly=True)
    cliente = fields.Char(string="Cliente", readonly=True)
    d = datetime
    date = fields.Date(string="Fecha" ,default= d.datetime.today(), readonly=True)
    attachment_ids = fields.Many2many("dtm.documentos.anexos",string="Anexos", readonly=False)
    telefono = fields.Char(string="Telefono(s)", readonly=True)
    correo = fields.Char(string = "email(s)", readonly=True)

    precio_total = fields.Float(string="Precio total")
    proveedor = fields.Selection(string='Proveedor',default='dtm',
        selection=[('dtm', 'DISEÑO Y TRANSFORMACIONES METALICAS S DE RL DE CV'), ('mtd', 'METAL TRANSFORMATION & DESIGN')])

    atencion_id = fields.Many2one("dtm.cotizacion.atencion")

    servicios_id = fields.Many2many('dtm.cotizacion.requerimientos','model_id', string='Requerimientos', readonly=False)

    def action_imprimir(self):
        print("Imprimiento")
        print(self.correo)
        print("")

    @api.onchange("servicios_id")
    def _onchange_servicios(self):
        get_info = self.env["dtm.cotizacion.requerimientos"].search([("no_cotizacion","=",self.no_cotizacion)])
        print(get_info)

    def get_view(self, view_id=None, view_type='form', **options):#Llena la tabla dtm_cotizaciones de la tabla dtm_clientes_needs
        res = super(DTMCotizaciones,self).get_view(view_id, view_type,**options)
        get_info = self.env['dtm.client.needs'].search([])
        self.env.cr.execute("DELETE FROM dtm_cotizaciones")
        for result in get_info:
            self.env.cr.execute("INSERT INTO dtm_cotizaciones (id, no_cotizacion, cliente, telefono, correo) " +
                                "VALUES ("+ str(result.id) +", '"+ result.no_cotizacion +"','"+result.cliente_ids.name+"', '"+ str(result.cliente_ids.phone) + "', '"+ str(result.cliente_ids.email) + "')")

        #Llena o actualiza la tabla dtm_cotizaciones_requerimientos de la tabla dtm_requerimientos
        get_dest = self.env['dtm.cotizacion.requerimientos'].search([])
        get_info2 = self.env['dtm.requerimientos'].search([("id",">",len(get_dest))])

        dictionary = {}
        for result in get_dest:
            if not dictionary.get(result.no_cotizacion):
                dictionary[result.no_cotizacion]=1
            else:
                dictionary[result.no_cotizacion] = dictionary.get(result.no_cotizacion) + 1

            self.env.cr.execute("UPDATE dtm_cotizacion_requerimientos SET no_item = "+str(dictionary[result.no_cotizacion]) +", cantidad= "+ str(result.cantidad) +", precio_unitario="+str(result.precio_unitario) +" , "+
                                "total="+str(result.total) +" WHERE id="+str(result.id))
        dictionary = {}
        for result in get_info2:
            if not dictionary.get(result.servicio):
                dictionary[result.servicio]=1
            else:
                dictionary[result.servicio] = dictionary.get(result.servicio) + 1

            self.env.cr.execute("INSERT INTO dtm_cotizacion_requerimientos (id, descripcion, cantidad, no_cotizacion, no_item) " +
                                "VALUES ("+ str(result.id) +", '"+ result.descripcion +"',"+str(result.cantidad) + ",'"+str(result.servicio)+ "',"+str(dictionary[result.servicio])+ ")")


        return res


class Requerimientos(models.Model):
    _name = "dtm.cotizacion.requerimientos"
    _description = "Servicios a cotizar"

    model_id = fields.Many2one("dtm.cotizaciones")
    no_cotizacion = fields.Char(string="No. De Cotización", readonly = True)
    no_item = fields.Integer(string="No")
    descripcion = fields.Char(string="Descripción")
    cantidad = fields.Integer(string="cantidad")
    precio_unitario = fields.Float(string="Precio Unitario")
    total = fields.Float(string="Total", readonly=True)

    @api.onchange("cantidad")
    def _onchange_precio(self):
        self.total = self.cantidad * self.precio_unitario

    @api.onchange("precio_unitario")
    def _onchange_precio(self):
        self.total = self.cantidad * self.precio_unitario

    # compute="_compute_fill_servicios"
    def _compute_fill_servicios(self): # Llena el campo servicios_id con los datos de la tabla requerimientos
        requerimientos = self.env['dtm.cotizacion.requerimientos'].search([])
        lines = []
        for slf in self:
            for result in requerimientos:
                if result.no_cotizacion == slf.no_cotizacion:
                    line =(4,result.id,{})
                    lines.append(line)
            self.servicios_id = lines


class Atencion(models.Model):
    _name = "dtm.cotizacion.atencion"
    _description = "Tabla para guardar las opciones de atención"
    _rec_name = "atencion"

    atencion = fields.Char(string="AT'n")


