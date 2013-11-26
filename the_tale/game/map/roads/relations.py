# coding: utf-8

from rels.django import DjangoEnum

class PATH_DIRECTION(DjangoEnum):
    records = ( ('LEFT',  'l', u'лево'),
                 ('RIGHT', 'r', u'право'),
                 ('UP',    'u', u'верх'),
                 ('DOWN',  'd', u'низ') )
