from odoo import api,fields,models
import datetime 
import time
import webbrowser as web
import pyautogui as pg

class Probando():
    def __init__(self,phone,message):
        self.phone = phone
        self.message = message

    def send(self):
        web.open("https://web.whatsapp.com/send?phone={}".format(self.phone))
        time.sleep(10)
        pg.typewrite(self.message)
        time.sleep(3)
        pg.press("enter")
        time.sleep(5)
        pg.hotkey("ctrl","w")
        
#------------------- Clase principal
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
    d = datetime
    date = fields.Date(string="Fecha" ,default= d.datetime.today(), readonly=True)   

    attachment_ids = fields.Many2many("dtm.documentos.anexos",string="Anexos", readonly=False)

    telefono = fields.Char(string="Telefono(s)", readonly=True , compute="_compute_onchange",store=True)

    correo = fields.Char(string = "email(s)", readonly=True, compute="_compute_onchange", store=True)
    
    def get_view(self, view_id=None, view_type='form', **options): #Usar en caso de que se necesite sortear los id
        res = super(ClientNeeds,self).get_view(view_id, view_type,**options)       
    #     no = 1
    #     get_info = self.env['dtm.client.needs'].search([])
    #     for result in get_info:
    #         print("atenciòn",result.atencion.id)
    #         # Borra de las tablas con llave foranea
    #         get_atencion = self.env['dtm.contactos.anexos'].search([("id","=",result.atencion.id)])
    #         for atencion in get_atencion:
    #             self.env.cr.execute("DELETE FROM dtm_contactos_anexos WHERE id="+ str(atencion.id))

    #         get_material = self.env['cot.list.material'].search([("model_id","=",str(result.id))])
    #         for material in get_material:
    #             # print(material.id,material.model_id.id)
    #             self.env.cr.execute("DELETE FROM cot_list_material  WHERE id="+ str(material.id)) 

    #         self.env.cr.execute("UPDATE dtm_client_needs SET id="+str(no) + "WHERE id="+ str(result.id))
    #         # Insert Again
    #         for material in get_material:
    #             self.env.cr.execute("INSERT INTO cot_list_material (id, model_id, cantidad, name, descripcion ) "+
    #                                 "VALUES (" + str(material.id) +", "+str(no)+", "+str(material.cantidad)+", '"+material.name+"', '"+ material.descripcion +"')")
    #         for contacto in get_atencion:
    #             self.env.cr.execute("INSERT INTO dtm_contactos_anexos (id, name, correo, telefono) "+
    #                              "VALUES (" + str(result.id) +", '"+str(contacto.name)+"', '"+contacto.correo+"', '"+ contacto.telefono +"')")
          
    #         no+=1
        return res
    
    

    #--------------Onchange-----------------
    @api.onchange('cliente_ids') # Carga correo y número de telefono de los contactos del campo clientes
    def onchange_cliente_ids(self):
        data = self.env['res.partner'].search([('id','=',self.cliente_ids.id)])
        self.correo = ""
        self.telefono = ""
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

    @api.onchange('atencion') # Carga correo y número de telefono de los contactos del campo atencion
    def _compute_onchange(self): 
        servicio = self.env['dtm.client.needs'].search([])
        for result in servicio:
            if result == self.no_cotizacion:
                self.env.cr.execute("UPDATE  cot_list_material SET no_servicio ='"+self.no_cotizacion+"'  WHERE model_id =" + str(self.id))
                # self.env.cr.execute("UPDATE  dtm_documentos_anexos SET no_servicio = '"+self.no_cotizacion+"'  WHERE no_servicio = '-----'" )
        
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
            


    @api.onchange('cliente_ids') # Carga correo y número de telefono de los contactos del campo atencion
    def _compute_cliente_ids(self):
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

    
    notes = fields.Text()
#------------------------ Documentos Anexos------------------------
    list_materials_ids = fields.One2many('cot.list.material', 'model_id',readonly=False)

#-----------------------------------------------------
    message_ids = fields.One2many()    
    has_message = fields.Boolean()
    body = fields.Html()

    #------------------------------- Función para mandar mensajería -----------------------
    # def message_post(self,*,
    #                  body='', subject=None, message_type='notification',
    #                  email_from=None, author_id=None, parent_id=False,
    #                  subtype_xmlid=None, subtype_id=False, partner_ids=None,
    #                  attachments=None, attachment_ids=None,
    #                  add_sign=True, record_name=
    #                  False,
    #                  **kwargs):
    #     res =  super(ClientNeeds,self).message_post(body=body,subject=subject,message_type=message_type,email_from=email_from,
    #                                                 author_id=author_id,parent_id=parent_id,subtype_xmlid=subtype_xmlid,subtype_id=subtype_id,
    #                                                 partner_ids=partner_ids, attachments=attachments, attachment_ids=attachment_ids,
    #                                                 add_sign=add_sign, record_name=record_name)
    #
    #     data = self.env['mail.followers'].search([('res_id','=',res.res_id),('res_model','=','dtm.client.needs')])
    #     phones = []
    #     for result in data.partner_id:
    #         phone = self.env['res.partner'].search([('id','=',result.id)])
    #         phones.append(phone.phone)
    #
    #     for resul in phones:
    #         # print(res.body[3:len(res.body)-4])
    #         x  = Probando(resul,res.body[3:len(res.body)-4])
    #         x.send()
    #         #Depende de la funcion Probando para mandar la mensajeria vía Whatsapp
    #     return res




class ListMaterial(models.Model):
    _name = "cot.list.material"
    
    model_id = fields.Many2one("dtm.client.needs")
    name = fields.Char(string="Producto o servicio", readonly=False, require=True)
    descripcion = fields.Text(string="Descripción", readonly=False, require=True)
    cantidad = fields.Integer(string="Cantidad", readonly=False, require=True)
    attachment_ids = fields.Many2many("dtm.documentos.anexos", string="Archivos", readonly=False)

    #material_serv_ids = fields.Many2many("dtm.list.material.producto")


    @api.onchange('material_serv_ids')
    def _onchange_material_serv_ids(self):
        # print("self.material_serv_ids",self.material_serv_ids)
        # print("self.model_id",self.model_id)

        get_info = self.env['cot.list.material'].search([('id','=',self.model_id.id)])

        # print('material serv ids',get_info.material_serv_ids)
        lines = []
        for result in self.material_serv_ids:
            # print(result.id)
            line = (1,result.id,{})
            lines.append(line)

        # print(lines)
        self.material_serv_ids = lines

        
    
    @api.model
    def create(self,vals):
        res = super(ListMaterial,self).create(vals)

        get_servicio = self.env['dtm.client.needs'].search([('id','=',vals["model_id"])])
        # print(get_servicio.no_cotizacion,

        self.env['dtm.requerimientos'].create({
            'servicio': get_servicio.no_cotizacion,
            'nombre': vals["name"],
            'cantidad': vals["cantidad"],
            'descripcion': vals["descripcion"],
        })

        return res
