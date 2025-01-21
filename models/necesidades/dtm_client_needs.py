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
        get_cotizacion = self.env['dtm.cotizaciones'].search([],order="no_cotizacion desc",limit=1)
        return str(int(get_cotizacion.no_cotizacion) + 1)

    no_cotizacion = fields.Char(string="No. De Necesidad", default=_default_init)

    cliente_ids = fields.Many2one("res.partner",string="Cliente", readonly=False, required=True, store=True)

    atencion = fields.Many2many("dtm.contactos.anexos",string="Nombre del requisitor", readonly=False)
    d = datetime
    date = fields.Date(string="Fecha" ,default= d.datetime.today(), readonly=True)   

    attachment_ids = fields.Many2many("dtm.documentos.anexos",string="Anexos", readonly=False)

    telefono = fields.Char(string="Telefono(s)", readonly=True , compute="_compute_onchange",store=True)

    correo = fields.Char(string = "email(s)", readonly=True, compute="_compute_onchange", store=True)

    cotizacion = fields.Boolean(default=False)

    nivel = fields.Selection(string="Nivel", default="uno",selection=[('uno',1),('dos',2),('tres',3)])

    # Datos para medición de metricos
    status = fields.Integer()
    notes = fields.Text()
#------------------------ Documentos Anexos------------------------
    list_materials_ids = fields.One2many('cot.list.material', 'model_id',readonly=False)

#-----------------------------------------------------
    message_ids = fields.One2many()    
    has_message = fields.Boolean()
    body = fields.Html()

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
                })
            else:
                get_cot_list.create({
                    'id_need': item.id,
                    'descripcion': item.name,
                    'cantidad': item.cantidad,
                    'model_id':get_cotizacion.id,
                })

    def action_prediseno(self):
        pass




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



class ListMaterial(models.Model):
    _name = "cot.list.material"
    _description = "Modelo para almacenar los materiales para las precotizaciones"
    
    model_id = fields.Many2one("dtm.client.needs")
    name = fields.Char(string="Producto o servicio", readonly=False, required=True)
    descripcion = fields.Text(string="Descripción", readonly=False, required=True)
    cantidad = fields.Integer(string="Cantidad", readonly=False, required=True)
    attachment_ids = fields.Many2many("dtm.documentos.anexos", string="Archivos", readonly=False)

    #material_serv_ids = fields.Many2many("dtm.list.material.producto")


    @api.onchange('material_serv_ids')
    def _onchange_material_serv_ids(self):
        lines = []
        for result in self.material_serv_ids:
            line = (1,result.id,{})
            lines.append(line)
        self.material_serv_ids = lines

        
    

