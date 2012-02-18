# coding: utf-8

from django.db import models

class EQUIP_TYPE:
    NONE = 1
    WEAPON = 2
    PLATE = 3

EQUIP_TYPE_CHOICES = ( (EQUIP_TYPE.NONE, u'не экипируется'),
                       (EQUIP_TYPE.WEAPON, u'оружие'),
                       (EQUIP_TYPE.PLATE, u'броня') )

EQUIP_TYPE_STR_2_ID = {'none': EQUIP_TYPE.NONE,
                       'weapon': EQUIP_TYPE.WEAPON,
                       'plate': EQUIP_TYPE.PLATE}


class ITEM_TYPE:
    USELESS = 1 
    WEAPON = 2
    ARMOR = 3

ITEM_TYPE_CHOICES = ( (ITEM_TYPE.USELESS, u'безделушка'),
                      (ITEM_TYPE.WEAPON, u'оружие'),
                      (ITEM_TYPE.ARMOR, u'броня') )

ITEM_TYPE_STR_2_ID = {'useless': ITEM_TYPE.USELESS,
                      'weapon': ITEM_TYPE.WEAPON,
                      'armor': ITEM_TYPE.ARMOR}


class ArtifactConstructor(models.Model):

    uuid = models.CharField(null=False, max_length=64, unique=True, db_index=True)
    
    item_type = models.IntegerField(null=False, choices=ITEM_TYPE_CHOICES)
    
    equip_type = models.IntegerField(null=False, choices=EQUIP_TYPE_CHOICES)

    name = models.CharField(null=False, default=u'', max_length=64)
