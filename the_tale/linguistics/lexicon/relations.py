# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from utg import words as utg_words
from utg import constructors as utg_constructors
from utg.relations import WORD_TYPE


def preprocess_s(row):
    return [var if isinstance(var, tuple) else (var, u'') for var in row]

def s(*substitutions):
    return [preprocess_s(row[i:] + row[:i]) for i, row in enumerate(substitutions)]


class VARIABLE_VERIFICATOR(DjangoEnum):
    utg_type = Column(unique=False, no_index=True, single_type=False)
    substitutions = Column(unique=False, no_index=True)

    records = ( ('PERSON', 0, u'любой персонаж', WORD_TYPE.NOUN, s([u'герой', u'привидение', u'героиня', (u'рыцарь', u'мн')],
                                                                   [u'призрак', u'чудовище', u'русалка', (u'боец', u'мн')],
                                                                   [u'жираф', u'чучело', u'зебра', (u'слон', u'мн')],
                                                                   [u'гусь', u'пугало', u'свинья', (u'волк', u'мн')]  )),

                ('NUMBER', 1, u'число', WORD_TYPE.INTEGER, s([1, 2, 5],
                                                             [21, 23, 25],
                                                             [1001, 1054, 1013])),

                ('PLACE', 2, u'место', WORD_TYPE.NOUN, s([u'Минск', u'Простоквашино', u'Вилейка', u'Барановичи'],
                                                         [u'Тагил', u'Чугуево', u'Рига', u'Афины'],
                                                         [u'Магадан', u'Бородино', u'Уфа', u'Чебоксары'])),

                ('ITEM', 4, u'любой предмет', WORD_TYPE.NOUN, s([u'нож', u'ядро', u'пепельница', u'ножницы'],
                                                                [u'кинжал', u'окно', u'мечта', u'макароны'],
                                                                [u'меч', u'варенье', u'чашка', u'дрова'])),

                ('TEXT', 5, u'любой текст', WORD_TYPE.TEXT, s([u'любой текст'],
                                                              [u'текст текст текст'],
                                                              [u'какой-то текст'])),

                ('MODIFIER', 6, u'модификатор города', WORD_TYPE.NOUN, s([u'форт', u'захолустье', u'святыня', (u'мемориал', u'мн')],
                                                                         [u'замок', u'пристанище', u'земля', (u'колония', u'мн')])),

                ('RACE', 7, u'раса', WORD_TYPE.NOUN, s([u'человек', u'эльф', u'орк', u'гоблин', u'дварф'],
                                                       [u'человек', u'эльф', u'орк', u'гоблин', u'дварф'],
                                                       [u'человек', u'эльф', u'орк', u'гоблин', u'дварф'])) )


_construct_utg_name_form = lambda v: v.utg_name_form
_construct_utg_name = lambda v: utg_words.WordForm(v)
_construct_number = lambda v: utg_constructors.construct_integer(v)
_construct_text = lambda v: utg_words.WordForm(utg_words.Word(type=WORD_TYPE.TEXT, forms=(v,)))

class VARIABLE(DjangoEnum):
    verificator = Column(unique=False, no_index=True)
    constructor = Column(unique=False, no_index=True)

    records = ( ('HERO', 'hero', u'герой', VARIABLE_VERIFICATOR.PERSON, _construct_utg_name_form),
                ('LEVEL', 'level', u'уровень', VARIABLE_VERIFICATOR.NUMBER, _construct_number),
                ('ANTAGONIST_POSITION', 'antagonist_position', u'позиция антаганиста', VARIABLE_VERIFICATOR.PLACE, _construct_utg_name_form),
                ('RECEIVER_POSITION', 'receiver_position', u'позиция получателя задания', VARIABLE_VERIFICATOR.PLACE, _construct_utg_name_form),
                ('ANTAGONIST', 'antagonist', u'антагонист', VARIABLE_VERIFICATOR.PERSON, _construct_utg_name_form),
                ('RECEIVER', 'receiver', u'получатель задания', VARIABLE_VERIFICATOR.PERSON, _construct_utg_name_form),
                ('ARTIFACT', 'artifact', u'артефакт', VARIABLE_VERIFICATOR.ITEM, _construct_utg_name_form),
                ('COINS', 'coins', u'монеты', VARIABLE_VERIFICATOR.NUMBER, _construct_number),
                ('INITIATOR', 'initiator', u'инициатор задания', VARIABLE_VERIFICATOR.PERSON, _construct_utg_name_form),
                ('INITIATOR_POSITION', 'initiator_position', u'позиция инициатора задания', VARIABLE_VERIFICATOR.PLACE, _construct_utg_name_form),
                ('ITEM', 'item', u'предмет', VARIABLE_VERIFICATOR.ITEM, _construct_utg_name_form),
                ('UNEQUIPPED', 'unequipped', u'снимаемый предмет', VARIABLE_VERIFICATOR.ITEM, _construct_utg_name_form),
                ('EQUIPPED', 'equipped', u'экипируемый предмет', VARIABLE_VERIFICATOR.ITEM, _construct_utg_name_form),
                ('DESTINATION', 'destination', u'пункт назначения', VARIABLE_VERIFICATOR.PLACE, _construct_utg_name_form),
                ('CURRENT_DESTINATION', 'current_destination', u'текущий подпункт назначения', VARIABLE_VERIFICATOR.PLACE, _construct_utg_name_form),
                ('PLACE', 'place', u'город', VARIABLE_VERIFICATOR.PLACE, _construct_utg_name_form),
                ('KILLER', 'killer', u'победитель в pvp', VARIABLE_VERIFICATOR.PERSON, _construct_utg_name_form),
                ('VICTIM', 'victim', u'проигравший в pvp', VARIABLE_VERIFICATOR.PERSON, _construct_utg_name_form),
                ('DUELIST_1', 'duelist_1', u'1-ый участник pvp', VARIABLE_VERIFICATOR.PERSON, _construct_utg_name_form),
                ('DUELIST_2', 'duelist_2', u'2-ый участник pvp', VARIABLE_VERIFICATOR.PERSON, _construct_utg_name_form),
                ('DROPPED_ITEM', 'dropped_item', u'выпавший предмет', VARIABLE_VERIFICATOR.ITEM, _construct_utg_name_form),
                ('EXPERIENCE', 'experience', u'опыт', VARIABLE_VERIFICATOR.NUMBER, _construct_number),
                ('HEALTH', 'health', u'здоровье', VARIABLE_VERIFICATOR.NUMBER, _construct_number),
                ('MOB', 'mob', u'монстр', VARIABLE_VERIFICATOR.PERSON, _construct_utg_name_form),
                ('ENERGY', 'energy', u'энергия', VARIABLE_VERIFICATOR.NUMBER, _construct_number),
                ('SELL_PRICE', 'sell_price', u'цена продажи', VARIABLE_VERIFICATOR.NUMBER, _construct_number),
                ('COINS_DELTA', 'coins_delta', u'разница в монетах', VARIABLE_VERIFICATOR.NUMBER, _construct_number),
                ('OLD_ARTIFACT', 'old_artifact', u'старый артефакт', VARIABLE_VERIFICATOR.ITEM, _construct_utg_name_form),
                ('PERSON', 'person', u'советник', VARIABLE_VERIFICATOR.PERSON, _construct_utg_name_form),
                ('DECLINED_BILL', 'declined_bill', u'название не прошедшего закона', VARIABLE_VERIFICATOR.TEXT, _construct_text),
                ('BILL', 'bill', u'название закона', VARIABLE_VERIFICATOR.TEXT, _construct_text),
                ('NEW_NAME', 'new_name', u'новое название города', VARIABLE_VERIFICATOR.PLACE, _construct_utg_name),
                ('OLD_NAME', 'old_name', u'старое название города', VARIABLE_VERIFICATOR.PLACE, _construct_utg_name),
                ('NEW_MODIFIER', 'new_modifier', u'новый модификатор города', VARIABLE_VERIFICATOR.MODIFIER, _construct_utg_name_form),
                ('OLD_MODIFIER', 'old_modifier', u'старый модификатор города', VARIABLE_VERIFICATOR.MODIFIER, _construct_utg_name_form),
                ('OLD_RACE', 'old_race', u'старая раса', VARIABLE_VERIFICATOR.RACE, _construct_utg_name_form),
                ('NEW_RACE', 'new_race', u'новая раса', VARIABLE_VERIFICATOR.RACE, _construct_utg_name_form),
                ('PLACE_1', 'place_1', u'1-ый город', VARIABLE_VERIFICATOR.PLACE, _construct_utg_name_form),
                ('PLACE_2', 'place_2', u'2-ой город', VARIABLE_VERIFICATOR.PLACE, _construct_utg_name_form),
                ('RESOURCE_1', 'resource_1', u'1-ый ресурс', VARIABLE_VERIFICATOR.TEXT, _construct_text),
                ('RESOURCE_2', 'resource_2', u'2-ой ресурс', VARIABLE_VERIFICATOR.TEXT, _construct_text),
                ('TEXT', 'text', u'любой текст', VARIABLE_VERIFICATOR.TEXT, _construct_text),
                ('EFFECTIVENESS', 'effectiveness', u'эффективность', VARIABLE_VERIFICATOR.NUMBER, _construct_number),
                ('ATTACKER', 'attacker', u'атакующий', VARIABLE_VERIFICATOR.PERSON, _construct_utg_name_form),
                ('DAMAGE', 'damage', u'урон', VARIABLE_VERIFICATOR.NUMBER, _construct_number),
                ('DEFENDER', 'defender', u'защитник', VARIABLE_VERIFICATOR.PERSON, _construct_utg_name_form),
                ('ACTOR', 'actor', u'актор (герой или монстр)', VARIABLE_VERIFICATOR.PERSON, _construct_utg_name_form),
                ('CONVERSION', 'conversion', u'информация о конверсии параметров', VARIABLE_VERIFICATOR.TEXT, _construct_text),
                )
