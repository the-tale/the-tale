# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from utg import words as utg_words
from utg import constructors as utg_constructors
from utg.relations import WORD_TYPE

from the_tale.linguistics import relations


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


_construct_utg_name_form = lambda v: (v.utg_name_form, v.linguistics_restrictions())
_construct_number = lambda v: (utg_constructors.construct_integer(int(v)), [])
_construct_text = lambda v: (utg_words.WordForm(utg_words.Word(type=WORD_TYPE.TEXT, forms=(v,))), [])


class VARIABLE_TYPE(DjangoEnum):
    verificator = Column(unique=False, no_index=True)
    constructor = Column(unique=False, no_index=True)
    restrictions = Column(unique=False, no_index=True)

    records = ( ('HERO', 0, u'герой', VARIABLE_VERIFICATOR.PERSON, _construct_utg_name_form, (relations.TEMPLATE_RESTRICTION_GROUP.GENDER,
                                                                                              relations.TEMPLATE_RESTRICTION_GROUP.RACE,
                                                                                              relations.TEMPLATE_RESTRICTION_GROUP.HABIT_HONOR,
                                                                                              relations.TEMPLATE_RESTRICTION_GROUP.HABIT_PEACEFULNESS,
                                                                                              relations.TEMPLATE_RESTRICTION_GROUP.ARCHETYPE,
                                                                                              relations.TEMPLATE_RESTRICTION_GROUP.TERRAIN,
                                                                                              relations.TEMPLATE_RESTRICTION_GROUP.ACTION_TYPE)),
                ('NUMBER', 1, u'число', VARIABLE_VERIFICATOR.NUMBER, _construct_number, ()),
                ('PLACE', 2, u'город', VARIABLE_VERIFICATOR.PLACE, _construct_utg_name_form, (relations.TEMPLATE_RESTRICTION_GROUP.CITY_MODIFIER,
                                                                                              relations.TEMPLATE_RESTRICTION_GROUP.HABIT_HONOR,
                                                                                              relations.TEMPLATE_RESTRICTION_GROUP.HABIT_PEACEFULNESS,
                                                                                              relations.TEMPLATE_RESTRICTION_GROUP.TERRAIN,
                                                                                              relations.TEMPLATE_RESTRICTION_GROUP.BUILDING_TYPE,
                                                                                              relations.TEMPLATE_RESTRICTION_GROUP.RACE)),
                ('PERSON', 3, u'NPC', VARIABLE_VERIFICATOR.PERSON, _construct_utg_name_form, (relations.TEMPLATE_RESTRICTION_GROUP.PERSON_TYPE,
                                                                                              relations.TEMPLATE_RESTRICTION_GROUP.GENDER,
                                                                                              relations.TEMPLATE_RESTRICTION_GROUP.RACE)),
                ('ARTIFACT', 4, u'артефакт', VARIABLE_VERIFICATOR.ITEM, _construct_utg_name_form, (relations.TEMPLATE_RESTRICTION_GROUP.ARTIFACT_TYPE,
                                                                                                   relations.TEMPLATE_RESTRICTION_GROUP.ARTIFACT_POWER_TYPE,
                                                                                                   relations.TEMPLATE_RESTRICTION_GROUP.ARTIFACT_RARITY,
                                                                                                   relations.TEMPLATE_RESTRICTION_GROUP.ARTIFACT_EFFECT,
                                                                                                   relations.TEMPLATE_RESTRICTION_GROUP.ARTIFACT)),
                ('MOB', 5, u'монстр', VARIABLE_VERIFICATOR.PERSON, _construct_utg_name_form, (relations.TEMPLATE_RESTRICTION_GROUP.MOB_TYPE,
                                                                                              relations.TEMPLATE_RESTRICTION_GROUP.MOB,
                                                                                              relations.TEMPLATE_RESTRICTION_GROUP.ARCHETYPE)),
                ('TEXT', 6, u'текст', VARIABLE_VERIFICATOR.TEXT, _construct_text, ()),
                ('ACTOR', 7, u'герой, монстр или спутник', VARIABLE_VERIFICATOR.PERSON, _construct_utg_name_form, (relations.TEMPLATE_RESTRICTION_GROUP.GENDER,
                                                                                                                   relations.TEMPLATE_RESTRICTION_GROUP.RACE,
                                                                                                                   relations.TEMPLATE_RESTRICTION_GROUP.HABIT_HONOR,
                                                                                                                   relations.TEMPLATE_RESTRICTION_GROUP.HABIT_PEACEFULNESS,
                                                                                                                   relations.TEMPLATE_RESTRICTION_GROUP.MOB,
                                                                                                                   relations.TEMPLATE_RESTRICTION_GROUP.MOB_TYPE,
                                                                                                                   relations.TEMPLATE_RESTRICTION_GROUP.COMPANION,
                                                                                                                   relations.TEMPLATE_RESTRICTION_GROUP.COMPANION_TYPE,
                                                                                                                   relations.TEMPLATE_RESTRICTION_GROUP.COMPANION_DEDICATION,
                                                                                                                   relations.TEMPLATE_RESTRICTION_GROUP.COMPANION_RARITY,
                                                                                                                   relations.TEMPLATE_RESTRICTION_GROUP.ARCHETYPE,
                                                                                                                   relations.TEMPLATE_RESTRICTION_GROUP.TERRAIN,
                                                                                                                   relations.TEMPLATE_RESTRICTION_GROUP.ACTION_TYPE)),
                ('MODIFIER', 8, u'модификатор города', VARIABLE_VERIFICATOR.MODIFIER, _construct_utg_name_form, (relations.TEMPLATE_RESTRICTION_GROUP.CITY_MODIFIER,)),
                ('RACE', 9, u'раса', VARIABLE_VERIFICATOR.RACE, _construct_utg_name_form, (relations.TEMPLATE_RESTRICTION_GROUP.RACE,)),
                ('COMPANION', 10, u'спутник', VARIABLE_VERIFICATOR.PERSON, _construct_utg_name_form, (relations.TEMPLATE_RESTRICTION_GROUP.COMPANION,
                                                                                                      relations.TEMPLATE_RESTRICTION_GROUP.COMPANION_TYPE,
                                                                                                      relations.TEMPLATE_RESTRICTION_GROUP.COMPANION_DEDICATION,
                                                                                                      relations.TEMPLATE_RESTRICTION_GROUP.COMPANION_RARITY,
                                                                                                      relations.TEMPLATE_RESTRICTION_GROUP.ARCHETYPE)) )

class VARIABLE(DjangoEnum):
    type = Column(unique=False, no_index=True)

    records = ( ('HERO', 'hero', u'герой', VARIABLE_TYPE.HERO),
                ('LEVEL', 'level', u'уровень', VARIABLE_TYPE.NUMBER),
                ('ANTAGONIST_POSITION', 'antagonist_position', u'позиция антагониста', VARIABLE_TYPE.PLACE),
                ('RECEIVER_POSITION', 'receiver_position', u'позиция получателя задания', VARIABLE_TYPE.PLACE),
                ('ANTAGONIST', 'antagonist', u'антагонист', VARIABLE_TYPE.PERSON),
                ('RECEIVER', 'receiver', u'получатель задания', VARIABLE_TYPE.PERSON),
                ('ARTIFACT', 'artifact', u'артефакт', VARIABLE_TYPE.ARTIFACT),
                ('COINS', 'coins', u'монеты', VARIABLE_TYPE.NUMBER),
                ('INITIATOR', 'initiator', u'инициатор задания', VARIABLE_TYPE.PERSON),
                ('INITIATOR_POSITION', 'initiator_position', u'позиция инициатора задания', VARIABLE_TYPE.PLACE),
                ('ITEM', 'item', u'предмет', VARIABLE_TYPE.ARTIFACT),
                ('UNEQUIPPED', 'unequipped', u'снимаемый предмет', VARIABLE_TYPE.ARTIFACT),
                ('EQUIPPED', 'equipped', u'экипируемый предмет', VARIABLE_TYPE.ARTIFACT),
                ('DESTINATION', 'destination', u'пункт назначения', VARIABLE_TYPE.PLACE),
                ('CURRENT_DESTINATION', 'current_destination', u'текущий подпункт назначения', VARIABLE_TYPE.PLACE),
                ('PLACE', 'place', u'город', VARIABLE_TYPE.PLACE),
                ('KILLER', 'killer', u'победитель в pvp', VARIABLE_TYPE.HERO),
                ('VICTIM', 'victim', u'проигравший в pvp', VARIABLE_TYPE.HERO),
                ('DUELIST_1', 'duelist_1', u'1-ый участник pvp', VARIABLE_TYPE.HERO),
                ('DUELIST_2', 'duelist_2', u'2-ый участник pvp', VARIABLE_TYPE.HERO),
                ('DROPPED_ITEM', 'dropped_item', u'выпавший предмет', VARIABLE_TYPE.ARTIFACT),
                ('EXPERIENCE', 'experience', u'опыт', VARIABLE_TYPE.NUMBER),
                ('HEALTH', 'health', u'здоровье', VARIABLE_TYPE.NUMBER),
                ('MOB', 'mob', u'монстр', VARIABLE_TYPE.MOB),
                ('ENERGY', 'energy', u'энергия', VARIABLE_TYPE.NUMBER),
                ('SELL_PRICE', 'sell_price', u'цена продажи', VARIABLE_TYPE.NUMBER),
                ('COINS_DELTA', 'coins_delta', u'разница в монетах', VARIABLE_TYPE.NUMBER),
                ('OLD_ARTIFACT', 'old_artifact', u'старый артефакт', VARIABLE_TYPE.ARTIFACT),
                ('PERSON', 'person', u'советник', VARIABLE_TYPE.PERSON),
                ('DECLINED_BILL', 'declined_bill', u'название не прошедшего закона', VARIABLE_TYPE.TEXT),
                ('BILL', 'bill', u'название закона', VARIABLE_TYPE.TEXT),
                ('NEW_NAME', 'new_name', u'новое название города', VARIABLE_TYPE.PLACE),
                ('OLD_NAME', 'old_name', u'старое название города', VARIABLE_TYPE.PLACE),
                ('NEW_MODIFIER', 'new_modifier', u'новый модификатор города', VARIABLE_TYPE.MODIFIER),
                ('OLD_MODIFIER', 'old_modifier', u'старый модификатор города', VARIABLE_TYPE.MODIFIER),
                ('OLD_RACE', 'old_race', u'старая раса', VARIABLE_TYPE.RACE),
                ('NEW_RACE', 'new_race', u'новая раса', VARIABLE_TYPE.RACE),
                ('PLACE_1', 'place_1', u'1-ый город', VARIABLE_TYPE.PLACE),
                ('PLACE_2', 'place_2', u'2-ой город', VARIABLE_TYPE.PLACE),
                ('RESOURCE_1', 'resource_1', u'1-ый ресурс', VARIABLE_TYPE.TEXT),
                ('RESOURCE_2', 'resource_2', u'2-ой ресурс', VARIABLE_TYPE.TEXT),
                ('TEXT', 'text', u'любой текст', VARIABLE_TYPE.TEXT),
                ('EFFECTIVENESS', 'effectiveness', u'эффективность', VARIABLE_TYPE.NUMBER),
                ('ATTACKER', 'attacker', u'атакующий', VARIABLE_TYPE.ACTOR),
                ('DAMAGE', 'damage', u'урон', VARIABLE_TYPE.NUMBER),
                ('DEFENDER', 'defender', u'защитник', VARIABLE_TYPE.ACTOR),
                ('ACTOR', 'actor', u'актор (герой или монстр)', VARIABLE_TYPE.ACTOR),
                ('CONVERSION', 'conversion', u'информация о конверсии параметров', VARIABLE_TYPE.TEXT),
                ('COMPANION', 'companion', u'спутник', VARIABLE_TYPE.COMPANION),
                ('COMPANION_OWNER', 'companion_owner', u'владелец спутника', VARIABLE_TYPE.ACTOR),
                )
