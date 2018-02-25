
import rels

from rels.django import DjangoEnum


class DAMAGE_TYPE(DjangoEnum):
    records = (('TYPE_2', 2, 'колющий'),
               ('TYPE_3', 3, 'кусательный'),
               ('TYPE_4', 4, 'рвущий'),
               ('TYPE_5', 5, 'режущий'),
               ('TYPE_6', 6, 'рубящий'),
               ('TYPE_7', 7, 'ударный'),
               ('TYPE_8', 8, 'энергетический'))


class WEAPON_TYPE(DjangoEnum):
    damage_types = rels.Column(unique=False, no_index=True)

    records = (('NONE', 0, 'нет', ()),
               ('TYPE_1', 1, 'булава', (DAMAGE_TYPE.TYPE_7,)),
               ('TYPE_2', 2, 'дубина', (DAMAGE_TYPE.TYPE_7,)),
               ('TYPE_3', 3, 'катар', (DAMAGE_TYPE.TYPE_2, DAMAGE_TYPE.TYPE_5)),
               ('TYPE_4', 4, 'кинжал', (DAMAGE_TYPE.TYPE_2, DAMAGE_TYPE.TYPE_5)),
               ('TYPE_5', 5, 'кистень', (DAMAGE_TYPE.TYPE_7,)),
               ('TYPE_6', 6, 'копьё', (DAMAGE_TYPE.TYPE_2, DAMAGE_TYPE.TYPE_7)),
               ('TYPE_7', 7, 'меч', (DAMAGE_TYPE.TYPE_2, DAMAGE_TYPE.TYPE_6)),
               ('TYPE_8', 8, 'нож', (DAMAGE_TYPE.TYPE_2, DAMAGE_TYPE.TYPE_5)),
               ('TYPE_9', 9, 'плеть', (DAMAGE_TYPE.TYPE_4, DAMAGE_TYPE.TYPE_7)),
               ('TYPE_10', 10, 'посох', (DAMAGE_TYPE.TYPE_7,)),
               ('TYPE_11', 11, 'сабля', (DAMAGE_TYPE.TYPE_5, DAMAGE_TYPE.TYPE_6)),
               ('TYPE_12', 12, 'топор', (DAMAGE_TYPE.TYPE_6,)),

               ('TYPE_14', 14, 'жвалы', (DAMAGE_TYPE.TYPE_3,)),
               ('TYPE_15', 15, 'клешня', (DAMAGE_TYPE.TYPE_4, DAMAGE_TYPE.TYPE_5)),
               ('TYPE_16', 16, 'клыки', (DAMAGE_TYPE.TYPE_3,)),
               ('TYPE_17', 17, 'клюв', (DAMAGE_TYPE.TYPE_7, DAMAGE_TYPE.TYPE_4)),
               ('TYPE_18', 18, 'когти', (DAMAGE_TYPE.TYPE_4,)),
               ('TYPE_19', 19, 'кулак', (DAMAGE_TYPE.TYPE_7,)),
               ('TYPE_20', 20, 'палка', (DAMAGE_TYPE.TYPE_7,)),
               ('TYPE_21', 21, 'рог', (DAMAGE_TYPE.TYPE_2,)),
               ('TYPE_22', 22, 'рога', (DAMAGE_TYPE.TYPE_2, DAMAGE_TYPE.TYPE_7)),
               ('TYPE_23', 23, 'хопеш', (DAMAGE_TYPE.TYPE_2, DAMAGE_TYPE.TYPE_5, DAMAGE_TYPE.TYPE_6)),
               ('TYPE_24', 24, 'шипы', (DAMAGE_TYPE.TYPE_4, DAMAGE_TYPE.TYPE_2)),
               ('TYPE_25', 25, 'перчатка с когтями', (DAMAGE_TYPE.TYPE_2, DAMAGE_TYPE.TYPE_4)),
               ('TYPE_26', 26, 'пила', (DAMAGE_TYPE.TYPE_6, DAMAGE_TYPE.TYPE_4)),
               ('TYPE_27', 27, 'рукав с лезвием', (DAMAGE_TYPE.TYPE_2, DAMAGE_TYPE.TYPE_4, DAMAGE_TYPE.TYPE_7)),
               ('TYPE_28', 28, 'полэкс', (DAMAGE_TYPE.TYPE_6, DAMAGE_TYPE.TYPE_2)),
               ('TYPE_29', 29, 'жало', (DAMAGE_TYPE.TYPE_2,)),
               ('TYPE_30', 30, 'касание энергетическое', (DAMAGE_TYPE.TYPE_8,)),
               ('TYPE_31', 31, 'хватательная лапа', (DAMAGE_TYPE.TYPE_7, DAMAGE_TYPE.TYPE_4)),
               ('TYPE_32', 32, 'копыто', (DAMAGE_TYPE.TYPE_7,)),
               ('TYPE_33', 33, 'нога', (DAMAGE_TYPE.TYPE_7,)),
               ('TYPE_34', 34, 'серп', (DAMAGE_TYPE.TYPE_5,)),
               ('TYPE_35', 35, 'праща', (DAMAGE_TYPE.TYPE_7,)),
               ('TYPE_36', 36, 'лук', (DAMAGE_TYPE.TYPE_2,)),
               ('TYPE_37', 37, 'арбалет', (DAMAGE_TYPE.TYPE_2,)),
               ('TYPE_38', 38, 'молот', (DAMAGE_TYPE.TYPE_7,)))


class MATERIAL(DjangoEnum):
    records = (('UNKNOWN', 0, 'неизвестен'),
               ('MATERIAL_1', 1, 'кость'),
               ('MATERIAL_2', 2, 'металл'),
               ('MATERIAL_3', 3, 'дерево'),
               ('MATERIAL_4', 4, 'камень'),
               ('MATERIAL_5', 5, 'хитин'),
               ('MATERIAL_6', 6, 'кристалл'),
               ('MATERIAL_7', 7, 'экзотика'),
               ('MATERIAL_8', 8, 'роговое образование'),
               ('MATERIAL_9', 9, 'зуб'),
               ('MATERIAL_10', 10, 'кожа'),
               ('MATERIAL_11', 11, 'бумага'))
