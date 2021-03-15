# -*- coding: utf-8 -*-

{
    'name': 'Calendar Improve Save Cost',
    'version': '1.0.0.0',
    'author': 'Develoop Software S.A.',
    'category': 'Develoop',
    'summary': 'Boton para guardar los costos desde el calendario',
    'website': 'https://www.develoop.net/',
    'description': """
        Agrega un nuevo boton en el calendario para mejorar el guardado de costos.
        """,
    'depends': ['base', 'calendar', 'purchase', 'account'],
    'data': [
        'views/calendar_button_save_cost_view.xml'
    ],
    "demo": [],
    "images": ['static/description/icon.png'],
    "installable": True
}