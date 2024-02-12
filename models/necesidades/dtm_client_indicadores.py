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
    uno_days = fields.Integer(string="Total")
    uno_sin = fields.Integer(string="Sin cotizaciòn")
    uno_pasadas = fields.Integer(string="Pasadas")
    uno_con = fields.Integer(string="Con cotización")
    uno_fecha_caducada = fields.Integer(string="Mayor a 2 dias")
    uno_percent = fields.Float(string="%")
    dos_days = fields.Integer(string="Total")
    dos_sin = fields.Integer(string="Sin cotizaciòn")
    dos_pasadas = fields.Integer(string="Pasadas")
    dos_fecha_caducada = fields.Integer(string="Mayor a 5 dias")
    dos_percent = fields.Float(string="%")
    dos_con = fields.Integer(string="Con cotización")
    tres_days = fields.Integer(string="Total")
    tres_sin = fields.Integer(string="Sin cotizaciòn")
    tres_pasadas = fields.Integer(string="Pasadas")
    tres_fecha_caducada = fields.Integer(string="Mayor a 12 dias")
    tres_percent = fields.Float(string="%")
    tres_con = fields.Integer(string="Con cotización")
    total = fields.Integer(string="Total")
    sin_cotizacion = fields.Float(string="Sin Cotización")

    def consultar(self):
        pass

    def action_ejecutar(self):
        print("Ejecutando")
        inicial = int(self.fecha_inicial.strftime("%j"))
        final = int(self.fecha_final.strftime("%j"))
        get_cn = self.env['dtm.client.needs'].search([])
        map_uno = {"fecha_cad":[],"pasadas":[],"sin_cotizacion":[],"con_cotizacion":[]}
        map_dos = {"fecha_cad":[],"pasadas":[],"sin_cotizacion":[],"con_cotizacion":[]}
        map_tres = {"fecha_cad":[],"pasadas":[],"sin_cotizacion":[],"con_cotizacion":[]}
        for result in get_cn:
            day = int(result.date.strftime("%j"))

            if result.nivel == "uno":
                if day > inicial and day < final:
                    if result.status < 3 and result.cotizacion:
                        map_uno["con_cotizacion"].append(result.no_cotizacion)
                    elif not result.cotizacion:
                        map_uno["sin_cotizacion"].append(result.no_cotizacion)
                    else:
                        map_uno["fecha_cad"].append(result.no_cotizacion)
                elif result.status < inicial and not result.cotizacion:
                    map_uno["pasadas"].append(result.no_cotizacion)

            if result.nivel == "dos":
                if day > inicial and day < final:
                    if result.status <= 5  and result.cotizacion:
                        map_dos["con_cotizacion"].append(result.no_cotizacion)
                    elif not result.cotizacion:
                        map_dos["sin_cotizacion"].append(result.no_cotizacion)
                    else:
                        map_dos["fecha_cad"].append(result.no_cotizacion)
                elif result.status < inicial and not result.cotizacion:
                    map_dos["pasadas"].append(result.no_cotizacion)

            if result.nivel == "tres":
                if day > inicial and day < final:
                    if result.status < 12 and result.cotizacion:
                        map_tres["con_cotizacion"].append(result.no_cotizacion)
                    elif not result.cotizacion:
                        map_tres["sin_cotizacion"].append(result.no_cotizacion)
                    else:
                        map_tres["fecha_cad"].append(result.no_cotizacion)
                elif result.status < inicial and not result.cotizacion:
                    map_tres["pasadas"].append(result.no_cotizacion)

        self.uno_pasadas = len(map_uno.get("pasadas"))
        self.uno_sin = len(map_uno.get("sin_cotizacion"))
        self.uno_con = len(map_uno.get("con_cotizacion"))
        self.uno_fecha_caducada = len(map_uno.get("fecha_cad"))
        self.uno_days = self.uno_pasadas + self.uno_sin + self.uno_con + self.uno_fecha_caducada

        self.dos_pasadas = len(map_dos.get("pasadas"))
        self.dos_sin = len(map_dos.get("sin_cotizacion"))
        self.dos_con = len(map_dos.get("con_cotizacion"))
        self.dos_fecha_caducada = len(map_dos.get("fecha_cad"))
        self.dos_days = self.dos_pasadas + self.dos_sin + self.dos_con + self.dos_fecha_caducada

        self.tres_pasadas = len(map_tres.get("pasadas"))
        self.tres_sin = len(map_tres.get("sin_cotizacion"))
        self.tres_con = len(map_tres.get("con_cotizacion"))
        self.tres_fecha_caducada = len(map_tres.get("fecha_cad"))
        self.tres_days = self.tres_pasadas + self.tres_sin + self.tres_con + self.tres_fecha_caducada



        self.total = self.uno_days + self.dos_days + self.tres_days
        self.sin_cotizacion = self.uno_pasadas + self.dos_pasadas + self.tres_pasadas
        # Porcentajes
        self.uno_percent = (100*self.uno_days)/ self.total
        self.dos_percent = (100*self.dos_days)/ self.total
        self.tres_percent = (100*self.tres_days)/ self.total




    def action_grafica(self):
        self.env.cr.execute("DELETE FROM dtm_client_graph")
        self.env.cr.execute("INSERT INTO dtm_client_graph (id, nombre, cantidad, porcentaje) VALUES (1, '0 - 2 días', "+str(self.uno_days)+", "+str(self.uno_percent)+")")
        self.env.cr.execute("INSERT INTO dtm_client_graph (id, nombre, cantidad, porcentaje) VALUES (2, '3 - 5 días', "+str(self.dos_days)+", "+str(self.dos_percent)+")")
        self.env.cr.execute("INSERT INTO dtm_client_graph (id, nombre, cantidad, porcentaje) VALUES (3, '5 - + días', "+str(self.tres_days)+", "+str(self.tres_percent)+")")

class Datos(models.Model):
    _name = "dtm.client.indicadores.datos"
    _description ="Tabla para guardar los datos de los indicadores"

    model_id = fields.Many2one("dtm.client.indicadores")
     #Indicadores
    status = fields.Integer()
    uno_days = fields.Integer()
    dos_days = fields.Integer()
    tres_days = fields.Integer()
    total = fields.Integer()
    uno_percent = fields.Float()
    dos_percent = fields.Float()
    tres_percent = fields.Float()
