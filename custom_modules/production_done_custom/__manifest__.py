# -*- coding: utf-8 -*-

{
    "name": "Acción luego de fabricación completada",
    "version": "1.0",
    "author": "Develoop Software",
    "category": "CRM",
    "summary": "Acción luego de fabricación completada",
    'website': "https://www.develoop.net/",
    'description': """
        - Cambia la etapa del CRM cuando los productos son fabricados . """,
    "depends": ["mrp", "crm","custom_production_improve"],
    "data": [
        'views/production_custom_done.xml',
    ],
    "demo": [],
    "images": ['static/description/icon.png'],
    "installable": True,
    "application": True,
    "auto_install": False,
}