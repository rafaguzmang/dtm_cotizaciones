{
    "name":"dtm_cotizaciones",
    "description":"Requerimientos del cliente, cotizaciones",
    "depends":["mail"],
    "data":[
        'security/ir.model.access.csv',
        'views/dtm_client_needs_view.xml',
        'views/dtm_documentos_anexos_view.xml',
        'views/dtm_precotizacion_view.xml',
        # 'views/dtm_list_material_producto_view.xml',
        'views/dtm_requerimientos_view.xml'
        # 'views/dtm_herencia_view.xml'
    ]
}
