from odoo import api,fields,models,tools
from odoo.modules import get_module_resource
from odoo.exceptions import ValidationError
import base64
import datetime

class DTMCotizaciones(models.Model):
    _name = "dtm.cotizaciones"
    _description = "Cotizaciones"
    _order = "no_cotizacion desc"

    def _default_init(self): # Genera número consecutivo de NPI y OT del campo no_cotizacion
        cant = self.env['dtm.cotizaciones'].search_count([])
        val = str(cant + 1)
        while len(val)<5:
            val = "0" + val

        return  val

    no_cotizacion = fields.Char(string="No. De Cotización",  default=_default_init,readonly=True)
    cliente_id = fields.Many2one("res.partner",tring="Cliente")
    cliente = fields.Char(string="Cliente", related='cliente_id.name')
    d = datetime
    date = fields.Date(string="Fecha" ,default= d.datetime.today())
    attachment_ids = fields.Many2many("dtm.documentos.anexos",string="Anexos")
    telefono = fields.Char(string="Telefono(s)", related='cliente_id.mobile')
    correo = fields.Char(string = "email(s)",readonly=True)
    correo_cc =  fields.Many2many("dtm.contactos.anexos",string="cc")
    precio_total = fields.Float(string="Precio total")
    proveedor = fields.Selection(string='Proveedor',default='dtm',
        selection=[('dtm', 'DISEÑO Y TRANSFORMACIONES METALICAS S DE RL DE CV'), ('mtd', 'METAL TRANSFORMATION & DESIGN')],tracking=True)

    atencion_id = fields.Many2one("dtm.cotizacion.atencion")

    # servicios_id = fields.One2many('dtm.cotizacion.requerimientos','model_id',compute="_compute_fill_servicios", string='Requerimientos', readonly=False)
    servicios_id = fields.One2many('dtm.cotizacion.requerimientos','model_id', string='Requerimientos', readonly=False)

    material_id = fields.Many2many('dtm.list.material.producto')

    terminos_pago = fields.Char(string="Terminos de pago",default="Terminos de Pago: Credito 45 dias")

    entrega = fields.Char(string="Entrega",default="L.A.B: Chihuahua, Chih.")

    curency = fields.Selection(string="Tipo de moneda",default="mx",
               selection=[("mx","Precio Especificado en Pesos Mexicanos"),("us","Precio Especificado en Dolares Americanos")],tracking=True)



    # subject = fields.Char(string="Asunto:",compute="_compute_subject", readonly=False)
    subject = fields.Char(string="Asunto:")
    dirigido = fields.Char(default="A quien corresponda :")
    body_email = fields.Text(default="Por este medio hago llegar la factura. \n Saludos cordiales")
    # email_image = fields.Image(string="Firma", compute="_compute_image")
    email_image = fields.Image(string="Firma")
    status = fields.Integer()


    # -----------------------------------------------------------Provicional-------------------------------------------------------------

    #-------------------------------------------------Acciones y Computes -----------------------------------------------------------------

    def action_imprimir(self):
        print(self.proveedor)

        return self.env.ref("dtm_cotizaciones.formato_cotizacion").report_action(self)


    @api.onchange('cliente_id') # Carga correo y número de telefono de los contactos del campo atencion
    def _onchange_cliente_ids(self):
        if self.cliente_id.commercial_company_name:
            contactos = self.env['res.partner'].search([('commercial_company_name','=',self.cliente_id.commercial_company_name),
                                                        ('display_name','!=',self.cliente_id.commercial_company_name)])

            self.env.cr.execute("DELETE FROM dtm_contactos_anexos")
            for get in contactos:
                vals = {
                    "name":get.name,
                    "correo":get.email,
                    "telefono":get.mobile
                }
                self.env['dtm.contactos.anexos'].create(vals)

            self.correo = self.cliente_id.email



class Requerimientos(models.Model):
    _name = "dtm.cotizacion.requerimientos"
    _description = "Servicios a cotizar"

    model_id = fields.Many2one('dtm.cotizaciones')

    descripcion = fields.Char(string="Descripción")
    unidad = fields.Selection(string="UM",selection=[("mxn","MXN"),("dlls","DLLS")],default="mxn")
    cantidad = fields.Integer(string="cantidad")
    precio_unitario = fields.Float(string="Precio Unitario")
    total = fields.Float(string="Total", store=True,compute="_compute_total")

    items_id = fields.One2many("dtm.cotizacion.item", "model_id")

    @api.depends("precio_unitario")
    def _compute_total(self):
        for result in self:
            result.total = result.cantidad * result.precio_unitario
            print(result.model_id.no_cotizacion,result.model_id)


class Items(models.Model):
    _name = "dtm.cotizacion.item"
    _description = "Modelo provicional para llevar la lista de los articulos a cotizar"

    model_id = fields.Many2one("dtm.cotizacion.requerimientos")

    name = fields.Char(string="Descripción")

class Atencion(models.Model):
    _name = "dtm.cotizacion.atencion"
    _description = "Tabla para guardar las opciones de atención"
    _rec_name = "atencion"

    atencion = fields.Char(string="AT'n")


