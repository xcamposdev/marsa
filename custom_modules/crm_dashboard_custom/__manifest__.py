# -*- coding: utf-8 -*-
{
    'name': 'CRM Dashboard Custom',
    'version': '1.0.0.0',
    'author': 'Develoop Software S.A.',
    'category': 'CRM',
    'website': 'https://www.develoop.net/',
    'depends': ['crm','base'],
    'summary': 'Reporte CRM Dashboard',
    'description': """
        Reporte Dashboard
        """,
    'data': [
        'security/ir.model.access.csv',
        'report/crm_dashboard_custom.xml',
    ],
    'images': ['static/description/icon.png'],
    'demo': [],
    'installable': True,
}
