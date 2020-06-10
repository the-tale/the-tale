
import smart_imports

smart_imports.all()


def preprocess_s(row):
    return [var if isinstance(var, tuple) else (var, '') for var in row]


def s(*substitutions):
    return [preprocess_s(row[i:] + row[:i]) for i, row in enumerate(substitutions)]


class VARIABLE_VERIFICATOR(rels_django.DjangoEnum):
    utg_type = rels.Column(unique=False, no_index=True, single_type=False)
    substitutions = rels.Column(unique=False, no_index=True)

    records = (('PERSON', 0, 'любой персонаж', utg_relations.WORD_TYPE.NOUN, s(['герой', 'привидение', 'героиня', ('рыцарь', 'мн')],
                                                                               ['призрак', 'чудовище', 'русалка', ('боец', 'мн')],
                                                                               ['жираф', 'чучело', 'зебра', ('слон', 'мн')],
                                                                               ['гусь', 'пугало', 'свинья', ('волк', 'мн')])),

               ('NUMBER', 1, 'число', utg_relations.WORD_TYPE.INTEGER, s([1, 2, 5],
                                                                         [21, 23, 25],
                                                                         [1001, 1054, 1013])),

               ('PLACE', 2, 'место', utg_relations.WORD_TYPE.NOUN, s(['Минск', 'Простоквашино', 'Вилейка', 'Барановичи'],
                                                                     ['Тагил', 'Чугуево', 'Рига', 'Афины'],
                                                                     ['Магадан', 'Бородино', 'Уфа', 'Чебоксары'])),

               # TODO: во время следующей большой переделки добавить одушевлённый артефакт в каждый набор слов (скорее всего мужского рода)
               ('ITEM', 4, 'любой предмет', utg_relations.WORD_TYPE.NOUN, s(['нож', 'ядро', 'пепельница', 'ножницы'],
                                                                            ['кинжал', 'окно', 'мечта', 'макароны'],
                                                                            ['меч', 'варенье', 'чашка', 'дрова'],
                                                                            ['арбалет', 'облако', 'палица', 'нунчаки'])),

               ('TEXT', 5, 'любой текст', utg_relations.WORD_TYPE.TEXT, s(['любой текст'],
                                                                          ['текст текст текст'],
                                                                          ['какой-то текст'])),

               ('MODIFIER', 6, 'модификатор города', utg_relations.WORD_TYPE.NOUN, s(['форт', 'захолустье', 'святыня', ('мемориал', 'мн')],
                                                                                     ['замок', 'пристанище', 'земля', ('колония', 'мн')])),

               ('RACE', 7, 'раса', utg_relations.WORD_TYPE.NOUN, s(['человек', 'эльф', 'орк', 'гоблин', 'дварф'],
                                                                   ['человек', 'эльф', 'орк', 'гоблин', 'дварф'],
                                                                   ['человек', 'эльф', 'орк', 'гоблин', 'дварф'])),

               ('DATE', 8, 'дата в мире игры', utg_relations.WORD_TYPE.TEXT, s(['18 сухого месяца 183 года'])),

               ('TIME', 9, 'время в мире игры', utg_relations.WORD_TYPE.TEXT, s(['9:20'])),

               ('COINS', 10, 'монеты', utg_relations.WORD_TYPE.INTEGER, s([1, 2, 5],
                                                                          [21, 23, 25],
                                                                          [1001, 1054, 1013])),

               ('CLAN', 11, 'гильдия', utg_relations.WORD_TYPE.NOUN, s(['Западная Орда', 'Центральное Информационное Агентство', 'Алый Рассвет', 'Лекари'],
                                                                       ['Корпорация', 'Молот Севера', 'Братство Волка', 'Драконы'],
                                                                       ['Шипастый Череп', 'Возмездие', 'Анархия', 'Хренелли'])), )


def _construct_utg_name_form(value):
    return (value.utg_name_form, value.linguistics_restrictions())


def _construct_number(value):
    return (utg_constructors.construct_integer(int(value)), [])


def _construct_text(value):
    return (utg_words.WordForm(utg_words.Word(type=utg_relations.WORD_TYPE.TEXT, forms=(value,))), [])


def _construct_coins(value):
    value = int(value)

    utg_name = utg_constructors.construct_integer(value)

    # check from greater amount to zero
    for record in reversed(game_relations.COINS_AMOUNT.records):
        if record.minumum <= value:
            sum_restriction = linguistics_restrictions.get(record)
            return (utg_name, [sum_restriction])


class VARIABLE_TYPE(rels_django.DjangoEnum):
    verificator = rels.Column(unique=False, no_index=True)
    constructor = rels.Column(unique=False, no_index=True)
    restrictions = rels.Column(unique=False, no_index=True)
    attributes = rels.Column(unique=False, no_index=True)

    records = (('NUMBER', 1, 'число', VARIABLE_VERIFICATOR.NUMBER, _construct_number, (), ()),
               ('PLACE', 2, 'город', VARIABLE_VERIFICATOR.PLACE, _construct_utg_name_form, (linguistics_restrictions.GROUP.CITY_MODIFIER,
                                                                                            linguistics_restrictions.GROUP.HABIT_HONOR,
                                                                                            linguistics_restrictions.GROUP.HABIT_PEACEFULNESS,
                                                                                            linguistics_restrictions.GROUP.TERRAIN,
                                                                                            linguistics_restrictions.GROUP.META_TERRAIN,
                                                                                            linguistics_restrictions.GROUP.META_HEIGHT,
                                                                                            linguistics_restrictions.GROUP.META_VEGETATION,
                                                                                            linguistics_restrictions.GROUP.BUILDING_TYPE,
                                                                                            linguistics_restrictions.GROUP.RACE,
                                                                                            linguistics_restrictions.GROUP.PLURAL_FORM), ()),
               ('PERSON', 3, 'Мастер или эмиссар', VARIABLE_VERIFICATOR.PERSON, _construct_utg_name_form, (linguistics_restrictions.GROUP.PERSON_TYPE,
                                                                                                           linguistics_restrictions.GROUP.GENDER,
                                                                                                           linguistics_restrictions.GROUP.RACE,
                                                                                                           linguistics_restrictions.GROUP.ACTOR,
                                                                                                           linguistics_restrictions.GROUP.PLURAL_FORM,
                                                                                                           linguistics_restrictions.GROUP.PERSON_PERSONALITY_COSMETIC,
                                                                                                           linguistics_restrictions.GROUP.PERSON_PERSONALITY_PRACTICAL), ()),
               ('ARTIFACT', 4, 'артефакт', VARIABLE_VERIFICATOR.ITEM, _construct_utg_name_form, (linguistics_restrictions.GROUP.ARTIFACT_TYPE,
                                                                                                 linguistics_restrictions.GROUP.ARTIFACT_POWER_TYPE,
                                                                                                 linguistics_restrictions.GROUP.ARTIFACT_RARITY,
                                                                                                 linguistics_restrictions.GROUP.ARTIFACT_EFFECT,
                                                                                                 linguistics_restrictions.GROUP.ARTIFACT,
                                                                                                 linguistics_restrictions.GROUP.PLURAL_FORM,
                                                                                                 linguistics_restrictions.GROUP.WEAPON_TYPE,
                                                                                                 linguistics_restrictions.GROUP.DAMAGE_TYPE,
                                                                                                 linguistics_restrictions.GROUP.MATERIAL), ()),
               ('MOB', 5, 'монстр', VARIABLE_VERIFICATOR.PERSON, _construct_utg_name_form, (linguistics_restrictions.GROUP.MOB_TYPE,
                                                                                            linguistics_restrictions.GROUP.MOB,
                                                                                            linguistics_restrictions.GROUP.ARCHETYPE,
                                                                                            linguistics_restrictions.GROUP.ACTION_TYPE,
                                                                                            linguistics_restrictions.GROUP.COMMUNICATION_VERBAL,
                                                                                            linguistics_restrictions.GROUP.COMMUNICATION_GESTURES,
                                                                                            linguistics_restrictions.GROUP.COMMUNICATION_TELEPATHIC,
                                                                                            linguistics_restrictions.GROUP.INTELLECT_LEVEL,
                                                                                            linguistics_restrictions.GROUP.PLURAL_FORM,
                                                                                            linguistics_restrictions.GROUP.BEING_STRUCTURE,
                                                                                            linguistics_restrictions.GROUP.BEING_FEATURE,
                                                                                            linguistics_restrictions.GROUP.BEING_MOVEMENT,
                                                                                            linguistics_restrictions.GROUP.BEING_BODY,
                                                                                            linguistics_restrictions.GROUP.BEING_SIZE,
                                                                                            linguistics_restrictions.GROUP.BEING_ORIENTATION), ('weapon',)),
               ('TEXT', 6, 'текст', VARIABLE_VERIFICATOR.TEXT, _construct_text, (), ()),

               ('ACTOR', 7, 'герой, монстр или спутник', VARIABLE_VERIFICATOR.PERSON, _construct_utg_name_form, (linguistics_restrictions.GROUP.GENDER,
                                                                                                                 linguistics_restrictions.GROUP.RACE,
                                                                                                                 linguistics_restrictions.GROUP.HABIT_HONOR,
                                                                                                                 linguistics_restrictions.GROUP.HABIT_PEACEFULNESS,
                                                                                                                 linguistics_restrictions.GROUP.MOB,
                                                                                                                 linguistics_restrictions.GROUP.MOB_TYPE,
                                                                                                                 linguistics_restrictions.GROUP.COMPANION,
                                                                                                                 linguistics_restrictions.GROUP.COMPANION_DEDICATION,
                                                                                                                 linguistics_restrictions.GROUP.COMPANION_ABILITY,
                                                                                                                 linguistics_restrictions.GROUP.ARCHETYPE,
                                                                                                                 linguistics_restrictions.GROUP.TERRAIN,
                                                                                                                 linguistics_restrictions.GROUP.META_TERRAIN,
                                                                                                                 linguistics_restrictions.GROUP.META_HEIGHT,
                                                                                                                 linguistics_restrictions.GROUP.META_VEGETATION,
                                                                                                                 linguistics_restrictions.GROUP.ACTION_TYPE,
                                                                                                                 linguistics_restrictions.GROUP.COMMUNICATION_VERBAL,
                                                                                                                 linguistics_restrictions.GROUP.COMMUNICATION_GESTURES,
                                                                                                                 linguistics_restrictions.GROUP.COMMUNICATION_TELEPATHIC,
                                                                                                                 linguistics_restrictions.GROUP.INTELLECT_LEVEL,
                                                                                                                 linguistics_restrictions.GROUP.ACTOR,
                                                                                                                 linguistics_restrictions.GROUP.PLURAL_FORM,
                                                                                                                 linguistics_restrictions.GROUP.COMPANION_EXISTENCE,
                                                                                                                 linguistics_restrictions.GROUP.BEING_STRUCTURE,
                                                                                                                 linguistics_restrictions.GROUP.BEING_FEATURE,
                                                                                                                 linguistics_restrictions.GROUP.BEING_MOVEMENT,
                                                                                                                 linguistics_restrictions.GROUP.BEING_BODY,
                                                                                                                 linguistics_restrictions.GROUP.BEING_SIZE,
                                                                                                                 linguistics_restrictions.GROUP.BEING_ORIENTATION,
                                                                                                                 linguistics_restrictions.GROUP.UPBRINGING,
                                                                                                                 linguistics_restrictions.GROUP.FIRST_DEATH,
                                                                                                                 linguistics_restrictions.GROUP.AGE,
                                                                                                                 linguistics_restrictions.GROUP.CLAN_MEMBERSHIP,
                                                                                                                 linguistics_restrictions.GROUP.PROTECTORAT_OWNERSHIP), ('weapon',)),

               ('MODIFIER', 8, 'модификатор города', VARIABLE_VERIFICATOR.MODIFIER, _construct_utg_name_form, (linguistics_restrictions.GROUP.CITY_MODIFIER,
                                                                                                               linguistics_restrictions.GROUP.PLURAL_FORM), ()),

               ('RACE', 9, 'раса', VARIABLE_VERIFICATOR.RACE, _construct_utg_name_form, (linguistics_restrictions.GROUP.RACE,
                                                                                         linguistics_restrictions.GROUP.PLURAL_FORM), ()),

               ('DATE', 10, 'дата', VARIABLE_VERIFICATOR.DATE, _construct_utg_name_form, (linguistics_restrictions.GROUP.REAL_FEAST,
                                                                                          linguistics_restrictions.GROUP.CALENDAR_DATE,
                                                                                          linguistics_restrictions.GROUP.PHYSICS_DATE,
                                                                                          linguistics_restrictions.GROUP.MONTH,
                                                                                          linguistics_restrictions.GROUP.QUINT,
                                                                                          linguistics_restrictions.GROUP.QUINT_DAY,
                                                                                          linguistics_restrictions.GROUP.DAY_TYPE), ()),

               ('TIME', 11, 'время', VARIABLE_VERIFICATOR.TIME, _construct_utg_name_form, (linguistics_restrictions.GROUP.DAY_TIME,), ()),

               ('COINS', 12, 'монеты', VARIABLE_VERIFICATOR.COINS, _construct_coins, (linguistics_restrictions.GROUP.COINS_AMOUNT,), ()),

               ('CLAN', 13, 'гильдия', VARIABLE_VERIFICATOR.CLAN, _construct_utg_name_form, (), ('abbr', 'motto')),)


class VARIABLE(rels_django.DjangoEnum):
    type = rels.Column(unique=False, no_index=True)

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
               ('DROPPED_ARTIFACT', 'dropped_artifact', 'выкидываемый артефакт', VARIABLE_TYPE.ARTIFACT),
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
               ('TIME', 'time', 'время в мире игры', VARIABLE_TYPE.TIME),
               ('CLAN', 'clan', 'гильдия', VARIABLE_TYPE.CLAN),

               ('HERO__WEAPON', 'hero.weapon', 'оружие героя', VARIABLE_TYPE.ARTIFACT),
               ('KILLER__WEAPON', 'killer.weapon', 'оружие победителя в pvp', VARIABLE_TYPE.ARTIFACT),
               ('VICTIM__WEAPON', 'victim.weapon', 'оружие проигравшего в pvp', VARIABLE_TYPE.ARTIFACT),
               ('DUELIST_1__WEAPON', 'duelist_1.weapon', 'оружие 1 участника pvp', VARIABLE_TYPE.ARTIFACT),
               ('DUELIST_2__WEAPON', 'duelist_2.weapon', 'оружие 2 участника pvp', VARIABLE_TYPE.ARTIFACT),
               ('MOB__WEAPON', 'mob.weapon', 'оружие монстра', VARIABLE_TYPE.ARTIFACT),
               ('ATTACKER__WEAPON', 'attacker.weapon', 'оружие атакующего', VARIABLE_TYPE.ARTIFACT),
               ('DEFENDER__WEAPON', 'defender.weapon', 'оружие защитника', VARIABLE_TYPE.ARTIFACT),
               ('ACTOR__WEAPON', 'actor.weapon', 'оружия актора (героя или монстра)', VARIABLE_TYPE.ARTIFACT),
               ('COMPANION__WEAPON', 'companion.weapon', 'оружие спутника', VARIABLE_TYPE.ARTIFACT),
               ('COMPANION_OWNER__WEAPON', 'companion_owner.weapon', 'оружие владельца спутника', VARIABLE_TYPE.ARTIFACT),
               ('CLAN_ABBR', 'clan.abbr', 'аббревиатура гильдии', VARIABLE_TYPE.TEXT),
               ('CLAN_MOTTO', 'clan.motto', 'девиз гильдии', VARIABLE_TYPE.TEXT),
               )
