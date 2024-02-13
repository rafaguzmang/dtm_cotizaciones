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
    odt_uno = fields.Integer(string="Total")
    odt_con_uno = fields.Integer(string="Con Orden de Compra")
    odt_sin_uno = fields.Integer(string="Sin Orden de Compra")

    dos_days = fields.Integer(string="Total")
    dos_sin = fields.Integer(string="Sin cotizaciòn")
    dos_pasadas = fields.Integer(string="Pasadas")
    dos_fecha_caducada = fields.Integer(string="Mayor a 5 dias")
    dos_percent = fields.Float(string="%")
    dos_con = fields.Integer(string="Con cotización")
    odt_dos = fields.Integer(string="Total")
    odt_con_dos = fields.Integer(string="Con Orden de Compra")
    odt_sin_dos = fields.Integer(string="Sin Orden de Compra")

    tres_days = fields.Integer(string="Total")
    tres_sin = fields.Integer(string="Sin cotizaciòn")
    tres_pasadas = fields.Integer(string="Pasadas")
    tres_fecha_caducada = fields.Integer(string="Mayor a 12 dias")
    tres_percent = fields.Float(string="%")
    tres_con = fields.Integer(string="Con cotización")
    odt_tres = fields.Integer(string="Total")
    odt_con_tres = fields.Integer(string="Con Orden de Compra")
    odt_sin_tres = fields.Integer(string="Sin Orden de Compra")

    total = fields.Integer(string="Total")
    sin_cotizacion = fields.Float(string="Sin Cotización")
    pasadas = fields.Float(string="Pasadas")
    odt = fields.Integer(string="Ordenes de compra")
    odt_con = fields.Integer(string="Con Orden")
    odt_sin = fields.Integer(string="Sin Orden")
    #Notas
    notas1 = fields.Text(string="Nivel 1")
    notas2 = fields.Text(string="Nivel 2")
    notas3 = fields.Text(string="Nivel 3")

    def consultar(self):
        pass

    def action_ejecutar(self):
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

        #Ordenes de compra nivel 1
        map_odt_uno = {"sin":[],"con":[]}
        for orden in map_uno["con_cotizacion"]:
            map_odt_uno["con"].append(orden)

        for orden in map_uno["fecha_cad"]:
            map_odt_uno["sin"].append(orden)

        self.odt_con_uno = len(map_odt_uno.get("con"))
        self.odt_sin_uno =  len(map_odt_uno.get("sin"))
        self.odt_uno =  self.odt_sin_uno + self.odt_con_uno

        #Ordenes de compra nivel 2
        map_odt_dos = {"sin":[],"con":[]}
        for orden in map_dos["con_cotizacion"]:
            map_odt_dos["con"].append(orden)

        for orden in map_dos["fecha_cad"]:
            map_odt_dos["sin"].append(orden)

        self.odt_con_dos = len(map_odt_dos.get("con"))
        self.odt_sin_dos =  len(map_odt_dos.get("sin"))
        self.odt_dos =  self.odt_sin_dos + self.odt_con_dos

        #Ordenes de compra nivel 3
        map_odt_tres = {"sin":[],"con":[]}
        for orden in map_tres["con_cotizacion"]:
            map_odt_tres["con"].append(orden)

        for orden in map_tres["fecha_cad"]:
            map_odt_tres["sin"].append(orden)

        self.odt_con_tres = len(map_odt_tres.get("con"))
        self.odt_sin_tres =  len(map_odt_tres.get("sin"))
        self.odt_tres =  self.odt_sin_tres + self.odt_con_tres

        #Totales
        self.total = self.uno_days + self.dos_days + self.tres_days
        self.sin_cotizacion = self.uno_sin + self.dos_sin + self.tres_sin
        self.pasadas = self.uno_pasadas + self.dos_pasadas + self.tres_pasadas
        self.odt = self.odt_uno + self.odt_dos + self.odt_tres
        self.odt_con = self.odt_con_uno + self.odt_con_dos + self.odt_con_tres
        self.odt_sin = self.odt_sin_uno + self.odt_sin_dos +self.odt_sin_tres

        # Porcentajes
        self.uno_percent = (100*self.uno_days)/ self.total
        self.dos_percent = (100*self.dos_days)/ self.total
        self.tres_percent = (100*self.tres_days)/ self.total




    def action_grafica(self):
        # fecha_in = int(self.fecha_inicial.strftime("%j"))
        # fecha_out = int(self.fecha_final.strftime("%j"))
        # fecha = fecha_out - fecha_in
        uno_porcen = (self.uno_con * 100)/self.uno_days
        dos_porcen = (self.dos_con * 100)/self.dos_days
        tres_porcen = (self.tres_con * 100)/self.tres_days

        self.env.cr.execute("DELETE FROM dtm_client_graph")
        self.env.cr.execute("INSERT INTO dtm_client_graph (id, nombre, cantidad, porcentaje) VALUES (1, 'Nivel 1 Total', "+str(self.uno_con)+", 100)")
        self.env.cr.execute("INSERT INTO dtm_client_graph (id, nombre, cantidad, porcentaje) VALUES (2, 'Nivel 1 Con Cotización', "+str(self.uno_sin)+", "+str(uno_porcen)+")")
        self.env.cr.execute("INSERT INTO dtm_client_graph (id, nombre, cantidad, porcentaje) VALUES (3, 'Nivel 2 Total', "+str(self.dos_con)+", 100)")
        self.env.cr.execute("INSERT INTO dtm_client_graph (id, nombre, cantidad, porcentaje) VALUES (4, 'Nivel 2 Con Cotización', "+str(self.dos_sin)+", "+str(dos_porcen)+")")
        self.env.cr.execute("INSERT INTO dtm_client_graph (id, nombre, cantidad, porcentaje) VALUES (5, 'Nivel 3 Total', "+str(self.tres_con)+", 100)")
        self.env.cr.execute("INSERT INTO dtm_client_graph (id, nombre, cantidad, porcentaje) VALUES (6, 'Nivel 3 Con Cotización', "+str(self.tres_sin)+", "+str(tres_porcen)+")")
        # self.env.cr.execute("INSERT INTO dtm_client_graph (id, nombre, cantidad, porcentaje) VALUES (3, '5 - + días', "+str(self.tres_days)+", "+str(self.tres_percent)+")")

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
