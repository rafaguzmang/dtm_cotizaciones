from odoo import fields,models,api
import datetime

class Indicadores(models.Model):
    _name = "dtm.client.indicadores"
    _description = "Tabla con los indicadores de eficiencia de ventas"

    # datos = fields.One2many("dtm.client.indicadores.datos", "model_id")
    fecha_inicial = fields.Date(string="Fecha Inicial",default=datetime.datetime.now())
    fecha_final = fields.Date(string="Fecha Final", default=datetime.datetime.now())
    fecha_creacion = fields.Date(string="Fecha de Creación",readonly=True)

    status = fields.Integer(string="Status")
    low_days = fields.Integer(string="0 - 2")
    medium_days = fields.Integer(string="3 - 5")
    hi_days = fields.Integer(string="5+")
    total = fields.Integer(string="Total")
    low_percent = fields.Float(string="%")
    medium_percent = fields.Float(string="%")
    hi_percent = fields.Float(string="%")
    sin_cotizacion = fields.Float(string="Sin Cotización")
    pasadas = fields.Char(string="Pasadas")

    def action_ejecutar(self):
        print("Ejecutando")
        inicial = int(self.fecha_inicial.strftime("%j"))
        final = int(self.fecha_final.strftime("%j"))
        get_cn = self.env['dtm.client.needs'].search([])
        map = {"low":[],"med":[],"hi":[],"pasadas":[],"sin_cotizacion":[]}
        for result in get_cn:
            day = int(result.date.strftime("%j"))
            if day > inicial and day < final and result.cotizacion:
                if result.status < 3:
                    map["low"].append( result.no_cotizacion)
                if result.status >= 3 and result.status <= 5:
                    map["med"].append(result.no_cotizacion)
                if result.status > 5:
                    map["hi"].append(result.no_cotizacion)
            elif day > inicial and day < final and not result.cotizacion:
                 map["sin_cotizacion"].append(result.no_cotizacion)
            elif day > inicial and not result.cotizacion:
                map["pasadas"].append(result.no_cotizacion)
        self.low_days = len(map.get("low"))
        self.medium_days = len(map.get("med"))
        self.hi_days = len(map.get("hi"))
        self.total = self.low_days + self.medium_days + self.hi_days
        self.low_percent = (100*self.low_days)/ self.total
        self.medium_percent = (100*self.medium_days)/ self.total
        self.hi_percent = (100*self.hi_days)/ self.total
        self.pasadas = len(map.get("pasadas"))
        self.sin_cotizacion = len(map.get("sin_cotizacion"))

    def action_grafica(self):
        self.env.cr.execute("DELETE FROM dtm_client_graph")
        self.env.cr.execute("INSERT INTO dtm_client_graph (id, nombre, cantidad, porcentaje) VALUES (1, '0 - 2 días', "+str(self.low_days)+", "+str(self.low_percent)+")")
        self.env.cr.execute("INSERT INTO dtm_client_graph (id, nombre, cantidad, porcentaje) VALUES (2, '3 - 5 días', "+str(self.medium_days)+", "+str(self.medium_percent)+")")
        self.env.cr.execute("INSERT INTO dtm_client_graph (id, nombre, cantidad, porcentaje) VALUES (3, '5 - + días', "+str(self.hi_days)+", "+str(self.hi_percent)+")")

class Datos(models.Model):
    _name = "dtm.client.indicadores.datos"
    _description ="Tabla para guardar los datos de los indicadores"

    model_id = fields.Many2one("dtm.client.indicadores")
     #Indicadores
    status = fields.Integer()
    low_days = fields.Integer()
    medium_days = fields.Integer()
    hi_days = fields.Integer()
    total = fields.Integer()
    low_percent = fields.Float()
    medium_percent = fields.Float()
    hi_percent = fields.Float()
