# coding: utf-8

from rels.django import DjangoEnum

class PATH_DIRECTION(DjangoEnum):
    records = ( ('LEFT',  'l', 'лево'),
                 ('RIGHT', 'r', 'право'),
                 ('UP',    'u', 'верх'),
                 ('DOWN',  'd', 'низ') )
