
import smart_imports

smart_imports.all()


class GROUP(rels_django.DjangoEnum):
    static_relation = rels.Column(unique=False, single_type=False, no_index=False)
    sort = rels.Column(unique=False)

    records = (('GENDER', 0, 'пол', game_relations.GENDER, True),
               ('RACE', 1, 'раса', game_relations.RACE, True),
               ('CITY_MODIFIER', 2, 'специализация города', places_modifiers.CITY_MODIFIERS, True),
               ('HABIT_HONOR', 3, 'честь', game_relations.HABIT_HONOR_INTERVAL, True),
               ('HABIT_PEACEFULNESS', 4, 'миролюбие', game_relations.HABIT_PEACEFULNESS_INTERVAL, True),
               ('PERSON_TYPE', 5, 'профессия', persons_relations.PERSON_TYPE, True),

               ('ARTIFACT_TYPE', 6, 'тип экипировки', artifacts_relations.ARTIFACT_TYPE, True),
               ('ARTIFACT_POWER_TYPE', 7, 'тип силы', artifacts_relations.ARTIFACT_POWER_TYPE, True),
               ('ARTIFACT_RARITY', 8, 'редкость артефакта', artifacts_relations.RARITY, True),
               ('ARTIFACT_EFFECT', 9, 'эффект артефакта', artifacts_relations.ARTIFACT_EFFECT, True),

               ('MOB_TYPE', 10, 'тип существа', tt_beings_relations.TYPE, True),

               ('ARTIFACT', 11, 'артефакт', None, True),
               ('MOB', 12, 'монстр', None, True),
               ('COMPANION', 13, 'спутник', None, True),

               ('COMPANION_DEDICATION', 15, 'тип самоотверженности спутника', companions_relations.DEDICATION, True),

               ('ARCHETYPE', 17, 'архетип', game_relations.ARCHETYPE, True),
               ('TERRAIN', 18, 'тип местности', map_relations.TERRAIN, True),
               ('BUILDING_TYPE', 19, 'тип здания', places_relations.BUILDING_TYPE, True),

               ('ACTION_TYPE', 20, 'тип действия героя', actions_relations.ACTION_TYPE, True),

               ('META_TERRAIN', 21, 'мета-тип местности', map_relations.META_TERRAIN, True),
               ('META_HEIGHT', 22, 'мета-тип высоты', map_relations.META_HEIGHT, True),
               ('META_VEGETATION', 23, 'мета-тип растительности', map_relations.META_VEGETATION, True),

               ('COMMUNICATION_VERBAL', 24, 'вербальная коммуникация', tt_beings_relations.COMMUNICATION_VERBAL, True),
               ('COMMUNICATION_GESTURES', 25, 'невербальная коммуникация', tt_beings_relations.COMMUNICATION_GESTURES, True),
               ('COMMUNICATION_TELEPATHIC', 26, 'телепатия', tt_beings_relations.COMMUNICATION_TELEPATHIC, True),

               ('INTELLECT_LEVEL', 27, 'уровень интеллекта', tt_beings_relations.INTELLECT_LEVEL, True),

               ('ACTOR', 28, 'мета-тип существа', game_relations.ACTOR, True),

               ('PLURAL_FORM', 29, 'есть множественное число', relations.WORD_HAS_PLURAL_FORM, True),

               ('PERSON_PERSONALITY_COSMETIC', 30, 'косметическая особенность характера', persons_relations.PERSONALITY_COSMETIC, True),
               ('PERSON_PERSONALITY_PRACTICAL', 31, 'практическая особенность характера', persons_relations.PERSONALITY_PRACTICAL, True),

               ('COMPANION_ABILITY', 32, 'особенность спутника', companions_abilities_effects.ABILITIES, True),

               ('COMPANION_EXISTENCE', 33, 'наличие спутника', companions_relations.COMPANION_EXISTENCE, True),

               ('REAL_FEAST', 34, 'праздники из реального мира', tt_calendar.REAL_FEAST, True),
               ('CALENDAR_DATE', 35, 'важные даты календаря', tt_calendar.DATE, True),
               ('PHYSICS_DATE', 36, 'важные даты для физического мира', tt_calendar.PHYSICS_DATE, False),
               ('DAY_TIME', 37, 'время дня', tt_calendar.DAY_TIME, False),
               ('MONTH', 38, 'месяц', tt_calendar.MONTH, False),
               ('QUINT', 39, 'квинт', tt_calendar.QUINT, False),
               ('QUINT_DAY', 40, 'день квинта', tt_calendar.QUINT_DAY, False),
               ('DAY_TYPE', 41, 'тип дня', tt_calendar.DAY_TYPE, True),

               ('COINS_AMOUNT', 42, 'величина суммы монет', game_relations.COINS_AMOUNT, True),

               ('WEAPON_TYPE', 43, 'тип оружия', tt_artifacts_relations.WEAPON_TYPE, True),
               ('DAMAGE_TYPE', 44, 'тип нанесения урона', tt_artifacts_relations.DAMAGE_TYPE, True),
               ('MATERIAL', 45, 'основной материал', tt_artifacts_relations.MATERIAL, True),

               ('BEING_STRUCTURE', 46, 'структура', tt_beings_relations.STRUCTURE, True),
               ('BEING_FEATURE', 47, 'особенность существа', tt_beings_relations.FEATURE, True),
               ('BEING_MOVEMENT', 48, 'способ передвижения', tt_beings_relations.MOVEMENT, True),
               ('BEING_BODY', 49, 'телосложение', tt_beings_relations.BODY, True),
               ('BEING_SIZE', 50, 'размер', tt_beings_relations.SIZE, True),
               ('BEING_ORIENTATION', 51, 'положение тела', tt_beings_relations.ORIENTATION, True),

               ('UPBRINGING', 52, 'воспитание', tt_beings_relations.UPBRINGING, True),
               ('FIRST_DEATH', 53, 'первая смерть', tt_beings_relations.FIRST_DEATH, True),
               ('AGE', 54, 'возраст в котором умер', tt_beings_relations.AGE, False),

               ('CLAN_MEMBERSHIP', 55, 'членство в гильдии', heroes_relations.CLAN_MEMBERSHIP, True))


def get(value):
    restriction_groups = GROUP.index_static_relation[value._relation]
    restriction = storage.restrictions.get_restriction(restriction_groups[0], value.value)
    return restriction.id if restriction else None


def get_raw(name, value):
    restriction_group = getattr(GROUP, name)
    restriction = storage.restrictions.get_restriction(restriction_group, value)
    return restriction.id if restriction else None
