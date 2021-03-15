# -*- coding: utf-8 -*-

{
    'name': 'Custom Purchase Order Improve',
    'version': '1.0.0.0',
    'author': 'Develoop Software S.A.',
    'category': 'Develoop',
    'summary': 'Modificamos el valor de un campo',
    'website': 'https://www.develoop.net/',
    'description': """
        Modificamos el valor del documento de origen de una compra.
        """,
    'depends': ['base', 'purchase'],
    'data': [
        'views/purchase_order_improve_custom_view.xml'
    ],
    "demo": [],
    "images": ['static/description/icon.png'],
    "installable": True
}