# coding: utf-8

from rels.django_staff import DjangoEnum

class PATH_DIRECTION(DjangoEnum):
    _records = ( ('LEFT',  'l', u'лево'),
                 ('RIGHT', 'r', u'право'),
                 ('UP',    'u', u'верх'),
                 ('DOWN',  'd', u'низ') )
