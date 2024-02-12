from odoo import fields,models,api
import datetime



class Indicadores(models.Model):
    _name = "dtm.cotizacion.indicadores"
    _description = "Modelo para indicadores de las cotizaciones"

    fecha_inicial = fields.Date(string="Fecha Inicial")
    fecha_final = fields.Date(string="Fecha final")
    total = fields.Integer(string="Total")


    def action_ejecutar (self):
        print("Ejecutando")
        inicial = int(self.fecha_inicial.strftime("%j"))
        final = int(self.fecha_final.strftime("%j"))
        get_cn = self.env['dtm.cotizaciones'].search([])
        map = {"low":[],"med":[],"hi":[],"pasadas":[],"sin_cotizacion":[]}
        for result in get_cn:
            day = int(result.date.strftime("%j"))
            if day > inicial and day < final :
                print(result.no_cotizacion)
                # if result.status < 3:
                #     map["low"].append( result.no_cotizacion)
                # if result.status >= 3 and result.status <= 5:
                #     map["med"].append(result.no_cotizacion)
                # if result.status > 5:
                #     map["hi"].append(result.no_cotizacion)
            # elif day > inicial and day < final and not result.cotizacion:
            #      map["sin_cotizacion"].append(result.no_cotizacion)
            # elif day > inicial and not result.cotizacion:
            #     map["pasadas"].append(result.no_cotizacion)



