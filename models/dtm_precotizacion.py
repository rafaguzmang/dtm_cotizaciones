from odoo import api,fields,models
import time
import webbrowser as web
import pyautogui as pg


#------------------Mensajería Whatsapp---------------------------------------
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
        

#-----------------------Clase Principal------------------------------
class Precotizacion(models.Model):
    _name = "dtm.precotizacion"
    _description = "Se hace la precotización con el costo de los servicios"
    _inherit = ["mail.thread","mail.activity.mixin"]
    _rec_name = "no_cotizacion"

    no_cotizacion = fields.Char(readonly=True) 
    cliente_ids = fields.Char(readonly=True) 
    notas = fields.Text()

    def _compute_fill_servicios(self): # Llena el campo servicios_id con los datos de la tabla requerimientos
        requerimientos = self.env['dtm.requerimientos'].search([])
        lines = []
        # self.env.cr("DELETE FROM dtm.requerimientos")
        for slf in self:
            for result in requerimientos:
                if result.servicio == slf.no_cotizacion:
                    line =(4,result.id,{})
                    lines.append(line)
            self.servicios_id = lines

    servicios_id = fields.Many2many('dtm.requerimientos', string='Requerimientos',compute="_compute_fill_servicios",readonly=False ) # Tabla con Nombre,Descripción,Cantidad,Precion Unitario,Precio Total


<<<<<<< HEAD
    precio_total = fields.Float(string="TOTAL", compute="_compute_precio_total",storage=True)
=======
<<<<<<< HEAD
    precio_total = fields.Float(string="TOTAL", compute="_compute_precio_total")
    #precio_total = fields.Float(string="TOTAL")
=======
    precio_total = fields.Float(string="TOTAL")
>>>>>>> 18beeedb5b86ac108f49163c59bc043b8b5bd6b1
>>>>>>> 4df8ecfc6c357b5c8058958b5e7f5beb30c9293c

    @api.depends("servicios_id")
    def _compute_precio_total(self):

        for result in self:
            sum = 0
            for inresult in result.servicios_id:
                # print(inresult.precio_total)
                sum += inresult.precio_total
            result.precio_total = sum



    #------------------------------- Acciones -----------------------

    #------------------------------- Función para mandar mensajería -----------------------
    def message_post(self,*, 
                    body='', subject=None, message_type='notification',
                    email_from=None, author_id=None, parent_id=False,
                    subtype_xmlid=None, subtype_id=False, partner_ids=None,
                    attachments=None, attachment_ids=None,
                    add_sign=True, record_name=
                    False,
                    **kwargs):
        res =  super(Precotizacion,self).message_post(body=body,subject=subject,message_type=message_type,email_from=email_from,
                                                    author_id=author_id,parent_id=parent_id,subtype_xmlid=subtype_xmlid,subtype_id=subtype_id,
                                                    partner_ids=partner_ids, attachments=attachments, attachment_ids=attachment_ids,
                                                    add_sign=add_sign, record_name=record_name)   
        
        #print('res: ',res)

        data = self.env['mail.followers'].search([('res_id','=',res.res_id),('res_model','=','dtm.client.needs')])
        phones = []
        for result in data.partner_id:            
            phone = self.env['res.partner'].search([('id','=',result.id)])
            phones.append(phone.phone)

        for resul in phones:
            # print(res.body[3:len(res.body)-4])
            x  = Probando(resul,res.body[3:len(res.body)-4])
            x.send()
            #Depende de la funcion "Probando", para mandar la mensajeria vía Whatsapp

        return res
    
    def get_view(self, view_id=None, view_type='form', **options):
        res = super(Precotizacion,self).get_view(view_id, view_type,**options)
        # self.material = "algo al carbón"
        get_info = self.env['dtm.client.needs'].search([])
        self.env.cr.execute("DELETE FROM dtm_precotizacion")
        for result in get_info:
            if not str( result.cliente_ids['name']):
                cliente = ""
            else:
                cliente = str( result.cliente_ids['name'])
            self.env.cr.execute("INSERT INTO dtm_precotizacion (id, no_cotizacion, cliente_ids) VALUES ("+ str(result.id) +", '"+ result.no_cotizacion +"','"+cliente+"')")
        return res
    


    





    
    
   
    
        

   


    




