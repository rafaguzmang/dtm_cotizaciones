{
    "name":"dtm_cotizaciones",
    "description":"Requerimientos del cliente, cotizaciones",
    "depends":["mail","contacts","dtm_odt_interna","web"],
    "data":[
        # Security
        'security/res_groups.xml',
        'security/ir.model.access.csv',

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
        'views/dtm_cotizaciones_recotizacion_view.xml',
        'views/dtm_cotizaciones_encuesta_view.xml',
        'views/dtm_cotizaciones_versiones_view.xml',
        'views/dtm_necesidades_owl_view.xml',
        # Data
        # 'data/cotizacion_email_template.xml',

    #     Reports
        'reports/cotizacion_formato.xml',
        'reports/cotizacion_formato_mtd.xml'
    ],
    'assets': {
        'web.assets_backend': [
            # CSS
            'dtm_cotizaciones/static/src/css/necesidades_cliente.css',
            'dtm_cotizaciones/static/src/css/styles.css',
            'dtm_cotizaciones/static/src/css/necesidades_modal.css',
            # XML
            'dtm_cotizaciones/static/src/xml/indicadores.xml',
            'dtm_cotizaciones/static/src/xml/necesidades_cliente.xml',
            'dtm_cotizaciones/static/src/xml/modals/necesidades_modal.xml',
            # JS
            'dtm_cotizaciones/static/src/js/indicadores.js',
            'dtm_cotizaciones/static/src/js/necesidades_cliente.js',
            'dtm_cotizaciones/static/src/js/modals/necesidades_modal.js',
        ],
    },
    'license': 'LGPL-3',
}
