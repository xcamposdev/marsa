# -*- coding: utf-8 -*-

{
    "name": "Cost Calculation",
    "version": "1.0",
    "author": "Develoop Software",
    "category": "CRM",
    "summary": "Permite realizar calculo de costes",
    'website': "https://www.develoop.net/",
    'description': """
        - Permite realizar calculo de costes """,
    "depends": ["sale",'sale_margin'],
    "data": [
        'views/cost_calculation_custom.xml',
    ],
    "demo": [],
    "images": ['static/description/icon.png'],
    "installable": True,
    "application": True,
    "auto_install": False,
}
