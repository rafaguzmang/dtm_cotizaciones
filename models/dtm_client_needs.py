from odoo import api,fields,models
from datetime import datetime
import re


class ClientNeeds(models.Model):
    _name = "dtm.client.needs"
    _inherit = ["mail.thread","mail.activity.mixin"]
    #---------------Function------------------
    def _default_init(self): # Genera número consecutivo de NPI y OT del campo no_cotizacion        
        res=[]
        no = ""       
        no_cotizacion = self.env['dtm.client.needs'].search([]) # Consulta los números de cotización de la tabla de dtm.client.needs
        #print(no_cotizacion)
        if  not no_cotizacion:  
            return "00001"              # Inicializa los números de cotización
        elif not self.no_cotizacion:
            for result in no_cotizacion:
                res.append(result.no_cotizacion)               
            res.sort(reverse=True)
            no = str(int(res[0])+1)
            while len(no) < 5:
                no = "0" + no
            return no

    no_cotizacion = fields.Char(string="No. De Cotización", default=_default_init) 

    cliente_ids = fields.Many2one("res.partner",string="Cliente", readonly=False)

    atencion = fields.Many2many("dtm.contactos.anexos",string="Nombre del requisitor", readonly=False)

    date = fields.Date(string="Fecha" ,default= datetime.today(), readonly=True)   

    attachment_ids = fields.Many2many("dtm.documentos.anexos",string="Anexos", readonly=False)

    #--------------Onchange-----------------
    @api.onchange('atencion') # Carga correo y número de telefono de los contactos del campo atencion
    def _compute_onchange(self): 

        #print(self.no_cotizacion)

        servicio = self.env['dtm.client.needs'].search([])

        for result in servicio:
            if result == self.no_cotizacion:
                self.env.cr.execute("UPDATE  cot_list_material SET no_servicio ='"+self.no_cotizacion+"'  WHERE model_id =" + str(self.id))
                self.env.cr.execute("UPDATE  dtm_documentos_anexos SET no_servicio = '"+self.no_cotizacion+"'  WHERE no_servicio = '-----'" )
        
        self.correo = ""
        self.telefono = ""

        #print(self.atencion)
        for record in self.atencion:
            self.correo = self.correo + record.correo + "; "
            self.telefono = self.telefono + record.telefono + "; "        
        if self.correo:
            self.correo = self.correo[:-2]
        if self.telefono:
            self.telefono = self.telefono[:-2]
    telefono = fields.Char(string="Telefono(s)", readonly=True , compute="_compute_onchange")

    correo = fields.Char(string = "email(s)", readonly=True, compute="_compute_onchange")

    @api.onchange('cliente_ids') # Carga correo y número de telefono de los contactos del campo atencion
    def _compute_cliente_ids(self): 
        print(self.cliente_ids.commercial_company_name)
        if self.cliente_ids.commercial_company_name:
            contactos = self.env['res.partner'].search([])
            self.env.cr.execute("DELETE FROM   dtm_contactos_anexos" )
            for result in contactos:
                if result.commercial_company_name == self.cliente_ids.commercial_company_name:  
                    if result.name == False:
                        result.name = 'N/A'
                    if result.email == False:
                        result.email = 'N/A'
                    if result.phone == False:
                        result.phone = 'N/A'
                    self.env.cr.execute("INSERT INTO dtm_contactos_anexos(name, correo ,telefono) VALUES ('"+ result.name +"','"+ result.email +"','" +result.phone+ "')" )

    
    notes = fields.Text()
#------------------------ Documentos Anexos------------------------
    list_materials_ids = fields.One2many('cot.list.material', 'model_id',readonly=False)

#-----------------------------------------------------

    @api.model
    def create(self, vals):
        
        res = super(ClientNeeds,self).create(vals)

        print('self: ',self)
        print('res: ',res)
        print('vals: ',vals)
        
        
        return res
    
    def write(self, vals):
        res =  super(ClientNeeds,self).write(vals)
        print('self: ',self)
        print('res: ',res)
        print('vals: ',vals)

        get_info = self.env['cot.list.material'].search([('id','=','15')])
        print(get_info)

        for result in get_info:
            print(result.attachment_ids)


        return res
    


class ListMaterial(models.Model):
    _name = "cot.list.material"
    
    model_id = fields.Many2one("dtm.client.needs")
    name = fields.Char(string="Producto o servicio", readonly=False)
    descripcion = fields.Text(string="Descripción", readonly=False)
    cantidad = fields.Integer(string="Cantidad", readonly=False)
    attachment_ids = fields.Many2many("dtm.documentos.anexos", string="Archivos", readonly=False)

    #material_serv_ids = fields.Many2many("dtm.list.material.producto")


    @api.onchange('material_serv_ids')
    def _onchange_material_serv_ids(self):
        print("self.material_serv_ids",self.material_serv_ids)
        print("self.model_id",self.model_id)

        get_info = self.env['cot.list.material'].search([('id','=',self.model_id.id)])

        print('material serv ids',get_info.material_serv_ids)
        lines = []
        for result in self.material_serv_ids:
            print(result.id)
            line = (1,result.id,{})
            lines.append(line)

        print(lines)
        self.material_serv_ids = lines

        
    
    @api.model
    def create(self,vals):
        res = super(ListMaterial,self).create(vals)
   
        print('self: ', self )
        print('vals: ', vals)
        print('res',res)
        print(vals["model_id"])

        get_servicio = self.env['dtm.client.needs'].search([('id','=',vals["model_id"])])
        print(get_servicio.no_cotizacion,
        )
        self.env['dtm.requerimientos'].create({
            'servicio': get_servicio.no_cotizacion,
            'nombre': vals["name"],
            'cantidad': vals["cantidad"],
            'descripcion': vals["descripcion"],
        })

        return res