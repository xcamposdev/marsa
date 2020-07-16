# -*- coding: utf-8 -*-
{
    'name': 'Marsa Custom CRM',
    'version': '1.0.0.0',
    'author': 'Develoop Software S.A.',
    'category': 'Marsa',
    'website': 'https://www.develoop.net/',
    'depends': ['crm', 'base','sale'],
    'summary': 'Marsa Custom Functionality',
    'description': """
        Integrate Marsa custom
        """,
    'data': [
        'security/ir.model.access.csv',
    	'views/calculator.xml',
    ],
    'images': ['static/description/icon.png'],
    'demo': [],
    'installable': True,
}
