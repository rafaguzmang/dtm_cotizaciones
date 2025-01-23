from odoo import api,fields,models,tools
from datetime import datetime

class DTMCotizaciones(models.Model):
    _name = "dtm.cotizaciones"
    _description = "Cotizaciones"
    _order = "no_cotizacion desc"
    _rec_name = "no_cotizacion"


    def _default_init(self): # Genera número consecutivo de NPI y OT del campo no_cotizacion
        # cant = self.env['dtm.cotizaciones'].search_count([])
        get_cot = self.env['dtm.cotizaciones'].search([], order='id desc', limit=1)
        val = str(int(get_cot.no_cotizacion) + 1)
        while len(val)<5:
            val = "0" + val

        return  val

    no_cotizacion = fields.Char(string="No. De Cotización",  default=_default_init,readonly=True)
    cliente_id = fields.Many2one("res.partner",string ="Cliente")
    cliente = fields.Char(related='cliente_id.name')

    date = fields.Date(string="Fecha" ,default= datetime.today())
    attachment_ids = fields.Many2many("dtm.documentos.anexos",string="Anexos")
    telefono = fields.Char(string="Telefono(s)", related='cliente_id.phone')
    correo = fields.Char(string = "email(s)",readonly=True)
    correo_cc =  fields.Many2many("dtm.contactos.anexos",string="cc")
    precio_total = fields.Float(string="Precio total")
    proveedor = fields.Selection(string='Proveedor',default='dtm',
        selection=[('dtm', 'DISEÑO Y TRANSFORMACIONES METALICAS S DE RL DE CV'), ('mtd', 'METAL TRANSFORMATION & DESIGN')])

    atencion_id = fields.Many2one("dtm.cotizacion.atencion")
    servicios_id = fields.One2many('dtm.cotizacion.requerimientos','model_id', string='Requerimientos', readonly=False)
    prediseno_id = fields.One2many("dtm.cotizaciones.predisenos",'model_id')

    material_id = fields.Many2many('dtm.list.material.producto')

    terminos_pago = fields.Char(string="Terminos de pago",default="Terminos de Pago: Credito 45 dias")

    entrega = fields.Char(string="Entrega",default="L.A.B: Chihuahua, Chih.")

    curency = fields.Selection(string="Tipo de moneda",default="mx",
               selection=[("mx","Precio Especificado en Pesos Mexicanos"),("us","Precio Especificado en Dolares Americanos")])


    subject = fields.Char(string="Asunto:")
    dirigido = fields.Char(default="A quien corresponda :")
    body_email = fields.Text(default="Por este medio hago llegar la factura. \n Saludos cordiales")
    email_image = fields.Image(string="Firma")
    status = fields.Char()
    po_number = fields.Char(string="PO")

    # -----------------------------------------------------------Provicional-------------------------------------------------------------
    def get_view(self, view_id=None, view_type='form', **options):# Llena la tabla dtm.ordenes.compra.precotizaciones con las cotizaciones(NO PRECOTIZACIONES) pendientes
        res = super(DTMCotizaciones,self).get_view(view_id, view_type,**options)

        get_self = self.env['dtm.ordenes.compra'].search([])
        for item in get_self:
            get_po = self.env['dtm.cotizaciones'].search([("no_cotizacion","=",item.no_cotizacion)])
            if get_po:
                get_po.po_number = item.orden_compra
        return res

    #-------------------------------------------------Acciones y Computes -----------------------------------------------------------------
    def action_generar(self):
        for prediseno in self.prediseno_id:
            get_prediseno = self.env['dtm.odt.prediseno'].search([('ot_number','=',prediseno.ot_number)])
            if get_prediseno:
                get_prediseno.write({
                    'name_client':self.cliente_id.id,
                    'product_name':prediseno.product_name,
                    'cuantity':prediseno.cuantity,
                })
            else:
                get_prediseno.create({
                    'ot_number':prediseno.ot_number,
                    'tipe_order':'PD',
                    'name_client':self.cliente_id.id,
                    'product_name':prediseno.product_name,
                    'date_in':prediseno.date_in,
                    'cuantity':prediseno.cuantity,
                })



    def action_imprimir(self):
        if self.proveedor == 'dtm':
            return self.env.ref("dtm_cotizaciones.formato_cotizacion").report_action(self)
        else:
            self.terminos_pago = "Payment terms: 30 days net"
            self.entrega= "F.O.B Chihuahua, Chih."
            return self.env.ref("dtm_cotizaciones.formato_cotizacion_mtd").report_action(self)


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

    descripcion = fields.Char(string="Nombre")
    unidad = fields.Selection(string="Moneda",selection=[("mxn","MXN"),("dlls","DLLS")],default="mxn")
    tipo_cantidad = fields.Selection(string="UM",selection=[("unidad","Unidad"),("peso","Peso")],default="unidad")
    cantidad = fields.Integer(string="cantidad")
    precio_unitario = fields.Float(string="Precio Unitario")
    total = fields.Float(string="Total", store=True,compute="_compute_total")
    id_need= fields.Integer()
    items_id = fields.One2many("dtm.cotizacion.item", "model_id")


    @api.depends("precio_unitario","cantidad")
    def _compute_total(self):
        for result in self:
            result.total = result.cantidad * result.precio_unitario
            # print(result.model_id.no_cotizacion,result.model_id)

class Items(models.Model):
    _name = "dtm.cotizacion.item"
    _description = "Modelo provicional para llevar la lista de los articulos a cotizar"

    model_id = fields.Many2one("dtm.cotizacion.requerimientos")

    name = fields.Char(string="Descripción")
    # FK para casar la descripción de necesidades con la cotización
    neces_id = fields.Integer()

class Atencion(models.Model):
    _name = "dtm.cotizacion.atencion"
    _description = "Tabla para guardar las opciones de atención"
    _rec_name = "atencion"

    atencion = fields.Char(string="AT'n")

class Prediseno(models.Model):
    _name = "dtm.cotizaciones.predisenos"
    _description = "Modelo para guardar los prediseños solicitados"
    # _rec_name = "descripcion"

    def action_autoNum(self):
        get_pd = self.env['dtm.odt'].search([("tipe_order","=","PD")],order='ot_number desc', limit=1)
        get_self = self.env['dtm.odt.prediseno'].search([],order='ot_number desc', limit=1)
        return get_pd.ot_number + 1 if get_pd.ot_number > get_self.id else get_self.id + 1

    model_id = fields.Many2one('dtm.cotizaciones')
    ot_number = fields.Integer(string="NO.",default=action_autoNum,readonly=True)
    tipe_order = fields.Char(string="TIPO",readonly=True, default='PD')
    name_client = fields.Many2one("res.partner",string ="Cliente")

    product_name = fields.Char(string="NOMBRE DEL PRODUCTO")
    date_in = fields.Date(string="CREACIÒN", default= datetime.today(),readonly=True)

    cuantity = fields.Integer(string="CANTIDAD")
    disenador = fields.Selection(string="DISEÑADOR", selection=[("andres","Andrés Orozco"),("luis","Luís García")])


