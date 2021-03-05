# -*- coding: utf-8 -*-

{
    "name": "Mejoras Modulo Fabricacion",
    "version": "1.0",
    "author": "Develoop Software",
    "category": "CRM",
    "summary": "Agrega mejoras y personalizaciones al modulo Fabricacion",
    'website': "https://www.develoop.net/",
    'description': """
        - Agrega mejoras y personalizaciones al modulo Fabricacion. """,
    "depends": ["mrp", "product", "stock", "sale"],
    "data": [
        'views/custom_production_improve_views.xml',
        'views/custom_production_stock_value_view.xml',
        'report/report_comprobacion_incidencias_print.xml',
        'report/comprobacion_incidencias_templates.xml'
    ],
    "demo": [],
    "images": ['static/description/icon.png'],
    "installable": True,
    "application": True,
    "auto_install": False,
}