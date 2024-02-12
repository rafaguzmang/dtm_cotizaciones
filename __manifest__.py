{
    "name":"dtm_cotizaciones",
    "description":"Requerimientos del cliente, cotizaciones",
    "depends":["mail","contacts"],
    "data":[
        # Security
        'security/ir.model.access.csv',

        # Views
        'views/dtm_client_needs_view.xml',
        'views/dtm_documentos_anexos_view.xml',
        'views/dtm_precotizacion_view.xml',
        'views/dtm_cotizaciones_views.xml',
        'views/dtm_requerimientos_view.xml',
        'views/dtm_client_indicadores_view.xml',
        'views/dtm_client_graph_view.xml',
        'views/dtm_cotizacion_indicadores_view.xml',
        # Data
        'data/cotizacion_email_template.xml',

    #     Reports
        'reports/cotizacion_formato.xml'
    ]
}
