from odoo import api,fields,models
import datetime

#------------------- Clase principal
class ClientNeeds(models.Model):
    _name = "dtm.client.needs"
    _inherit = ["mail.thread","mail.activity.mixin"]
    _description = "Tabla para hacer la precotización (costo de la empresa)"
    _order = "no_cotizacion desc"
    _rec_name = "no_cotizacion"

    #---------------Function------------------
    def _default_init(self): # Genera número consecutivo del campo no_cotizacion
        get_cotizacion = self.env['dtm.client.needs'].search([],order="no_cotizacion desc",limit=1)
        return str(int(get_cotizacion.no_cotizacion) + 1)

    no_cotizacion = fields.Char(string="No. De Necesidad", default=_default_init)

    cliente_ids = fields.Many2one("res.partner",string="Cliente", readonly=False, required=True, store=True)

    atencion = fields.Many2many("dtm.contactos.anexos",string="Nombre del requisitor", readonly=False)
    d = datetime
    date = fields.Date(string="Fecha" ,default= d.datetime.today(), readonly=True)   

    attachment_ids = fields.Many2many("dtm.documentos.anexos",string="Anexos", readonly=False)

    telefono = fields.Char(string="Telefono(s)", readonly=True , compute="_compute_onchange",store=True)

    correo = fields.Char(string = "email(s)", readonly=True, compute="_compute_onchange", store=True)

    cotizacion = fields.Boolean(default=False,compute="_compute_cotizacion")

    nivel = fields.Selection(string="Nivel", default="uno",selection=[('uno',1),('dos',2),('tres',3)])

    via_solicitud = fields.Selection(string="Vía de solicitud", selection=[
        ('telefonica', 'Telefónica'), ('correo', 'Correo'), ('planos', 'Planos'), ('dibujos', 'Dibujos')])

    prediseno_id = fields.One2many('dtm.cotizaciones.predisenos','model_id',string='Prediseño')

    # Datos para medición de metricos
    status = fields.Integer()
    notes = fields.Text()
#------------------------ Documentos Anexos------------------------
    list_materials_ids = fields.One2many('cot.list.material', 'model_id',readonly=False)

#-----------------------------------------------------
    message_ids = fields.One2many()    
    has_message = fields.Boolean()
    body = fields.Html()

    autorizacion_id = fields.Many2many("ir.attachment")

    def action_cotizacion(self):
        get_cotizacion = self.env['dtm.cotizaciones'].search([('no_cotizacion','=',self.no_cotizacion)])
        if get_cotizacion:
            get_cotizacion = self.env['dtm.cotizaciones'].search([('no_cotizacion','=',self.no_cotizacion)])
            get_cotizacion.write({
                'cliente_id': self.cliente_ids.id,
                'telefono': self.cliente_ids.phone,
                'date': self.date,
                                  })
        else:
            self.env['dtm.cotizaciones'].create({
                                                'no_cotizacion': self.no_cotizacion,
                                                'cliente_id': self.cliente_ids.id
                                                })
            get_cotizacion = self.env['dtm.cotizaciones'].search([('no_cotizacion','=',self.no_cotizacion)])


        for item in self.list_materials_ids:
            get_cot_list = self.env['dtm.cotizacion.requerimientos'].search([('model_id','=',get_cotizacion.id),
                                                                             ('id_need','=',item.id)])
            if get_cot_list:
                get_cot_list.write({
                    'descripcion': item.name,
                    'cantidad': item.cantidad,
                    'items_id': [(1,self.env['dtm.cotizacion.item'].search([('neces_id','=',item.id)]).id if self.env['dtm.cotizacion.item'].search([('neces_id','=',item.id)]) else 0 ,{'name':item.descripcion})],
                    'attachment_ids': [(6,0,item.attachment_ids.mapped('id'))]
                })
            else:
                get_cot_list.create({
                    'id_need': item.id,
                    'descripcion': item.name,
                    'cantidad': item.cantidad,
                    'model_id':get_cotizacion.id,
                    'items_id': [(0,0,{'name':item.descripcion,'neces_id':item.id})],
                    'attachment_ids': [(6,0,item.attachment_ids.mapped('id'))]
                })


    def _compute_cotizacion(self):
        for result in self:
            result.cotizacion = True if self.env['dtm.cotizaciones'].search([('no_cotizacion','=',result.no_cotizacion)]) else False




     #--------------Onchange-----------------
    @api.onchange('cliente_ids') # Carga correo y número de telefono de los contactos del campo clientes
    def onchange_cliente_ids(self):
        data = self.env['res.partner'].search([('id','=',self.cliente_ids.id)])
        # self.correo = ""
        # self.telefono = ""
        # print(self.correo,self.telefono)
        if data:
            for result in data:
                if result.phone:
                    self.telefono = result.phone + "; "
                else:
                    self.telefono  = "N/A; "
                if result.email:
                    self.correo = result.email + "; "
                else:
                    self.correo = "N/A; "
                if self._origin.id:
                    self.env.cr.execute("UPDATE dtm_client_needs SET telefono='"+self.telefono+"' , correo='"+self.correo+"' WHERE id="+str(self._origin.id))

    @api.depends('atencion') # Carga correo y número de telefono de los contactos del campo atencion
    def _compute_onchange(self):
        servicio = self.env['dtm.client.needs'].search([])
        for result in servicio:
            if result == self.no_cotizacion:
                self.env.cr.execute("UPDATE  cot_list_material SET no_servicio ='"+self.no_cotizacion+"'  WHERE model_id =" + str(self.id))
                # self.env.cr.execute("UPDATE  dtm_documentos_anexos SET no_servicio = '"+self.no_cotizacion+"'  WHERE no_servicio = '-----'" )

        print("atención",self.correo,self.telefono)

        self.correo = ""
        self.telefono = ""

        self.onchange_cliente_ids()

        #print(self.atencion)
        for record in self.atencion:
            self.correo = self.correo + record.correo + "; "
            self.telefono = self.telefono + record.telefono + "; "
        if self.correo:
            self.correo = self.correo[:-2]
        if self.telefono:
            self.telefono = self.telefono[:-2]

        if self._origin.id:
            self.env.cr.execute("UPDATE dtm_client_needs SET telefono='"+self.telefono+"' , correo='"+self.correo+"' WHERE id="+str(self._origin.id))

    @api.onchange('cliente_ids') # Carga correo y número de telefono de los contactos del campo atencion
    def _onchange_cliente_ids(self):
        if self.cliente_ids.commercial_company_name:
            contactos = self.env['res.partner'].search([('commercial_company_name','=',self.cliente_ids.commercial_company_name),
                                                        ('display_name','!=',self.cliente_ids.commercial_company_name)])
            self.env.cr.execute("DELETE FROM   dtm_contactos_anexos" )
            for result in contactos:
                # if result.commercial_company_name == self.cliente_ids.commercial_company_name:
                    if result.name == False:
                        result.name = 'N/A'
                    if result.email == False:
                        result.email = 'N/A'
                    if result.phone == False:
                        result.phone = 'N/A'
                    self.env.cr.execute("INSERT INTO dtm_contactos_anexos(name, correo ,telefono) VALUES ('"+ result.name +"','"+ result.email +"','" +result.phone+ "')" )

    def get_view(self, view_id=None, view_type='form', **options):
        res = super(ClientNeeds,self).get_view(view_id, view_type,**options)

        # Lógica para obtener indicadores de Ventas
        for month in range(1,13):
            if month <= int(datetime.datetime.today().strftime("%m")):
                # Busca las cotizaciones del mes actual y del mes pasado
                self.env.cr.execute(" SELECT date,po_number,id FROM dtm_cotizaciones WHERE EXTRACT(MONTH FROM date) = "+str(month)+
                                    " AND EXTRACT(YEAR FROM date) = "+datetime.datetime.today().strftime("%Y")+";")
                get_cotizaciones = self.env.cr.fetchall()

                self.env.cr.execute(" SELECT date,po_number,id FROM dtm_cotizaciones WHERE EXTRACT(MONTH FROM date) = "+str(month)+
                                    " AND EXTRACT(YEAR FROM date) = "+datetime.datetime.today().strftime("%Y")+";")
                get_cotizaciones_old = self.env.cr.fetchall()

                aceptadas = 0
                noaceptadas = 0
                costo_aceptado = 0
                costo_noaceptado = 0
                if get_cotizaciones:
                    # Obtiene los datos necesarios
                    # Ordenes aceptadas y rechazadas
                    for cotizacion in get_cotizaciones:
                        get_month = self.env['dtm.client.indicadores'].search([('no_month','=',month)])
                        if cotizacion[1] is not None:
                            aceptadas += 1
                            # Iguala el precio en pesos Mexicanos
                            if 'dlls' in self.env['dtm.cotizaciones'].search([('id','=',cotizacion[2])]).mapped('servicios_id').mapped('unidad'):
                                costo_aceptado += sum(self.env['dtm.cotizaciones'].search([('id','=',cotizacion[2])]).mapped('servicios_id').mapped('total')) * get_month.costo_dlls
                            else:
                                costo_aceptado += sum(self.env['dtm.cotizaciones'].search([('id','=',cotizacion[2])]).mapped('servicios_id').mapped('total'))
                        else:
                            noaceptadas += 1
                            if 'dlls' in self.env['dtm.cotizaciones'].search([('id','=',cotizacion[2])]).mapped('servicios_id').mapped('unidad'):
                                costo_noaceptado += sum(self.env['dtm.cotizaciones'].search([('id','=',cotizacion[2])]).mapped('servicios_id').mapped('total')) * get_month.costo_dlls
                            else:
                                costo_noaceptado += sum(self.env['dtm.cotizaciones'].search([('id','=',cotizacion[2])]).mapped('servicios_id').mapped('total'))

                # Si el mes existe lo actualiza si no lo crea
                get_this = self.env['dtm.client.indicadores'].search([('no_month','=',month)])
                if get_this:
                    get_this.write({
                        'cotizaciones':len(get_cotizaciones),
                        'cotizaciones_aceptadas':aceptadas,
                        'cotizaciones_noaceptadas':noaceptadas,
                        # 'cotizaciones_pendientes':self.cotizaciones_pendientes,
                        'cotizaciones_costo_total':costo_noaceptado + costo_aceptado,
                        'cotizaciones_costo_aceptado':costo_aceptado,
                        'porcentaje': (aceptadas * 1)/len(get_cotizaciones) if len(get_cotizaciones) > 0 else 0,

                    })
                else:
                    get_this.create({
                        'no_month':int(datetime.datetime.today().strftime("%m")),
                        'month_name':datetime.datetime.today().strftime("%B"),
                        'cotizaciones':len(get_cotizaciones),
                        'cotizaciones_aceptadas':aceptadas,
                        'cotizaciones_costo_total':costo_noaceptado + costo_aceptado,
                        'cotizaciones_costo_aceptado':costo_aceptado,
                        'porcentaje': (aceptadas * 1)/len(get_cotizaciones) if len(get_cotizaciones) > 0 else 0,
                    })


        return res



class ListMaterial(models.Model):
    _name = "cot.list.material"
    _description = "Modelo para almacenar los materiales para las precotizaciones"
    
    model_id = fields.Many2one("dtm.client.needs")
    name = fields.Char(string="Producto o servicio", readonly=False, required=True)
    descripcion = fields.Text(string="Descripción", readonly=False, required=True)
    cantidad = fields.Integer(string="Cantidad", readonly=False, required=True)
    attachment_ids = fields.Many2many("dtm.documentos.anexos", string="Archivos", readonly=False)
    color = fields.Char(string='Color')


    #material_serv_ids = fields.Many2many("dtm.list.material.producto")


    @api.onchange('material_serv_ids')
    def _onchange_material_serv_ids(self):
        lines = []
        for result in self.material_serv_ids:
            line = (1,result.id,{})
            lines.append(line)
        self.material_serv_ids = lines


class Prediseno(models.Model):
    _name = "dtm.cotizaciones.predisenos"
    _description = "Modelo para guardar los prediseños solicitados"

    def action_autoNum(self):
        get_pd = self.env['dtm.odt'].search([('od_number','!=',0)],order='od_number desc', limit=1)
        return get_pd.od_number + 1

    model_id = fields.Many2one('dtm.client.needs')#Enlaza con el modelo padre
    od_number = fields.Integer(string="NO.",readonly=True,default=action_autoNum)

    product_name = fields.Char(string="NOMBRE DEL PRODUCTO")
    date_in = fields.Date(string="CREACIÒN", default= datetime.datetime.today(),readonly=True)
    description = fields.Text(string="Descripción")

    cuantity = fields.Integer(string="CANTIDAD")
    disenador = fields.Selection(string="DISEÑADOR", selection=[("andres","Andrés Orozco"),("luis","Luís García")])
    date_rel = fields.Date(string="FECHA DE ENTREGA")
    anexos_id = fields.Many2many('ir.attachment','prediseno_send')
    firma_disenador = fields.Char(string="Firma diseñador")

    prediseno_id = fields.Many2many('ir.attachment','prediseno_final',string="Prediseño")
    liga_id = fields.Many2many('ir.attachment','prediseno_liga',string="Ligas")

    def action_prediseno(self):

        dtm_odt = self.env['dtm.odt'].search([('od_number','=',self.od_number)],limit=1)
        print(self.model_id.cliente_ids.name)
        vals = {
            'od_number':self.od_number,
            'tipe_order':'Diseño',
            'name_client':self.model_id.cliente_ids.name,
            'product_name':self.product_name,
            'date_in':self.date_in,
            'date_rel':self.date_rel,
            'cuantity':self.cuantity,
            'disenador':self.disenador,
            'description':self.description,
            'anexos_ventas_id':[(6,0,self.anexos_id.ids)]
        }

        dtm_odt.write({'anexos_ventas_id':[(5,0,{})]}) if dtm_odt else None
        dtm_odt.write(vals) if dtm_odt else dtm_odt.create(vals)



        
    

