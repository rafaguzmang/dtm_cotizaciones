import re

from odoo import http
from odoo.http import request
import json

class DtmCotizacionesController(http.Controller):
    @http.route('/dtm_cotizaciones/get_necesidades', type='http', auth='public', csrf=False)
    def get_necesidades(self, **kw):

        get_necesidades = request.env['dtm.client.needs'].sudo().search([])
        result = []
        for record in get_necesidades:
            correos = record.correo.split(';')
            correos_list = []
            for correo in correos:
                correo = re.sub(r'^\s+|\s+$', '', correo)
                if correo not in ['','N/A']:
                    correos_list.append(request.env['res.partner'].sudo().search([('email','=',correo)],limit=1).name)
            if len(correos_list) > 1 and record.cliente_ids.name in correos_list:
                correos_list.remove(record.cliente_ids.name)
            correos.remove('N/A') if len(correos)>1 and 'N/A' in correos else correos
            result.append({
                'no_cotizacion': record.no_cotizacion,
                'cliente_ids': record.cliente_ids.name,
                'atencion': ", ".join(correos_list),
                'date': record.date.strftime('%Y-%m-%d'),
                'create_date': record.create_date.strftime('%Y-%m-%d'),
                'telefono': record.telefono,
                'correo': ", ".join(correos),
                'product_id': ", ".join(record.list_materials_ids.mapped('name')),
                'via_solicitud': record.via_solicitud.capitalize() if record.via_solicitud else "-----",
                'status': "Cotizado" if request.env['dtm.cotizaciones'].search([('no_cotizacion','=',record.no_cotizacion)],limit=1) else "Pendiente",
                # 'attachment_ids': record.attachment_ids.name,
                # 'cotizacion': record.cotizacion,
                # 'nivel': record.nivel,
                # 'prediseno_id': record.prediseno_id.name,
                # 'notes': record.notes,
                # 'list_materials_ids': record.list_materials_ids.name,
                # 'message_ids': record.message_ids.name,
                # 'autorizacion_id': record.autorizacion_id.name,
            })
        
        return request.make_response(
            json.dumps(result),
            headers={
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin':'*',
                }
        )

        
       
    @http.route('/restpartner_client', type='json', auth='public', csrf=False)
    def restpartner_client(self, **kw):
        raw_data = request.httprequest.data
        data = json.loads(raw_data)

        get_partner = request.env['res.partner'].sudo().search([('name','ilike',data['name'])],limit=1)
        print(get_partner.name,get_partner.email,get_partner.phone,get_partner.id)
        result = []
        for record in get_partner:
            result.append({
                'name': record.name,
                'email': record.email,
                'phone': record.phone,
                'id': record.id,
            })

        return result