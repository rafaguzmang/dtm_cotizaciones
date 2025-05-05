{
    "name":"dtm_cotizaciones",
    "description":"Requerimientos del cliente, cotizaciones",
    "depends":["mail","contacts","dtm_odt_interna","web"],
    "data":[
        # Security
        'security/ir.model.access.csv',
        'security/res_groups.xml',
        'security/model_access.xml',

        # Views
        'views/dtm_client_needs_view.xml',
        'views/dtm_documentos_anexos_view.xml',
        'views/dtm_cotizaciones_views.xml',
        'views/dtm_requerimientos_view.xml',
        'views/dtm_client_indicadores_view.xml',
        'views/dtm_client_graph_view.xml',
        'views/dtm_cotizaciones_requerimientos_view.xml',
        'views/dtm_menu_item.xml',
        'views/indicador_view.xml',
        # Data
        # 'data/cotizacion_email_template.xml',

    #     Reports
        'reports/cotizacion_formato.xml',
        'reports/cotizacion_formato_mtd.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'dtm_cotizaciones/static/src/xml/indicadores.xml',
            'dtm_cotizaciones/static/src/js/indicadores.js',
            'dtm_cotizaciones/static/src/css/styles.css',

        ],
    },
    'license': 'LGPL-3',
}
