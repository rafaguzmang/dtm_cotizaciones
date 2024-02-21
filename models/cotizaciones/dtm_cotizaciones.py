from odoo import api,fields,models,tools
from odoo.modules import get_module_resource
from odoo.exceptions import ValidationError
import base64
import datetime

class DTMCotizaciones(models.Model):
    _name = "dtm.cotizaciones"
    _description = "Cotizaciones"
    _order = "no_cotizacion desc"

    no_cotizacion = fields.Char(string="No. De Cotización", readonly=True)
    cliente = fields.Char(string="Cliente", readonly=True)
    d = datetime
    date = fields.Date(string="Fecha" ,default= d.datetime.today(), readonly=True)
    attachment_ids = fields.Many2many("dtm.documentos.anexos",string="Anexos", readonly=False)
    telefono = fields.Char(string="Telefono(s)", readonly=True)
    correo = fields.Char(string = "email(s)", readonly=True)
    correo_cc = fields.Char(string="cc" , readonly=True)
    precio_total = fields.Float(string="Precio total")
    proveedor = fields.Selection(string='Proveedor',default='dtm',
        selection=[('dtm', 'DISEÑO Y TRANSFORMACIONES METALICAS S DE RL DE CV'), ('mtd', 'METAL TRANSFORMATION & DESIGN')],tracking=True)

    atencion_id = fields.Many2one("dtm.cotizacion.atencion")

    servicios_id = fields.One2many('dtm.cotizacion.requerimientos','model_id',compute="_compute_fill_servicios", string='Requerimientos', readonly=False)

    material_id = fields.Many2many('dtm.list.material.producto')

    terminos_pago = fields.Char(string="Terminos de pago",default="Terminos de Pago: Credito 45 dias")

    entrega = fields.Char(string="Entrega",default="L.A.B: Chihuahua, Chih.")

    curency = fields.Selection(string="Tipo de moneda",default="mx",
               selection=[("mx","Precio Especificado en Pesos Mexicanos"),("us","Precio Especificado en Dolares Americanos")],tracking=True)

    subject = fields.Char(string="Asunto:",compute="_compute_subject", readonly=False)
    dirigido = fields.Char(default="A quien corresponda :")
    body_email = fields.Text(default="Por este medio hago llegar la factura. \n Saludos cordiales")
    email_image = fields.Image(string="Firma", compute="_compute_image")
    status = fields.Integer()

    # Datos para el envío del correo (Formato)
    def _compute_subject(self):
        for result in self:
            subject = "Cotización DTM no " + result.no_cotizacion
            result.subject = subject

    def _compute_image(self):
        email = self.env.user.partner_id.email
        # if email == "ventas1@dtmindustry.com": # Carga imagen personalizada del usuario
        img_path = get_module_resource('dtm_cotizaciones', 'static/src/images', 'alejandro_erives_dtm.png') # your default image path
        # else:
        #     img_path = None


        for result in self:
             if img_path != None:
                with open(img_path, 'rb') as f: # read the image from the path
                    image = f.read()
                    result.email_image = base64.b64encode(image)
             else:
                 result.email_image = None

    def _compute_fill_servicios(self): # Llena el campo servicios_id con los datos de la tabla requerimientos
        requerimientos = self.env['dtm.cotizacion.requerimientos'].search([])
        materiales = self.env['dtm.list.material.producto'].search([])


        for result in requerimientos:  # Borra de la tabla dtm_requerimientos los item borrados de la tabla cot_list_material
            get_needs = self.env['dtm.requerimientos'].search([("id", "=", result.id)])
            # print(get_needs.model_id, result.id)
            if not get_needs:
                # print(get_needs, result.id)
                self.env.cr.execute("DELETE FROM dtm_cotizacion_requerimientos WHERE id =" + str(result.id))

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
        if not self.date:
            self.date = self.d.datetime.today()

        self.env.cr.execute("UPDATE dtm_client_needs SET cotizacion=true WHERE no_cotizacion='"+self.no_cotizacion+"'")

        return self.env.ref("dtm_cotizaciones.formato_cotizacion").report_action(self)

    def action_send_email(self):
        # print(self.env.user.email)
        if not self.date:
            # print(self.d.datetime.today())
            self.date = self.d.datetime.today()
        mail_template = self.env.ref('dtm_cotizaciones.cotizacion_email_template')
        mail_template.send_mail(self.id,force_send=True)

    @api.onchange("atencion_id")
    def _onchange_atencion_id(self):
        self.dirigido = self.atencion_id.atencion

    def get_view(self, view_id=None, view_type='form', **options):#Llena la tabla dtm_cotizaciones de la tabla dtm_clientes_needs
        res = super(DTMCotizaciones,self).get_view(view_id, view_type,**options)
        get_info = self.env['dtm.client.needs'].search([])

        for result in get_info:
            # print(result.no_cotizacion)
            get_self = self.env['dtm.cotizaciones'].search([("no_cotizacion","=",result.no_cotizacion)])
            correo_cc = result.correo
            if correo_cc:
                print(correo_cc)
                if correo_cc.find(";") != -1:
                    correo_cc = correo_cc.replace(";",",")
                    print(correo_cc)
                    x = correo_cc.index(",")
                    correo_cc = correo_cc[x+1:len(correo_cc)]
                else:
                    correo_cc = ""

            else:
                correo_cc = ""
            if get_self:
                self.env.cr.execute("UPDATE dtm_cotizaciones SET telefono='"+str(result.cliente_ids.phone) +"', correo='"+str(result.cliente_ids.email) +
                        "', cliente='"+str(result.cliente_ids.name) + "', correo_cc='"+correo_cc+"' WHERE no_cotizacion ='" +result.no_cotizacion+"'")
            else:
                 self.env.cr.execute("INSERT INTO dtm_cotizaciones (id, no_cotizacion, cliente, telefono, correo, terminos_pago, entrega, curency, proveedor, correo_cc) " +
                                    "VALUES ("+ str(result.id) +", '"+ result.no_cotizacion +"','"+result.cliente_ids.name+"', '"+ str(result.cliente_ids.phone) + "', '"+ str(result.cliente_ids.email) +
                                     "', 'Terminos de Pago: Credito 45 dias', 'L.A.B: Chihuahua, Chih.', 'mx','dtm', '"+correo_cc+"')")


        #Llena o actualiza la tabla dtm_cotizaciones_requerimientos de la tabla dtm_requerimientos

        get_req = self.env['dtm.requerimientos'].search([])

        dictionary = {}
        for result in get_req:
            get_cot_rec = self.env['dtm.cotizacion.requerimientos'].search([('id','=',result.id)])
            if get_cot_rec:
                if not dictionary.get(result.servicio):
                    dictionary[result.servicio]=1
                else:
                    dictionary[result.servicio] = dictionary.get(result.servicio) + 1
                #
                # self.env.cr.execute("UPDATE dtm_cotizacion_requerimientos SET no_item ="+str(dictionary[result.servicio])+
                #                     ", cantidad= "+ str(result.cantidad) +str(result.nombre)+"'"
                #                     " WHERE id="+str(result.id))

                self.env.cr.execute("UPDATE dtm_cotizacion_requerimientos SET no_item ="+str(dictionary[result.servicio])+
                                    ", cantidad= "+ str(result.cantidad) +
                                    " WHERE id="+str(result.id))

            else:
                dictionary = {}
                if not dictionary.get(result.servicio):
                    dictionary[result.servicio]=1
                else:
                    dictionary[result.servicio] = dictionary.get(result.servicio) + 1

                self.env.cr.execute("INSERT INTO dtm_cotizacion_requerimientos (id, descripcion, cantidad, no_cotizacion, no_item) " +
                                "VALUES ("+ str(result.id) +", '"+ str(result.nombre) +"',"+str(result.cantidad) + ",'"+str(result.servicio)+ "',"+str(dictionary[result.servicio])+ ")")
        return res


class Requerimientos(models.Model):
    _name = "dtm.cotizacion.requerimientos"
    _description = "Servicios a cotizar"

    model_id = fields.Many2one('dtm.cotizaciones')
    no_cotizacion = fields.Char(string="No. De Cotización", readonly = True)
    no_item = fields.Integer(string="No")
    descripcion = fields.Char(string="Descripción")
    unidad = fields.Char(string="UM")
    cantidad = fields.Integer(string="cantidad")
    precio_unitario = fields.Float(string="Precio Unitario")
    total = fields.Float(string="Total", store=True)

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


