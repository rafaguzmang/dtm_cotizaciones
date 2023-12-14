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
    _inherit = ["mail.thread","mail.activity.mixin"]

    no_cotizacion = fields.Char(readonly=True) 
    cliente_ids = fields.Char(readonly=True) 
    notas = fields.Text()

    def _compute_fill_servicios(self): # llena el campo servicios_id con los datos de la tabla requerimientos
        requerimientos = self.env['dtm.requerimientos'].search([])
        lines = []
        line = (5,0,{})
        for result in requerimientos:
            if result.servicio == self.no_cotizacion:
                line =(4,result.id,{})
                lines.append(line)
        self.servicios_id = lines

    servicios_id = fields.Many2many('dtm.requerimientos', string='Requerimientos',compute="_compute_fill_servicios" )




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
        res =  super(ClientNeeds,self).message_post(body=body,subject=subject,message_type=message_type,email_from=email_from,
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
            print(res.body[3:len(res.body)-4])
            x  = Probando(resul,res.body[3:len(res.body)-4])
            x.send()
            #Depende de la funcion Probanda para mandar la mensajeria vía Whatsapp

        return res
    
    @api.model #--------------------  Llena la tabla con las ordenes de servicio ----------------
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super(Precotizacion, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        get_info = self.env['dtm.client.needs'].search([])
        self.env.cr.execute("DELETE FROM dtm_precotizacion")
        for result in get_info:
            if not str( result.cliente_ids['name']):
                cliente = ""
            else:
                cliente = str( result.cliente_ids['name'])
            self.env.cr.execute("INSERT INTO dtm_precotizacion (no_cotizacion, cliente_ids) VALUES ('"+ result.no_cotizacion +"','"+cliente+"')")
        return res
    


    





    
    
   
    
        

   


    




