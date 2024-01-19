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
        selection=[('dtm', 'DISEÑO Y TRANSFORMACIONES METALICAS S DE RL DE CV'), ('mtd', 'METAL TRANSFORMATION & DESIGN')],tracking=True)

    atencion_id = fields.Many2one("dtm.cotizacion.atencion")

    servicios_id = fields.Many2many('dtm.cotizacion.requerimientos','model_id',compute="_compute_fill_servicios", string='Requerimientos', readonly=False)

    material_id = fields.Many2many('dtm.list.material.producto')

    terminos_pago = fields.Char(string="Terminos de pago",default="Terminos de Pago: Credito 45 dias")

    entrega = fields.Char(string="Entrega",default="L.A.B: Chihuahua, Chih.")

    curency = fields.Selection(string="Tipo de moneda",default="mx",
               selection=[("mx","Precio Especificado en Pesos Mexicanos"),("us","Precio Especificado en Dolares Americanos")],tracking=True)

    # Datos para el envío del correo (Formato)

    subject = fields.Char(string="Asunto:",default="Cotización DTM")
    dirigido = fields.Char(default="A quien corresponda :")
    body_email = fields.Text(default="Por este medio hago llegar la factura. \n Saludos cordiales")


    def _compute_fill_servicios(self): # Llena el campo servicios_id con los datos de la tabla requerimientos
        requerimientos = self.env['dtm.cotizacion.requerimientos'].search([])
        materiales = self.env['dtm.list.material.producto'].search([])
        lines = []
        for slf in self:
            for result in requerimientos:
                if result.no_cotizacion == slf.no_cotizacion:
                    line =(4,result.id,{})
                    lines.append(line)
            self.servicios_id = lines

        lines = []
        for slf in self.servicios_id: # Carga servicios_id con los servicios o materiales correspondientes a los requerimientos
            for result in materiales:
                # print(result.model_id.id)
                if result.model_id.id == slf.id:
                    # print(result.descripcion)
                    line =(4,result.id,{})
                    lines.append(line)
            self.material_id = lines
        # print(self.material_id)


    def action_imprimir(self):
        print("Imprimiento")
        
        return self.env.ref("dtm_cotizaciones.formato_cotizacion").report_action(self)


    def action_send_email(self):
        print("Enviado")
        # print(self.env.user.email)
        # if not self.date:
        #     print(self.d.datetime.today())
        #     self.date = self.d.datetime.today()

        # mail_template = self.env.ref('dtm_cotizaciones.cotizacion_mail_template')
        # mail_template.send_mail(self.id,force_send=True)


    @api.onchange("servicios_id")
    def _onchange_servicios(self):
        get_info = self.env["dtm.cotizacion.requerimientos"].search([("no_cotizacion","=",self.no_cotizacion)])
        # print(get_info)

    def get_view(self, view_id=None, view_type='form', **options):#Llena la tabla dtm_cotizaciones de la tabla dtm_clientes_needs
        res = super(DTMCotizaciones,self).get_view(view_id, view_type,**options)
        get_self = self.env['dtm.cotizaciones'].search([])
        get_info = self.env['dtm.client.needs'].search([("id",">",len(get_self))])
        if len(get_info) > 0:
             for result in get_info:
                 self.env.cr.execute("INSERT INTO dtm_cotizaciones (id, no_cotizacion, cliente, telefono, correo, terminos_pago, entrega, curency, proveedor) " +
                                    "VALUES ("+ str(result.id) +", '"+ result.no_cotizacion +"','"+result.cliente_ids.name+"', '"+ str(result.cliente_ids.phone) + "', '"+ str(result.cliente_ids.email) +
                                     "', 'Terminos de Pago: Credito 45 dias', 'L.A.B: Chihuahua, Chih.', 'mx','dtm')")


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




class Atencion(models.Model):
    _name = "dtm.cotizacion.atencion"
    _description = "Tabla para guardar las opciones de atención"
    _rec_name = "atencion"

    atencion = fields.Char(string="AT'n")


