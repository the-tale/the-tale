
from rels import Column
from rels.django import DjangoEnum

from utg import words as utg_words
from utg import constructors as utg_constructors
from utg.relations import WORD_TYPE

from the_tale.linguistics import relations


def preprocess_s(row):
    return [var if isinstance(var, tuple) else (var, '') for var in row]


def s(*substitutions):
    return [preprocess_s(row[i:] + row[:i]) for i, row in enumerate(substitutions)]


class VARIABLE_VERIFICATOR(DjangoEnum):
    utg_type = Column(unique=False, no_index=True, single_type=False)
    substitutions = Column(unique=False, no_index=True)

    records = ( ('PERSON', 0, 'любой персонаж', WORD_TYPE.NOUN, s(['герой', 'привидение', 'героиня', ('рыцарь', 'мн')],
                                                                  ['призрак', 'чудовище', 'русалка', ('боец', 'мн')],
                                                                  ['жираф', 'чучело', 'зебра', ('слон', 'мн')],
                                                                  ['гусь', 'пугало', 'свинья', ('волк', 'мн')]  )),

                ('NUMBER', 1, 'число', WORD_TYPE.INTEGER, s([1, 2, 5],
                                                            [21, 23, 25],
                                                            [1001, 1054, 1013])),

                ('PLACE', 2, 'место', WORD_TYPE.NOUN, s(['Минск', 'Простоквашино', 'Вилейка', 'Барановичи'],
                                                        ['Тагил', 'Чугуево', 'Рига', 'Афины'],
                                                        ['Магадан', 'Бородино', 'Уфа', 'Чебоксары'])),

                # TODO: во время следующей большой переделки добавить одушевлённый артефакт в каждый набор слов (скорее всего мужского рода)
                ('ITEM', 4, 'любой предмет', WORD_TYPE.NOUN, s(['нож', 'ядро', 'пепельница', 'ножницы'],
                                                               ['кинжал', 'окно', 'мечта', 'макароны'],
                                                               ['меч', 'варенье', 'чашка', 'дрова'])),

                ('TEXT', 5, 'любой текст', WORD_TYPE.TEXT, s(['любой текст'],
                                                             ['текст текст текст'],
                                                             ['какой-то текст'])),

                ('MODIFIER', 6, 'модификатор города', WORD_TYPE.NOUN, s(['форт', 'захолустье', 'святыня', ('мемориал', 'мн')],
                                                                        ['замок', 'пристанище', 'земля', ('колония', 'мн')])),

                ('RACE', 7, 'раса', WORD_TYPE.NOUN, s(['человек', 'эльф', 'орк', 'гоблин', 'дварф'],
                                                      ['человек', 'эльф', 'орк', 'гоблин', 'дварф'],
                                                      ['человек', 'эльф', 'орк', 'гоблин', 'дварф'])),

                ('DATE', 8, 'дата в мире игры', WORD_TYPE.TEXT, s(['18 сухого месяца 183 года'])),

                ('TIME', 9, 'время в мире игры', WORD_TYPE.TEXT, s(['9:20'])),

                ('COINS', 10, 'монеты', WORD_TYPE.INTEGER, s([1, 2, 5],
                                                             [21, 23, 25],
                                                             [1001, 1054, 1013])),)


def _construct_utg_name_form(value):
    return (value.utg_name_form, value.linguistics_restrictions())


def _construct_number(value):
    return (utg_constructors.construct_integer(int(value)), [])


def _construct_text(value):
    return (utg_words.WordForm(utg_words.Word(type=WORD_TYPE.TEXT, forms=(value,))), [])


def _construct_coins(value):
    from the_tale.game import relations as game_relations
    from the_tale.linguistics.storage import restrictions_storage

    value = int(value)

    utg_name = utg_constructors.construct_integer(value)

    # check from greater amount to zero
    for record in reversed(game_relations.COINS_AMOUNT.records):
        if record.minumum <= value:
            sum_restriction = restrictions_storage.get_restriction(relations.TEMPLATE_RESTRICTION_GROUP.COINS_AMOUNT, record.value).id
            return (utg_name, [sum_restriction])


class VARIABLE_TYPE(DjangoEnum):
    verificator = Column(unique=False, no_index=True)
    constructor = Column(unique=False, no_index=True)
    restrictions = Column(unique=False, no_index=True)

    records = (('NUMBER', 1, 'число', VARIABLE_VERIFICATOR.NUMBER, _construct_number, ()),
               ('PLACE', 2, 'город', VARIABLE_VERIFICATOR.PLACE, _construct_utg_name_form, (relations.TEMPLATE_RESTRICTION_GROUP.CITY_MODIFIER,
                                                                                            relations.TEMPLATE_RESTRICTION_GROUP.HABIT_HONOR,
                                                                                            relations.TEMPLATE_RESTRICTION_GROUP.HABIT_PEACEFULNESS,
                                                                                            relations.TEMPLATE_RESTRICTION_GROUP.TERRAIN,
                                                                                            relations.TEMPLATE_RESTRICTION_GROUP.META_TERRAIN,
                                                                                            relations.TEMPLATE_RESTRICTION_GROUP.META_HEIGHT,
                                                                                            relations.TEMPLATE_RESTRICTION_GROUP.META_VEGETATION,
                                                                                            relations.TEMPLATE_RESTRICTION_GROUP.BUILDING_TYPE,
                                                                                            relations.TEMPLATE_RESTRICTION_GROUP.RACE,
                                                                                            relations.TEMPLATE_RESTRICTION_GROUP.PLURAL_FORM)),
               ('PERSON', 3, 'NPC', VARIABLE_VERIFICATOR.PERSON, _construct_utg_name_form, (relations.TEMPLATE_RESTRICTION_GROUP.PERSON_TYPE,
                                                                                            relations.TEMPLATE_RESTRICTION_GROUP.GENDER,
                                                                                            relations.TEMPLATE_RESTRICTION_GROUP.RACE,
                                                                                            relations.TEMPLATE_RESTRICTION_GROUP.PLURAL_FORM,
                                                                                            relations.TEMPLATE_RESTRICTION_GROUP.PERSON_PERSONALITY_COSMETIC,
                                                                                            relations.TEMPLATE_RESTRICTION_GROUP.PERSON_PERSONALITY_PRACTICAL)),
               ('ARTIFACT', 4, 'артефакт', VARIABLE_VERIFICATOR.ITEM, _construct_utg_name_form, (relations.TEMPLATE_RESTRICTION_GROUP.ARTIFACT_TYPE,
                                                                                                 relations.TEMPLATE_RESTRICTION_GROUP.ARTIFACT_POWER_TYPE,
                                                                                                 relations.TEMPLATE_RESTRICTION_GROUP.ARTIFACT_RARITY,
                                                                                                 relations.TEMPLATE_RESTRICTION_GROUP.ARTIFACT_EFFECT,
                                                                                                 relations.TEMPLATE_RESTRICTION_GROUP.ARTIFACT,
                                                                                                 relations.TEMPLATE_RESTRICTION_GROUP.PLURAL_FORM)),
               ('MOB', 5, 'монстр', VARIABLE_VERIFICATOR.PERSON, _construct_utg_name_form, (relations.TEMPLATE_RESTRICTION_GROUP.MOB_TYPE,
                                                                                            relations.TEMPLATE_RESTRICTION_GROUP.MOB,
                                                                                            relations.TEMPLATE_RESTRICTION_GROUP.ARCHETYPE,
                                                                                            relations.TEMPLATE_RESTRICTION_GROUP.ACTION_TYPE,
                                                                                            relations.TEMPLATE_RESTRICTION_GROUP.COMMUNICATION_VERBAL,
                                                                                            relations.TEMPLATE_RESTRICTION_GROUP.COMMUNICATION_GESTURES,
                                                                                            relations.TEMPLATE_RESTRICTION_GROUP.COMMUNICATION_TELEPATHIC,
                                                                                            relations.TEMPLATE_RESTRICTION_GROUP.INTELLECT_LEVEL,
                                                                                            relations.TEMPLATE_RESTRICTION_GROUP.PLURAL_FORM)),
               ('TEXT', 6, 'текст', VARIABLE_VERIFICATOR.TEXT, _construct_text, ()),

               ('ACTOR', 7, 'герой, монстр или спутник', VARIABLE_VERIFICATOR.PERSON, _construct_utg_name_form, (relations.TEMPLATE_RESTRICTION_GROUP.GENDER,
                                                                                                                 relations.TEMPLATE_RESTRICTION_GROUP.RACE,
                                                                                                                 relations.TEMPLATE_RESTRICTION_GROUP.HABIT_HONOR,
                                                                                                                 relations.TEMPLATE_RESTRICTION_GROUP.HABIT_PEACEFULNESS,
                                                                                                                 relations.TEMPLATE_RESTRICTION_GROUP.MOB,
                                                                                                                 relations.TEMPLATE_RESTRICTION_GROUP.MOB_TYPE,
                                                                                                                 relations.TEMPLATE_RESTRICTION_GROUP.COMPANION,
                                                                                                                 relations.TEMPLATE_RESTRICTION_GROUP.COMPANION_DEDICATION,
                                                                                                                 relations.TEMPLATE_RESTRICTION_GROUP.COMPANION_ABILITY,
                                                                                                                 relations.TEMPLATE_RESTRICTION_GROUP.ARCHETYPE,
                                                                                                                 relations.TEMPLATE_RESTRICTION_GROUP.TERRAIN,
                                                                                                                 relations.TEMPLATE_RESTRICTION_GROUP.META_TERRAIN,
                                                                                                                 relations.TEMPLATE_RESTRICTION_GROUP.META_HEIGHT,
                                                                                                                 relations.TEMPLATE_RESTRICTION_GROUP.META_VEGETATION,
                                                                                                                 relations.TEMPLATE_RESTRICTION_GROUP.ACTION_TYPE,
                                                                                                                 relations.TEMPLATE_RESTRICTION_GROUP.COMMUNICATION_VERBAL,
                                                                                                                 relations.TEMPLATE_RESTRICTION_GROUP.COMMUNICATION_GESTURES,
                                                                                                                 relations.TEMPLATE_RESTRICTION_GROUP.COMMUNICATION_TELEPATHIC,
                                                                                                                 relations.TEMPLATE_RESTRICTION_GROUP.INTELLECT_LEVEL,
                                                                                                                 relations.TEMPLATE_RESTRICTION_GROUP.ACTOR,
                                                                                                                 relations.TEMPLATE_RESTRICTION_GROUP.PLURAL_FORM,
                                                                                                                 relations.TEMPLATE_RESTRICTION_GROUP.COMPANION_EXISTENCE)),

               ('MODIFIER', 8, 'модификатор города', VARIABLE_VERIFICATOR.MODIFIER, _construct_utg_name_form, (relations.TEMPLATE_RESTRICTION_GROUP.CITY_MODIFIER,
                                                                                                               relations.TEMPLATE_RESTRICTION_GROUP.PLURAL_FORM)),

               ('RACE', 9, 'раса', VARIABLE_VERIFICATOR.RACE, _construct_utg_name_form, (relations.TEMPLATE_RESTRICTION_GROUP.RACE,
                                                                                         relations.TEMPLATE_RESTRICTION_GROUP.PLURAL_FORM)),

               ('DATE', 10, 'дата', VARIABLE_VERIFICATOR.DATE, _construct_utg_name_form, (relations.TEMPLATE_RESTRICTION_GROUP.REAL_FEAST,
                                                                                          relations.TEMPLATE_RESTRICTION_GROUP.CALENDAR_DATE,
                                                                                          relations.TEMPLATE_RESTRICTION_GROUP.PHYSICS_DATE,
                                                                                          relations.TEMPLATE_RESTRICTION_GROUP.MONTH,
                                                                                          relations.TEMPLATE_RESTRICTION_GROUP.QUINT,
                                                                                          relations.TEMPLATE_RESTRICTION_GROUP.QUINT_DAY,
                                                                                          relations.TEMPLATE_RESTRICTION_GROUP.DAY_TYPE)),

               ('TIME', 11, 'время', VARIABLE_VERIFICATOR.TIME, _construct_utg_name_form, (relations.TEMPLATE_RESTRICTION_GROUP.DAY_TIME,)),

               ('COINS', 12, 'монеты', VARIABLE_VERIFICATOR.COINS, _construct_coins, (relations.TEMPLATE_RESTRICTION_GROUP.COINS_AMOUNT,)),)


class VARIABLE(DjangoEnum):
    type = Column(unique=False, no_index=True)

    records = (('HERO', 'hero', 'герой', VARIABLE_TYPE.ACTOR),
               ('LEVEL', 'level', 'уровень', VARIABLE_TYPE.NUMBER),
               ('ANTAGONIST_POSITION', 'antagonist_position', 'позиция антагониста', VARIABLE_TYPE.PLACE),
               ('RECEIVER_POSITION', 'receiver_position', 'позиция получателя задания', VARIABLE_TYPE.PLACE),
               ('ANTAGONIST', 'antagonist', 'антагонист', VARIABLE_TYPE.PERSON),
               ('RECEIVER', 'receiver', 'получатель задания', VARIABLE_TYPE.PERSON),
               ('ARTIFACT', 'artifact', 'артефакт', VARIABLE_TYPE.ARTIFACT),
               ('COINS', 'coins', 'монеты', VARIABLE_TYPE.COINS),
               ('INITIATOR', 'initiator', 'инициатор задания', VARIABLE_TYPE.PERSON),
               ('INITIATOR_POSITION', 'initiator_position', 'позиция инициатора задания', VARIABLE_TYPE.PLACE),
               ('ITEM', 'item', 'предмет', VARIABLE_TYPE.ARTIFACT),
               ('UNEQUIPPED', 'unequipped', 'снимаемый предмет', VARIABLE_TYPE.ARTIFACT),
               ('EQUIPPED', 'equipped', 'экипируемый предмет', VARIABLE_TYPE.ARTIFACT),
               ('DESTINATION', 'destination', 'пункт назначения', VARIABLE_TYPE.PLACE),
               ('CURRENT_DESTINATION', 'current_destination', 'текущий подпункт назначения', VARIABLE_TYPE.PLACE),
               ('PLACE', 'place', 'город', VARIABLE_TYPE.PLACE),
               ('KILLER', 'killer', 'победитель в pvp', VARIABLE_TYPE.ACTOR),
               ('VICTIM', 'victim', 'проигравший в pvp', VARIABLE_TYPE.ACTOR),
               ('DUELIST_1', 'duelist_1', '1-ый участник pvp', VARIABLE_TYPE.ACTOR),
               ('DUELIST_2', 'duelist_2', '2-ый участник pvp', VARIABLE_TYPE.ACTOR),
               ('DROPPED_ITEM', 'dropped_item', 'выпавший предмет', VARIABLE_TYPE.ARTIFACT),
               ('EXPERIENCE', 'experience', 'опыт', VARIABLE_TYPE.NUMBER),
               ('HEALTH', 'health', 'здоровье', VARIABLE_TYPE.NUMBER),
               ('MOB', 'mob', 'монстр', VARIABLE_TYPE.MOB),
               ('ENERGY', 'energy', 'энергия', VARIABLE_TYPE.NUMBER),
               ('SELL_PRICE', 'sell_price', 'цена продажи', VARIABLE_TYPE.COINS),
               ('OLD_ARTIFACT', 'old_artifact', 'старый артефакт', VARIABLE_TYPE.ARTIFACT),
               ('PERSON', 'person', 'мастер', VARIABLE_TYPE.PERSON),
               ('NEW_NAME', 'new_name', 'новое название города', VARIABLE_TYPE.PLACE),
               ('OLD_NAME', 'old_name', 'старое название города', VARIABLE_TYPE.PLACE),
               ('NEW_MODIFIER', 'new_modifier', 'новый модификатор города', VARIABLE_TYPE.MODIFIER),
               ('OLD_MODIFIER', 'old_modifier', 'старый модификатор города', VARIABLE_TYPE.MODIFIER),
               ('OLD_RACE', 'old_race', 'старая раса', VARIABLE_TYPE.RACE),
               ('NEW_RACE', 'new_race', 'новая раса', VARIABLE_TYPE.RACE),
               ('PLACE_1', 'place_1', '1-ый город', VARIABLE_TYPE.PLACE),
               ('PLACE_2', 'place_2', '2-ой город', VARIABLE_TYPE.PLACE),
               ('RESOURCE_1', 'resource_1', '1-ый ресурс', VARIABLE_TYPE.TEXT),
               ('RESOURCE_2', 'resource_2', '2-ой ресурс', VARIABLE_TYPE.TEXT),
               ('TEXT', 'text', 'любой текст', VARIABLE_TYPE.TEXT),
               ('EFFECTIVENESS', 'effectiveness', 'эффективность', VARIABLE_TYPE.NUMBER),
               ('ATTACKER', 'attacker', 'атакующий', VARIABLE_TYPE.ACTOR),
               ('DAMAGE', 'damage', 'урон', VARIABLE_TYPE.NUMBER),
               ('DEFENDER', 'defender', 'защитник', VARIABLE_TYPE.ACTOR),
               ('ACTOR', 'actor', 'актор (герой или монстр)', VARIABLE_TYPE.ACTOR),
               ('CONVERSION', 'conversion', 'информация о конверсии параметров', VARIABLE_TYPE.TEXT),
               ('COMPANION', 'companion', 'спутник', VARIABLE_TYPE.ACTOR),
               ('COMPANION_OWNER', 'companion_owner', 'владелец спутника', VARIABLE_TYPE.ACTOR),
               ('ATTACKER_DAMAGE', 'attacker_damage', 'урон по атакующему', VARIABLE_TYPE.NUMBER),
               ('DATE', 'date', 'дата в мире игры', VARIABLE_TYPE.DATE),
               ('TIME', 'time', 'время в мире игры', VARIABLE_TYPE.TIME), )
