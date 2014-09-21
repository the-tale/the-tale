# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from utg.relations import WORD_TYPE


def preprocess_s(row):
    return [var if isinstance(var, tuple) else (var, ()) for var in row]

def s(*substitutions):
    return [preprocess_s(row[i:] + row[:i]) for i, row in enumerate(substitutions)]


class VARIABLE_VERIFICATOR(DjangoEnum):
    utg_type = Column(unique=False, no_index=True, single_type=False)
    substitutions = Column(unique=False, no_index=True)

    records = ( ('PERSON', 0, u'любой персонаж', WORD_TYPE.NOUN, s([u'герой', u'привидение', u'героиня', (u'рыцарь', u'мн')],
                                                                   [u'призрак', u'чудовище', u'русалка', (u'боец', u'мн')],
                                                                   [u'жираф', u'чучело', u'зебра', (u'слон', u'мн')])),

                ('NUMBER', 1, u'число', WORD_TYPE.INTEGER, s([1, 2, 5],
                                                             [21, 22, 25],
                                                             [1001, 1052, 1025])),

                ('PLACE', 2, u'место', WORD_TYPE.NOUN, s([u'Минск', u'Простоквашино', u'Вилейка', u'Барановичи'],
                                                         [u'Тагил', u'Чугуево', u'Рига', u'Афины'],
                                                         [u'Магадан', u'Бородино', u'Уфа', u'Чебоксары'])),

                ('ITEM', 4, u'любой предмет', WORD_TYPE.NOUN, s([u'нож', u'ядро', u'пепельница', u'ножницы'],
                                                                [u'кинжал', u'окно', u'мечта', u'макароны'],
                                                                [u'меч', u'варенье', u'чашка', u'дрова'])),

                ('TEXT', 5, u'любой текст', None, s([u'любой текст'],
                                                    [u'абракадабра'],
                                                    [u'какой-то текст'])),

                ('MODIFIER', 6, u'модификатор города', WORD_TYPE.NOUN, s([u'форт', u'захолустье', u'святыня', (u'мемориал', u'мн')],
                                                                         [u'замок', u'пристанище', u'земля', (u'колония', u'мн')])),

                ('RACE', 7, u'раса', WORD_TYPE.NOUN, s([u'человек', u'эльф', u'орк', u'гоблин', u'дварф'],
                                                       [u'человек', u'эльф', u'орк', u'гоблин', u'дварф'],
                                                       [u'человек', u'эльф', u'орк', u'гоблин', u'дварф'])) )


class VARIABLE(DjangoEnum):
    verificator = Column(unique=False, no_index=True)

    records = ( ('HERO', 'hero', u'герой', VARIABLE_VERIFICATOR.PERSON),
                ('LEVEL', 'level', u'уровень', VARIABLE_VERIFICATOR.NUMBER),
                ('ANTAGONIST_POSITION', 'antagonist_position', u'1', VARIABLE_VERIFICATOR.PLACE),
                ('RECEIVER_POSITION', 'receiver_position', u'2', VARIABLE_VERIFICATOR.PLACE),
                ('ANTAGONIST', 'antagonist', u'3', VARIABLE_VERIFICATOR.PERSON),
                ('RECEIVER', 'receiver', u'4', VARIABLE_VERIFICATOR.PERSON),
                ('ARTIFACT', 'artifact', u'5', VARIABLE_VERIFICATOR.ITEM),
                ('COINS', 'coins', u'6', VARIABLE_VERIFICATOR.NUMBER),
                ('INITIATOR', 'initiator', u'7', VARIABLE_VERIFICATOR.PERSON),
                ('INITIATOR_POSITION', 'initiator_position', u'8', VARIABLE_VERIFICATOR.PLACE),
                ('ITEM', 'item', u'9', VARIABLE_VERIFICATOR.ITEM),
                ('UNEQUIPPED', 'unequipped', u'10', VARIABLE_VERIFICATOR.ITEM),
                ('EQUIPPED', 'equipped', u'11', VARIABLE_VERIFICATOR.ITEM),
                ('DESTINATION', 'destination', u'12', VARIABLE_VERIFICATOR.PLACE),
                ('CURRENT_DESTINATION', 'current_destination', u'13', VARIABLE_VERIFICATOR.PLACE),
                ('PLACE', 'place', u'14', VARIABLE_VERIFICATOR.PLACE),
                ('KILLER', 'killer', u'15', VARIABLE_VERIFICATOR.PERSON),
                ('VICTIM', 'victim', u'16', VARIABLE_VERIFICATOR.PERSON),
                ('DUELIST_1', 'duelist_1', u'17', VARIABLE_VERIFICATOR.PERSON),
                ('DUELIST_2', 'duelist_2', u'18', VARIABLE_VERIFICATOR.PERSON),
                ('DROPPED_ITEM', 'dropped_item', u'19', VARIABLE_VERIFICATOR.ITEM),
                ('EXPERIENCE', 'experience', u'20', VARIABLE_VERIFICATOR.NUMBER),
                ('HEALTH', 'health', u'21', VARIABLE_VERIFICATOR.NUMBER),
                ('MOB', 'mob', u'22', VARIABLE_VERIFICATOR.PERSON),
                ('ENERGY', 'energy', u'23', VARIABLE_VERIFICATOR.NUMBER),
                ('SELL_PRICE', 'sell_price', u'24', VARIABLE_VERIFICATOR.NUMBER),
                ('COINS_DELTA', 'coins_delta', u'25', VARIABLE_VERIFICATOR.NUMBER),
                ('OLD_ARTIFACT', 'old_artifact', u'26', VARIABLE_VERIFICATOR.ITEM),
                ('PERSON', 'person', u'27', VARIABLE_VERIFICATOR.PERSON),
                ('DECLINED_BILL', 'declined_bill', u'28', VARIABLE_VERIFICATOR.TEXT),
                ('BILL', 'bill', u'29', VARIABLE_VERIFICATOR.TEXT),
                ('NEW_NAME', 'new_name', u'30', VARIABLE_VERIFICATOR.PLACE),
                ('OLD_NAME', 'old_name', u'31', VARIABLE_VERIFICATOR.PLACE),
                ('NEW_MODIFIER', 'new_modifier', u'32', VARIABLE_VERIFICATOR.MODIFIER),
                ('OLD_MODIFIER', 'old_modifier', u'33', VARIABLE_VERIFICATOR.MODIFIER),
                ('OLD_RACE', 'old_race', u'34', VARIABLE_VERIFICATOR.RACE),
                ('NEW_RACE', 'new_race', u'35', VARIABLE_VERIFICATOR.RACE),
                ('PLACE_1', 'place_1', u'36', VARIABLE_VERIFICATOR.PLACE),
                ('PLACE_2', 'place_2', u'37', VARIABLE_VERIFICATOR.PLACE),
                ('RESOURCE_1', 'resource_1', u'38', VARIABLE_VERIFICATOR.TEXT),
                ('RESOURCE_2', 'resource_2', u'39', VARIABLE_VERIFICATOR.TEXT),
                ('TEXT', 'text', u'40', VARIABLE_VERIFICATOR.TEXT),
                ('EFFECTIVENESS', 'effectiveness', u'41', VARIABLE_VERIFICATOR.NUMBER),
                ('ATTACKER', 'attacker', u'42', VARIABLE_VERIFICATOR.PERSON),
                ('DAMAGE', 'damage', u'43', VARIABLE_VERIFICATOR.NUMBER),
                ('DEFENDER', 'defender', u'44', VARIABLE_VERIFICATOR.PERSON),
                ('ACTOR', 'actor', u'45', VARIABLE_VERIFICATOR.PERSON),
                )
