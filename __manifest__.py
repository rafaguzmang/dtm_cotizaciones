{
    "name":"dtm_cotizaciones",
    "description":"Requerimientos del cliente, cotizaciones",
    "depends":["mail"],
    "data":[
        # Security
        'security/ir.model.access.csv',

        # Views
        'views/dtm_client_needs_view.xml',
        'views/dtm_documentos_anexos_view.xml',
        'views/dtm_precotizacion_view.xml',
        'views/dtm_cotizaciones_views.xml',
        'views/dtm_requerimientos_view.xml',

        # Data
        'data/cotizacion_email_template.xml',


    #     Reports
        'reports/cotizacion_formato.xml'
    ]
}
