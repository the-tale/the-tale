# coding: utf-8
import os

from dext.utils.app_settings import app_settings

from game.balance import constants as c

APP_DIR = os.path.abspath(os.path.dirname(__file__))

class EQUIP_TYPE:
    NONE = 1
    WEAPON = 2
    PLATE = 3
    AMULET = 4
    HELMET = 5
    CLOAK = 6

    SHOULDERS = 7
    GLOVES = 8
    PANTS = 9
    BOOTS = 10


EQUIP_TYPE_CHOICES = ( (EQUIP_TYPE.NONE, u'не экипируется'),
                       (EQUIP_TYPE.WEAPON, u'оружие'),
                       (EQUIP_TYPE.PLATE, u'броня'),
                       (EQUIP_TYPE.AMULET, u'амулет'),
                       (EQUIP_TYPE.HELMET, u'шлем'),
                       (EQUIP_TYPE.CLOAK, u'плащ') )

EQUIP_TYPE_STR_2_ID = {'none': EQUIP_TYPE.NONE,
                       'weapon': EQUIP_TYPE.WEAPON,
                       'plate': EQUIP_TYPE.PLATE,
                       'amulet': EQUIP_TYPE.AMULET,
                       'helmet': EQUIP_TYPE.HELMET,
                       'cloak': EQUIP_TYPE.CLOAK,
                       'shoulders': EQUIP_TYPE.SHOULDERS,
                       'gloves': EQUIP_TYPE.GLOVES,
                       'pants': EQUIP_TYPE.PANTS,
                       'boots': EQUIP_TYPE.BOOTS}


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

class RARITY_TYPE:
    NORMAL = 0
    RARE = 1
    EPIC = 2

RARITY_TYPE_STR_2_ID = {'normal': RARITY_TYPE.NORMAL,
                        'rare': RARITY_TYPE.RARE,
                        'epic': RARITY_TYPE.EPIC}

RARITY_TYPE_2_PRIORITY = { RARITY_TYPE.NORMAL: c.NORMAL_LOOT_PROBABILITY,
                           RARITY_TYPE.RARE: c.RARE_LOOT_PROBABILITY,
                           RARITY_TYPE.EPIC : c.EPIC_LOOT_PROBABILITY  }


artifacts_settings = app_settings( 'ARTIFACTS',
                                   ARTIFACTS_STORAGE=os.path.join(APP_DIR, 'fixtures', 'artifacts.xls'),
                                   LOOT_STORAGE=os.path.join(APP_DIR, 'fixtures', 'loot.xls'),
                                   TEST_STORAGE=os.path.join(APP_DIR, 'fixtures', 'test.xls'),
                                   INFINITY_ARTIFACT_LEVEL=999999999)
