from email.policy import default

from odoo import fields,models,api
from datetime import datetime

class Indicadores(models.Model):
    _name = "dtm.client.indicadores"
    _description = "Tabla con los xml de eficiencia de ventas"

    no_month = fields.Integer()
    month_name = fields.Char(string="Mes")
    cotizaciones = fields.Integer(string="Cotizaciones Totales")
    cotizaciones_aceptadas = fields.Integer(string="Cotizaciones Aceptadas")
    cotizaciones_pendientes = fields.Integer(string="Cotizaciones Pendientes")
    cotizaciones_noaceptadas = fields.Integer(string="Cotizaciones No aceptadas")
    cotizaciones_costo_total = fields.Float(string="Costo Total")
    cotizaciones_costo_aceptado = fields.Float(string="Costo Aprobado")
    costo_dlls = fields.Float(string="Costo Dolar")
    porcentaje = fields.Float(string="%")
    aprovado = fields.Float(default=6.0)

    def get_view(self, view_id=None, view_type='form', **options):
        res = super(Indicadores,self).get_view(view_id, view_type,**options)

        # Lógica para obtener indicadores de Ventas
        for month in range(1,13):
            if month <= int(datetime.today().strftime("%m")):
                # Busca las cotizaciones del mes actual y del mes pasado
                self.env.cr.execute(" SELECT date,po_number,id FROM dtm_cotizaciones WHERE EXTRACT(MONTH FROM date) = "+str(month)+
                                    " AND EXTRACT(YEAR FROM date) = "+datetime.today().strftime("%Y")+";")
                get_cotizaciones = self.env.cr.fetchall()

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
                        'cotizaciones_pendientes':self.cotizaciones_pendientes,
                        'cotizaciones_costo_total':costo_noaceptado + costo_aceptado,
                        'cotizaciones_costo_aceptado':costo_aceptado,
                        'porcentaje': (aceptadas * 1)/len(get_cotizaciones) if len(get_cotizaciones) > 0 else 0,

                    })
                else:
                    get_this.create({
                        'no_month':int(datetime.today().strftime("%m")),
                        'month_name':datetime.today().strftime("%B"),
                        'cotizaciones':len(get_cotizaciones),
                        'cotizaciones_aceptadas':aceptadas,
                        'cotizaciones_costo_total':costo_noaceptado + costo_aceptado,
                        'cotizaciones_costo_aceptado':costo_aceptado,
                        'porcentaje': (aceptadas * 1)/len(get_cotizaciones) if len(get_cotizaciones) > 0 else 0,
                    })


        return res
