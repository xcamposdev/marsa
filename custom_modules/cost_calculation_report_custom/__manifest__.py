# -*- coding: utf-8 -*-

{
    "name": "cost calculation custom report",
    "version": "1.0",
    "author": "Develoop Software",
    "category": "CRM",
    "summary": "Reporte de costes custom",
    'website': "https://www.develoop.net/",
    'description': """
        - Reporte de costes custom""",
    "depends": ['sale','sale_margin','purchase'],
    "data": [
        'report/cost_calculation_report.xml',
        'report/report_cost_calculation_templates.xml',
    ],
    "demo": [],
    "images": ['static/description/icon.png'],
    "installable": True,
    "application": True,
    "auto_install": False,
}
