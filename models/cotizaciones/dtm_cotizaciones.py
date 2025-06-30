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
    no_recotizacion = fields.Integer(string='Recotización', default=0,readonly=True)

    date = fields.Date(string="Fecha" ,default= datetime.today())
    # attachment_ids = fields.Many2many("dtm.documentos.anexos",string="Anexos")
    telefono = fields.Char(string="Telefono(s)", related='cliente_id.phone')
    correo = fields.Char(string = "email(s)",readonly=True)
    correo_cc =  fields.Many2many("dtm.contactos.anexos",string="cc")
    precio_total = fields.Float(string="Precio total")
    proveedor = fields.Selection(string='Proveedor',default='dtm',
        selection=[('dtm', 'DISEÑO Y TRANSFORMACIONES METALICAS S DE RL DE CV'), ('mtd', 'METAL TRANSFORMATION & DESIGN')])

    atencion_id = fields.Many2one("dtm.cotizacion.atencion")
    servicios_id = fields.One2many('dtm.cotizacion.requerimientos','model_id', string='Requerimientos', readonly=False)

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
    recotizacion = fields.Integer(string='Recotización')

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
    @api.onchange('prediseno_id')
    def action_generar(self):
        for prediseno in self.prediseno_id:
            vals = {
                "od_number":prediseno.od_number,
                "tipe_order":'PD',
                "name_client":self.cliente,
                "product_name":prediseno.product_name,
                "date_in":prediseno.date_in,
                "date_rel":prediseno.date_rel,
                "cuantity":prediseno.cuantity,
                "disenador":'Andrés Orozco' if prediseno.disenador == 'andres' else 'Luis García',
                "description":prediseno.description,
                "archivos_id": [(6,0,[self.servicios_id.attachment_ids._origin.id])],
            }
            get_od = self.env['dtm.odt'].search([("od_number","=",prediseno.od_number)])
            get_od.write(vals) if get_od else get_od.create(vals)



    def action_imprimir(self):
        if self.proveedor == 'dtm':
            return self.env.ref("dtm_cotizaciones.formato_cotizacion").report_action(self)
        else:
            self.terminos_pago = "Payment terms: 30 days net"
            self.entrega= "F.O.B Chihuahua, Chih."
            return self.env.ref("dtm_cotizaciones.formato_cotizacion_mtd").report_action(self)

    def action_refacturar(self):
        refacturar = self.env['dtm.cotizaciones.recotizacion'].search([('no_cotizacion','=',self.no_cotizacion),('no_recotizacion','=',self.no_recotizacion)])
        # refacturar = self.env['dtm.cotizaciones.recotizacion'].search([('no_cotizacion','=',self.no_cotizacion)])

        vals = {
            'no_cotizacion':self.no_cotizacion,
            'cliente':self.cliente,
            'no_recotizacion':self.no_recotizacion,
            'date':self.date,
            'telefono':self.telefono,
            'correo':self.correo,
            'precio_total':self.precio_total,
            'proveedor':self.proveedor,
            'terminos_pago':self.terminos_pago,
            'entrega':self.entrega,
            'curency':self.curency,
            'atencion':self.atencion_id.atencion,
            'servicios_id':[(6, 0, self.servicios_id.mapped('id'))],
            'prediseno_id':[(6,0,self.prediseno_id.mapped('id'))],
        }
        if not refacturar:
            refacturar.create(vals)
            self.no_recotizacion += 1

    def action_versiones(self):
        get_versiones = self.env['dtm.cotizaciones.versiones'].search([('no_cotizacion','=',self.no_cotizacion),('cliente','=',self.cliente_id.name)])
        if not get_versiones:
            self.env['dtm.cotizaciones.versiones'].create({'no_cotizacion':self.no_cotizacion,'cliente':self.cliente_id.name})
        self.action_refacturar()
        self_versiones = self.env['dtm.cotizaciones.recotizacion'].search([('no_cotizacion','=',self.no_cotizacion)])
        print(self_versiones)
        get_versiones.write({'versiones_id':self_versiones.ids})

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
    attachment_ids = fields.Many2many("dtm.documentos.anexos", string="Archivos", readonly=False)
    cotizacion_materiales_id = fields.One2many("dtm.cotizacion.materiales","model_id")


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


class CotizacionMateriales(models.Model):
    _name = "dtm.cotizacion.materiales"
    _description = "Modelo para solicitar la cotización de los materiales"

    model_id = fields.Many2one("dtm.cotizacion.requerimientos")

    material_id = fields.Many2one("dtm.materiales",string="Material")
    precio = fields.Float(string="Costo", readonly=True)
    # espera = fields.Boolean(string="En espera")

    @api.onchange('material_id')
    def _onchage_costo(self):
        print(self.material_id._origin.id)
        find = self.env['dtm.compras.precios'].search([('codigo','=',self.material_id._origin.id)],limit=1).precio
        if find > 0:
            print('mayor a cero')
            self.precio = find
        elif find == 0:
            compras = self.env['dtm.compras.requerido'].search([('codigo','=',self.material_id._origin.id),('tipo_orden','=','Cotización')])
            vals = {
                'codigo':self.material_id._origin.id,
                'nombre':self.material_id.nombre,
                'cantidad':1,
                'tipo_orden':'Cotización',
                'aprovacion': True,
                'fecha_recepcion':datetime.today(),
                'orden_compra':'-----',
                'disenador': 'Ventas'
            }
            print(compras)
            if self.material_id._origin.id and self.material_id.nombre:
                compras.write(vals) if compras else compras.create(vals)

    def action_recotizar(self):
        compras = self.env['dtm.compras.requerido'].search(
            [('codigo', '=', self.material_id._origin.id), ('tipo_orden', '=', 'Cotización')])
        vals = {
            'codigo': self.material_id._origin.id,
            'nombre': self.material_id.nombre,
            'cantidad': 1,
            'tipo_orden': 'Cotización',
            'aprovacion': True,
            'fecha_recepcion': datetime.today(),
            'orden_compra': '-----',
            'disenador': 'Ventas',
            'unitario':self.precio
        }
        print(compras)
        if self.material_id._origin.id and self.material_id.nombre:
            compras.write(vals) if compras else compras.create(vals)

class Versiones(models.Model):
    _name = 'dtm.cotizaciones.versiones'
    _description = 'Modelo para llevar el historials de las cotizaciones'
    _rec_name = "no_cotizacion"

    no_cotizacion = fields.Char(string="No. De Cotización",readonly=True)
    cliente = fields.Char(strin='cliente',readonly=True)
    versiones_id = fields.Many2many('dtm.cotizaciones.recotizacion')

class Recotizacion(models.Model):
    _name = 'dtm.cotizaciones.recotizacion'
    _description = 'Modelo para llevar el historials de las cotizaciones'
    _rec_name = "no_cotizacion"

    no_cotizacion = fields.Char(string="No. De Cotización",readonly=True)
    cliente = fields.Char(strin='cliente',readonly=True)
    no_recotizacion = fields.Integer(string='Recotización', default=0,readonly=True)

    date = fields.Date(string="Fecha" ,readonly=True)
    # attachment_ids = fields.Many2many("dtm.documentos.anexos",string="Anexos")
    telefono = fields.Char(string="Telefono(s)",readonly=True)
    correo = fields.Char(string = "email(s)",readonly=True)
    # correo_cc =  fields.Many2many("dtm.contactos.anexos",string="cc",readonly=True)
    precio_total = fields.Float(string="Precio total",readonly=True)
    proveedor = fields.Selection(string='Proveedor',default='dtm',
        selection=[('dtm', 'DISEÑO Y TRANSFORMACIONES METALICAS S DE RL DE CV'), ('mtd', 'METAL TRANSFORMATION & DESIGN')],readonly=True)

    atencion = fields.Char(string="Atención",readonly=True)
    servicios_id = fields.Many2many('dtm.cotizacion.requerimientos', readonly=True)
    # prediseno_id = fields.One2many("dtm.cotizaciones.predisenos",'model_id',readonly=True)

    material_id = fields.Many2many('dtm.list.material.producto',readonly=True)

    terminos_pago = fields.Char(string="Terminos de pago",default="Terminos de Pago: Credito 45 dias",readonly=True)

    entrega = fields.Char(string="Entrega",default="L.A.B: Chihuahua, Chih.",readonly=True)

    curency = fields.Selection(string="Tipo de moneda",default="mx",
               selection=[("mx","Precio Especificado en Pesos Mexicanos"),("us","Precio Especificado en Dolares Americanos")],readonly=True)






