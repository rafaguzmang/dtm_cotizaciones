from odoo import api,fields,models
from datetime import datetime


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
    


    





    
    
   
    
        

   


    




