from odoo import fields,models,api
from datetime import datetime

class Indicadores(models.Model):
    _name = "dtm.client.indicadores"
    _description = "Tabla con los indicadores de eficiencia de ventas"

    no_month = fields.Integer()
    month_name = fields.Char(string="Mes")
    cotizaciones = fields.Integer(string="Cotizaciones Totales")
    cotizaciones_aceptadas = fields.Integer(string="Cotizaciones Aceptadas")
    cotizaciones_pendientes = fields.Integer(string="Cotizaciones Pendientes")
    cotizaciones_noaceptadas = fields.Integer(string="Cotizaciones No aceptadas")


    def get_view(self, view_id=None, view_type='form', **options):
        res = super(Indicadores,self).get_view(view_id, view_type,**options)

        for month in range(1,13):

            if int(datetime.today().strftime("%m")) == month:
                # Busca las cotizaciones del mes actual y del mes pasado
                self.env.cr.execute(" SELECT date,po_number,precio_total FROM dtm_cotizaciones WHERE EXTRACT(MONTH FROM date) = "+str(month)+
                                    " AND EXTRACT(YEAR FROM date) = "+datetime.today().strftime("%Y")+";")
                get_cotizaciones = self.env.cr.fetchall()
                if get_cotizaciones:
                    # Obtiene los datos necesarios
                    aceptadas = 0
                    noaceptadas = 0
                    # Ordenes aceptadas y rechazadas
                    for cotizacion in get_cotizaciones:
                        if cotizacion[1] is not None:
                            aceptadas += 1
                        else:
                            noaceptadas += 1

                # Si el mes existe lo actualiza si no lo crea
                get_this = self.env['dtm.client.indicadores'].search([('no_month','=',month)])
                if get_this:
                    get_this.write({
                        'cotizaciones':len(get_cotizaciones),
                        'cotizaciones_aceptadas':aceptadas,
                        'cotizaciones_noaceptadas':noaceptadas,
                        'cotizaciones_pendientes':self.cotizaciones_pendientes,
                    })
                else:
                    get_this.create({
                        'no_month':int(datetime.today().strftime("%m")),
                        'month_name':datetime.today().strftime("%B"),
                        'cotizaciones':len(get_cotizaciones),
                        'cotizaciones_aceptadas':aceptadas,
                        'cotizaciones_noaceptadas':noaceptadas,
                        'cotizaciones_pendientes':self.cotizaciones_pendientes,
                    })


        return res
