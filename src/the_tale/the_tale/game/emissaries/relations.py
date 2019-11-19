
import smart_imports

smart_imports.all()


class STATE(rels_django.DjangoEnum):
    records = (('IN_GAME', 1, 'Работает'),
               ('OUT_GAME', 2, 'Вне игры'))


class REMOVE_REASON(rels_django.DjangoEnum):
    records = (('NOT_REMOVED', 0, 'Не удалён'),
               ('KILLED', 1, 'Убит'),
               ('DISMISSED', 2, 'Уволен'))


noun = lexicon_dictionary.noun


class ABILITY(rels_django.DjangoEnum):
    event_name = rels.Column()
    profession = rels.Column()

    records = (('ECONOMY', 0, 'экономика',
                noun(['экономическое', 'экономического', 'экономическому', 'экономическое', 'экономическим', 'экономическом',
                      'экономические', 'экономических', 'экономическим', 'экономические', 'экономическими', 'экономических'], 'ср'),
                'экономист'),
               ('WARFARE', 1, 'военное дело',
                noun(['милитаристское', 'милитаристского', 'милитаристкому', 'милитаристское', 'милитаристким', 'милитаристском',
                      'милитаристские', 'милитаристских', 'милитаристким', 'милитаристские', 'милитаристкими', 'милитаристских'], 'ср'),
                'командующий'),
               ('TECHNOLOGIES', 2, 'технологии',
                noun(['технологическое', 'технологического', 'технологическому',
                      'технологическое', 'технологическим', 'технологическом',
                      'технологические', 'технологических', 'технологическим',
                      'технологические', 'технологическими', 'технологических'], 'ср'),
                'магоинженер'),
               ('SOCIOLOGY', 3, 'социология',
                noun(['общественное', 'общественного', 'общественному', 'общественное', 'общественным', 'общественном',
                      'общественные', 'общественных', 'общественным', 'общественные', 'общественными', 'общественных'], 'ср'),
                'социолог'),
               ('POLITICAL_SCIENCE', 4, 'политология',
                noun(['политическое', 'политического', 'политическому', 'политическое', 'политическим', 'политическом',
                      'политические', 'политических', 'политическим', 'политические', 'политическими', 'политических'], 'ср'),
                'политик'),
               ('COVERT_OPERATIONS', 5, 'тайные операции',
                noun(['тайное', 'тайного', 'тайному', 'тайное', 'тайным', 'тайном',
                      'тайные', 'тайных', 'тайным', 'тайные', 'тайными', 'тайных'], 'ср'),
                'шпион'),
               ('RELIGIOUS_STUDIES', 6, 'религиоведение',
                noun(['религиозное', 'религиозного', 'религиозному', 'религиозное', 'религиозным', 'религиозном',
                      'религиозные', 'религиозных', 'религиозным', 'религиозные', 'религиозными', 'религиозных'], 'ср'),
                'религиовед'),
               ('CULTURAL_SCIENCE', 7, 'культурология',
                noun(['культурное', 'культурного', 'культурному', 'культурное', 'культурным', 'культурном',
                      'культурные', 'культурных', 'культурным', 'культурные', 'культурными', 'культурных'], 'ср'),
                'культуролог'))


def attribute_modifiers(name_prefix, text_prefix, values):
    return [game_attributes.attr(name_prefix + ability.name,
                                 value,
                                 text_prefix.format(ability.text))
            for value, ability in zip(values, ABILITY.records)]


def event_modifiers(name_prefix, text, values, verbose_units='', formatter=lambda x: x):
    return [game_attributes.attr(name_prefix + attribute.name,
                                 value,
                                 text.format(attribute.event_name.word.forms[7]),
                                 verbose_units=verbose_units,
                                 formatter=formatter)
            for value, attribute in zip(values, ABILITY.records)]


class ATTRIBUTE(game_attributes.ATTRIBUTE):

    records = ([game_attributes.attr('MAX_HEALTH', 0, 'максимум здорвья')] +

               attribute_modifiers('ATTRIBUTE_GROW_SPEED__',
                                   'скорость роста способности «{}»',
                                   [1, 2, 3, 4, 5, 6, 7, 8, 9]) +

               attribute_modifiers('ATTRIBUTE_MAXIMUM__',
                                   'максимум способности «{}»',
                                   [10, 11, 12, 13, 14, 15, 16, 17, 18]) +

               [game_attributes.attr('DAMAGE_TO_HEALTH', 19, 'урон здоровью при покушении'),
                game_attributes.attr('POSITIVE_POWER', 20, 'положительное влияние от заданий',
                                     verbose_units='%', formatter=game_attributes.percents_formatter),
                game_attributes.attr('NEGATIVE_POWER', 21, 'негативное влияние от заданий',
                                     verbose_units='%', formatter=game_attributes.percents_formatter),
                game_attributes.attr('MAXIMUM_SIMULTANEOUSLY_EVENTS', 22, 'максимум одновременных мероприятий',),
                game_attributes.attr('EXPERIENCE_BONUS', 23, 'бонус к опыту от задания с участием эмиссара',
                                     verbose_units='%', formatter=game_attributes.percents_formatter)] +

               event_modifiers('EVENT_ACTION_POINTS_DELTA__',
                               'изменение цены в очках действия для {} мероприятий',
                               [24, 25, 26, 27, 28, 29, 30, 31, 32],
                               verbose_units='%', formatter=game_attributes.percents_formatter) +

               event_modifiers('EVENT_POWER_DELTA__',
                               'изменение цены влиянии для {} мероприятий',
                               [33, 34, 35, 36, 37, 38, 39, 40, 41],
                               verbose_units='%', formatter=game_attributes.percents_formatter) +

               [game_attributes.attr('CLAN_EXPERIENCE', 42, 'опыт гильдии от мероприятий',
                                     verbose_units='%', formatter=game_attributes.percents_formatter)])


ATTRIBUTE.EFFECTS_ORDER = sorted(set(record.order for record in ATTRIBUTE.records))


def trait(attribute, value, text, delta, positive):
    type = TRAIT_TYPE.POSITIVE if positive else TRAIT_TYPE.NEGATIVE

    if delta > 0:
        description = '{} увеличивается на {}'
    else:
        description = '{} уменьшается на {}'

    # if attribute.formatter is game_attributes.percents_formatter:
    if attribute.verbose_units:
        description += attribute.verbose_units

    return ('{}__{}'.format(attribute.name, type.name),
            value,
            text,
            attribute,
            delta,
            type,
            description.format(attribute.text, attribute.formatter(abs(delta))))


def ability_traits(name_template, values, text_template, delta, positive):
    if len(values) != len(ABILITY.records):
        raise NotImplementedError

    return [trait(getattr(ATTRIBUTE, name_template.format(ability.name)),
                  value,
                  text_template.format(ability.profession),
                  delta,
                  positive)
            for value, ability in zip(values, ABILITY.records)]


class TRAIT_TYPE(rels_django.DjangoEnum):
    records = (('POSITIVE', 0, 'положительная черта'),
               ('NEGATIVE', 1, 'отрицательная черта'))


class TRAIT(rels_django.DjangoEnum):
    attribute = rels.Column(unique=False)
    modification = rels.Column(unique=False, single_type=False)
    type = rels.Column(unique=False)
    description = rels.Column()

    records = ([trait(ATTRIBUTE.MAX_HEALTH, 0, 'крепкий здоровьем', tt_emissaries_constants.MAXIMUM_HEALTH_DELTA, True),
                trait(ATTRIBUTE.MAX_HEALTH, 1, 'болезненный', -tt_emissaries_constants.MAXIMUM_HEALTH_DELTA, False)] +

               ability_traits('ATTRIBUTE_GROW_SPEED__{}',
                              values=[2, 3, 4, 5, 6, 7, 8, 9],
                              text_template='способный {}',
                              delta=tt_emissaries_constants.ATTRIBUT_INCREMENT_BUFF,
                              positive=True) +

               ability_traits('ATTRIBUTE_GROW_SPEED__{}',
                              values=[10, 11, 12, 13, 14, 15, 16, 17],
                              text_template='слабый {}',
                              delta=-tt_emissaries_constants.ATTRIBUT_INCREMENT_BUFF,
                              positive=False) +

               ability_traits('ATTRIBUTE_MAXIMUM__{}',
                              values=[18, 19, 20, 21, 22, 23, 24, 25],
                              text_template='гениальный {}',
                              delta=tt_emissaries_constants.ATRIBUTE_MAXIMUM_DELTA,
                              positive=True) +

               ability_traits('ATTRIBUTE_MAXIMUM__{}',
                              values=[26, 27, 28, 29, 30, 31, 32, 33],
                              text_template='посредственный {}',
                              delta=-tt_emissaries_constants.ATRIBUTE_MAXIMUM_DELTA,
                              positive=False) +

               [trait(ATTRIBUTE.DAMAGE_TO_HEALTH, 34, 'толстокожий', -tt_emissaries_constants.DAMAGE_TO_HEALTH_DELTA, True),
                trait(ATTRIBUTE.DAMAGE_TO_HEALTH, 35, 'хрупкий', tt_emissaries_constants.DAMAGE_TO_HEALTH_DELTA, False),

                trait(ATTRIBUTE.POSITIVE_POWER, 36, 'рассполагающий', tt_emissaries_constants.QUEST_POWER_BONUS, True),
                trait(ATTRIBUTE.POSITIVE_POWER, 37, 'отвратный', -tt_emissaries_constants.QUEST_POWER_BONUS, False),

                trait(ATTRIBUTE.NEGATIVE_POWER, 38, 'осторожный', -tt_emissaries_constants.QUEST_POWER_BONUS, True),
                trait(ATTRIBUTE.NEGATIVE_POWER, 39, 'доверчивый', tt_emissaries_constants.QUEST_POWER_BONUS, False),

                trait(ATTRIBUTE.EXPERIENCE_BONUS, 40, 'хитроумный', tt_emissaries_constants.QUEST_EXPERIENCE_BUFF, True),
                trait(ATTRIBUTE.EXPERIENCE_BONUS, 41, 'простоватый', -tt_emissaries_constants.QUEST_EXPERIENCE_DEBUFF, False)] +

               ability_traits('EVENT_ACTION_POINTS_DELTA__{}',
                              values=[42, 43, 44, 45, 46, 47, 48, 49],
                              text_template='экономный {}',
                              delta=-tt_clans_constants.PRICE_START_EVENT_DELTA,
                              positive=True) +

               ability_traits('EVENT_ACTION_POINTS_DELTA__{}',
                              values=[50, 51, 52, 53, 54, 55, 56, 57],
                              text_template='расточительный {}',
                              delta=tt_clans_constants.PRICE_START_EVENT_DELTA,
                              positive=False) +

               ability_traits('EVENT_POWER_DELTA__{}',
                              values=[58, 59, 60, 61, 62, 63, 64, 65],
                              text_template='авторитетный {}',
                              delta=-tt_clans_constants.PRICE_START_EVENT_DELTA,
                              positive=True) +

               ability_traits('EVENT_POWER_DELTA__{}',
                              values=[66, 67, 68, 69, 70, 71, 72, 73],
                              text_template='непопулярный {}',
                              delta=tt_clans_constants.PRICE_START_EVENT_DELTA,
                              positive=False) +

               [trait(ATTRIBUTE.CLAN_EXPERIENCE, 74, 'дальновидный', tt_emissaries_constants.EVENT_EXPERIENCE_BUFF, True),
                trait(ATTRIBUTE.CLAN_EXPERIENCE, 75, 'ветренный', -tt_emissaries_constants.EVENT_EXPERIENCE_DEBUFF, False)])


class EVENT_STATE(rels_django.DjangoEnum):
    records = (('RUNNING', 1, 'работает'),
               ('STOPPED', 2, 'остановлено'))


class EVENT_STOP_REASON(rels_django.DjangoEnum):
    records = (('NOT_STOPPED', 0, 'не остановлено'),
               ('FINISHED', 1, 'завершено'),
               ('STOPPED_BY_PLAYER', 2, 'остановлено игроком'),
               ('EMISSARY_LEFT_GAME', 3, 'эмиссар покинул игру'))


class EVENT_AVAILABILITY(rels_django.DjangoEnum):
    description = rels.Column(unique=False)
    records = (('FOR_ALL', 0, 'для всех', 'Мероприятие действует всегда'),
               ('FOR_LEADERS', 1, 'для лидеров', 'Эффект мероприятия действует только если эмиссар является лидером по влиянияю в городе'))


def meta_object_receiver(id):

    @functools.wraps(meta_object_receiver)
    def receiver():
        from . import meta_relations
        return meta_relations.Event.create_from_id(id)

    return receiver


def event(name,
          value,
          text,
          availability,
          action_points_cost_modifier,
          power_cost_modifier,
          abilities,
          clan_permission='can_emissaries_planing'):
    return (name,
            value,
            text,
            availability,
            action_points_cost_modifier,
            power_cost_modifier,
            clan_permission,
            meta_object_receiver(value),
            abilities)


class EVENT_TYPE(rels_django.DjangoEnum):
    availability = rels.Column(unique=False)
    action_points_cost_modifier = rels.Column(unique=False)
    power_cost_modifier = rels.Column(unique=False)
    clan_permission = rels.Column(unique=False)
    meta_object = rels.Column()
    abilities = rels.Column(unique=False)

    records = (event('REST', 0, 'Отдых', EVENT_AVAILABILITY.FOR_ALL, 1.0, 1.0,
                     [ABILITY.TECHNOLOGIES, ABILITY.COVERT_OPERATIONS]),
               event('DISMISS', 1, 'Увольнение', EVENT_AVAILABILITY.FOR_ALL, 0.5, 0.0,
                     [ABILITY.POLITICAL_SCIENCE], clan_permission='can_emissaries_relocation'),
               event('RELOCATION', 2, 'Релокация', EVENT_AVAILABILITY.FOR_ALL, 2.0, 2.0,
                     [ABILITY.WARFARE, ABILITY.COVERT_OPERATIONS], clan_permission='can_emissaries_relocation'),
               event('RENAME', 3, 'Смена легенды', EVENT_AVAILABILITY.FOR_ALL, 1.0, 0.5,
                     [ABILITY.COVERT_OPERATIONS]),

               event('LEVEL_UP_POINTS_GANE', 4, 'Оптимизация делопроизводства', EVENT_AVAILABILITY.FOR_ALL, 1.0, 0.5,
                     [ABILITY.ECONOMY]),
               event('LEVEL_UP_MEMBERS_MAXIMUM', 5, 'Работа с кадрами', EVENT_AVAILABILITY.FOR_ALL, 1.0, 0.5,
                     [ABILITY.SOCIOLOGY]),
               event('LEVEL_UP_EMISSARIES_MAXIMUM', 6, 'Расширение влияния', EVENT_AVAILABILITY.FOR_ALL, 1.0, 0.5,
                     [ABILITY.POLITICAL_SCIENCE]),
               event('LEVEL_UP_FREE_QUESTS_MAXIMUM', 7, 'Привлечение добровольцев', EVENT_AVAILABILITY.FOR_ALL, 1.0, 0.5,
                     [ABILITY.SOCIOLOGY]),

               event('TRAINING', 8, 'Учения', EVENT_AVAILABILITY.FOR_ALL, 1.5, 1.5,
                     [ABILITY.WARFARE, ABILITY.POLITICAL_SCIENCE]),
               event('RESERVES_SEARCH', 9, 'Поиск резервов', EVENT_AVAILABILITY.FOR_ALL, 0.5, 1.5,
                     [ABILITY.ECONOMY, ABILITY.TECHNOLOGIES]),

               event('TASK_BOARD_UPDATING', 10, 'Обновление доски заданий', EVENT_AVAILABILITY.FOR_ALL, 0.5, 0.5,
                     [ABILITY.SOCIOLOGY, ABILITY.POLITICAL_SCIENCE]),
               event('FAST_TRANSPORTATION', 11, 'Организация сопровождения', EVENT_AVAILABILITY.FOR_ALL, 1.0, 2.0,
                     [ABILITY.WARFARE, ABILITY.COVERT_OPERATIONS]),
               event('COMPANIONS_SUPPORT', 12, 'Поддержка спутников', EVENT_AVAILABILITY.FOR_ALL, 1.5, 1.0,
                     [ABILITY.TECHNOLOGIES, ABILITY.SOCIOLOGY, ABILITY.RELIGIOUS_STUDIES]),

               event('ARTISANS_SUPPORT', 13, 'Поддержка ремесленников', EVENT_AVAILABILITY.FOR_LEADERS, 1.5, 1.5,
                     [ABILITY.ECONOMY, ABILITY.TECHNOLOGIES]),
               event('PUBLIC_OPINION_MANAGEMENT', 14, 'Управление общественным мнением', EVENT_AVAILABILITY.FOR_LEADERS, 2.0, 2.0,
                     [ABILITY.SOCIOLOGY, ABILITY.POLITICAL_SCIENCE]),
               event('PATRONAGE', 15, 'Меценатство', EVENT_AVAILABILITY.FOR_LEADERS, 1.0, 1.0,
                     [ABILITY.ECONOMY, ABILITY.CULTURAL_SCIENCE]),

               event('PATRIOTIC_PATRONAGE', 16, 'Патриотическая протекция', EVENT_AVAILABILITY.FOR_LEADERS, 1.0, 1.0,
                     [ABILITY.ECONOMY, ABILITY.SOCIOLOGY, ABILITY.CULTURAL_SCIENCE]),

               event('GLORY_OF_THE_KEEPERS', 17, 'Слава Хранителей', EVENT_AVAILABILITY.FOR_LEADERS, 2.0, 2.0,
                     [ABILITY.RELIGIOUS_STUDIES, ABILITY.CULTURAL_SCIENCE]),)


class EVENT_CURRENCY(rels_django.DjangoEnum):
    records = (('TASK_BOARD', 0, 'доска заданий города'),
               ('FAST_TRANSPORTATION', 1, 'быстрая транспортировка'),
               ('COMPANIONS_SUPPORT', 2, 'поддержка спутников'),
               ('GLORY_OF_THE_KEEPERS', 3, 'Слава Хранителей'))
