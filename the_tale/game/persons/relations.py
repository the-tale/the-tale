# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from questgen import relations as questgen_relations
from questgen.quests.base_quest import RESULTS as QUEST_RESULTS

from the_tale.game.balance import constants as c

from the_tale.game import attributes
from the_tale.game import effects

from the_tale.game.jobs import effects as jobs_effects

from the_tale.game.places import relations as places_relations
from the_tale.game.heroes import relations as heroes_relations


class PERSON_TYPE(DjangoEnum):
    building_type = Column(related_name='person_type')
    quest_profession = Column(unique=False)

    records = ( ('BLACKSMITH',   0, u'кузнец', places_relations.BUILDING_TYPE.SMITHY, questgen_relations.PROFESSION.BLACKSMITH),
                ('FISHERMAN',    1, u'рыбак', places_relations.BUILDING_TYPE.FISHING_LODGE, questgen_relations.PROFESSION.NONE),
                ('TAILOR',       2, u'портной', places_relations.BUILDING_TYPE.TAILOR_SHOP, questgen_relations.PROFESSION.NONE),
                ('CARPENTER',    3, u'плотник', places_relations.BUILDING_TYPE.SAWMILL, questgen_relations.PROFESSION.NONE),
                ('HUNTER',       4, u'охотник', places_relations.BUILDING_TYPE.HUNTER_HOUSE, questgen_relations.PROFESSION.NONE),
                ('WARDEN',       5, u'стражник', places_relations.BUILDING_TYPE.WATCHTOWER, questgen_relations.PROFESSION.NONE),
                ('MERCHANT',     6, u'торговец', places_relations.BUILDING_TYPE.TRADING_POST, questgen_relations.PROFESSION.NONE),
                ('INNKEEPER',    7, u'трактирщик', places_relations.BUILDING_TYPE.INN, questgen_relations.PROFESSION.NONE),
                ('ROGUE',        8, u'вор', places_relations.BUILDING_TYPE.DEN_OF_THIEVE, questgen_relations.PROFESSION.ROGUE),
                ('FARMER',       9, u'фермер', places_relations.BUILDING_TYPE.FARM, questgen_relations.PROFESSION.NONE),
                ('MINER',        10, u'шахтёр', places_relations.BUILDING_TYPE.MINE, questgen_relations.PROFESSION.NONE),
                ('PRIEST',       11, u'священник', places_relations.BUILDING_TYPE.TEMPLE, questgen_relations.PROFESSION.NONE),
                ('PHYSICIAN',    12, u'лекарь', places_relations.BUILDING_TYPE.HOSPITAL, questgen_relations.PROFESSION.NONE),
                ('ALCHEMIST',    13, u'алхимик', places_relations.BUILDING_TYPE.LABORATORY, questgen_relations.PROFESSION.NONE),
                ('EXECUTIONER',  14, u'палач', places_relations.BUILDING_TYPE.SCAFFOLD, questgen_relations.PROFESSION.NONE),
                ('MAGICIAN',     15, u'волшебник', places_relations.BUILDING_TYPE.MAGE_TOWER, questgen_relations.PROFESSION.NONE),
                ('USURER',       16, u'ростовщик', places_relations.BUILDING_TYPE.GUILDHALL, questgen_relations.PROFESSION.NONE),
                ('CLERK',        17, u'писарь', places_relations.BUILDING_TYPE.BUREAU, questgen_relations.PROFESSION.NONE),
                ('MAGOMECHANIC', 18, u'магомеханик', places_relations.BUILDING_TYPE.MANOR, questgen_relations.PROFESSION.NONE),
                ('BARD',         19, u'бард', places_relations.BUILDING_TYPE.SCENE, questgen_relations.PROFESSION.NONE),
                ('TAMER',        20, u'дрессировщик', places_relations.BUILDING_TYPE.MEWS, questgen_relations.PROFESSION.NONE),
                ('HERDSMAN',     21, u'скотовод', places_relations.BUILDING_TYPE.RANCH, questgen_relations.PROFESSION.NONE) )


class SOCIAL_CONNECTION_TYPE(DjangoEnum):
    questgen_type = Column()
    records = ( ('PARTNER', 0, u'партнёр', questgen_relations.SOCIAL_RELATIONS.PARTNER),
                ('CONCURRENT', 1, u'конкурент', questgen_relations.SOCIAL_RELATIONS.CONCURRENT), )

class SOCIAL_CONNECTION_STATE(DjangoEnum):
    records = ( ('IN_GAME', 0, u'в игре'),
                ('OUT_GAME', 1, u'вне игры'), )


class ATTRIBUTE(attributes.ATTRIBUTE):

    records = ( attributes.attr('ON_QUEST_HABITS', 0, u'изменения черт, если Мастер получает выгоду от задания', default=dict, apply=lambda a, b: (a.update(b) or a)),
                attributes.attr('TERRAIN_POWER', 1, u'сила влияния на ланшафт', default=lambda: 1),
                attributes.attr('TERRAIN_RADIUS_BONUS', 2, u'бонус к радиусу влияния города на ландшафт'),
                attributes.attr('PLACES_HELP_AMOUNT', 3, u'бонус к начисляемым «влияниям» за задания', default=lambda: 1),
                attributes.attr('POLITIC_POWER_BONUS', 4, u'бонус к влиянию за задания с участием Мастера'),
                attributes.attr('EXPERIENCE_BONUS', 5, u'бонус к опыту за задания с участием Мастера'),
                attributes.attr('ON_PROFITE_REWARD_BONUS', 6, u'бонус к наградами за задания, если Мастер получает выгоду'),
                attributes.attr('FRIENDS_QUESTS_PRIORITY_BONUS', 7, u'бонус к вероятности соратникам получить задание, связанное с Мастером'),
                attributes.attr('ENEMIES_QUESTS_PRIORITY_BONUS', 8, u'бонус к вероятности противников получить задание, связанное с Мастером'),
                attributes.attr('POLITIC_RADIUS_BONUS', 9, u'бонус к радиусу влияния города'),
                attributes.attr('STABILITY_RENEWING_BONUS', 10, u'бонус к скорости восстановления стабильности в городе'),
                attributes.attr('BUILDING_AMORTIZATION_SPEED', 11, u'скорость амортизации здания Мастера', default=lambda: 1),
                attributes.attr('ON_PROFITE_ENERGY', 12, u'прибавка энергии Хранителя за задание, если Мастер получает выгоду'),
                attributes.attr('JOB_POWER_BONUS', 13, u'бонус к эффекту занятий Мастера'),
                attributes.attr('JOB_GROUP_PRIORITY', 14, u'бонус к приоритету типов занятий Мастера', default=dict, apply=lambda a, b: (a.update(b) or a)),
                attributes.attr('SOCIAL_RELATIONS_PARTNERS_POWER', 15, u'сила социальных связей с партнёрами'),
                attributes.attr('SOCIAL_RELATIONS_CONCURRENTS_POWER', 16, u'сила социальных связей с конкурентами'),
                attributes.attr('DEMOGRAPHICS_PRESSURE', 17, u'демографическое давление', default=lambda: 1) )

    EFFECTS_ORDER = sorted(set(record[-4] for record in records))


class PERSONALITY(DjangoEnum):
    effect = Column()
    description = Column()


def personality(name, value, text, attribute, attribute_value, description):
    return (name, value, text, effects.Effect(name=text, attribute=getattr(ATTRIBUTE, attribute), value=attribute_value), description)




class PERSONALITY_COSMETIC(PERSONALITY):
    records = ( personality('TRUTH_SEEKER', 0, u'правдолюб', 'ON_QUEST_HABITS', {QUEST_RESULTS.SUCCESSED: heroes_relations.HABIT_CHANGE_SOURCE.MASTER_QUEST_HONORABLE,
                                                                                 QUEST_RESULTS.FAILED: heroes_relations.HABIT_CHANGE_SOURCE.MASTER_QUEST_DISHONORABLE},
                 u'Увеличивает честь героя, если Мастер получает выгоду от задания и уменьшает, если вред.'),

                personality('KNAVE', 1, u'плут', 'ON_QUEST_HABITS', {QUEST_RESULTS.SUCCESSED: heroes_relations.HABIT_CHANGE_SOURCE.MASTER_QUEST_DISHONORABLE,
                                                                     QUEST_RESULTS.FAILED: heroes_relations.HABIT_CHANGE_SOURCE.MASTER_QUEST_HONORABLE},
                 u'Уменьшает честь героя, если Мастер получает выгоду от задания и увеличивает, если вред.'),

                personality('GOOD_SOUL', 2, u'добряк', 'ON_QUEST_HABITS', {QUEST_RESULTS.SUCCESSED: heroes_relations.HABIT_CHANGE_SOURCE.MASTER_QUEST_UNAGGRESSIVE,
                                                                           QUEST_RESULTS.FAILED: heroes_relations.HABIT_CHANGE_SOURCE.MASTER_QUEST_AGGRESSIVE},
                 u'Увеличивает миролюбие героя, если Мастер получает выгоду от задания и уменьшает, если вред.'),

                personality('BULLY', 3, u'забияка', 'ON_QUEST_HABITS', {QUEST_RESULTS.SUCCESSED: heroes_relations.HABIT_CHANGE_SOURCE.MASTER_QUEST_AGGRESSIVE,
                                                                        QUEST_RESULTS.FAILED: heroes_relations.HABIT_CHANGE_SOURCE.MASTER_QUEST_UNAGGRESSIVE},
                 u'Уменьшает миролюбие героя, если Мастер получает выгоду от задания и увеличивает, если вред.'),

                personality('LEADER', 4, u'лидер', 'TERRAIN_POWER', 0.15,
                 u'Оказывает большее влияние на ландшафт вокруг города.'),

                personality('FIDGET', 5, u'непоседа', 'TERRAIN_RADIUS_BONUS', 1,
                 u'Увеличивает радиус изменений ландшафта городом.'),

                personality('GUARANTOR', 6, u'поручитель', 'PLACES_HELP_AMOUNT', 1,
                 u'За выполнение задания, связанного с мастером, герой получает больше очков помощи в каждом городе, связанном с заданием.'),

                personality('NIHILIST', 7, u'нигилист', 'PLACES_HELP_AMOUNT', -0.5,
                 u'За выполнение задания, связанного с мастером, герой получает меньше очков помощи в каждом городе, связанном с заданием.'),

                personality('RECLUSE', 8, u'затворник', 'PLACES_HELP_AMOUNT', 0,
                 u'Мастер не оказывает никакого специфического влияния.'),

                personality('ORGANIZER', 9, u'организатор', 'DEMOGRAPHICS_PRESSURE', 1,
                 u'Увеличивает демографическое давление своей расы в городе.') )


class PERSONALITY_PRACTICAL(PERSONALITY):
    records = ( personality('MULTIWISE', 1, u'многомудрый', 'EXPERIENCE_BONUS', 0.25,
                 u'Выполняя задания, связанные с Мастером, герои получают больше опыта.'),

                personality('INFLUENTIAL', 2, u'влиятельный', 'POLITIC_POWER_BONUS', 0.25,
                 u'Выполняя задания, связанные с Мастером, герои приносят больше влияния.'),

                personality('GENEROUS', 3, u'щедрый', 'ON_PROFITE_REWARD_BONUS', 2.0,
                 u'Герои получают больше денег за задания, если Мастер получает от него выгоду.'),

                personality('CHARISMATIC', 4, u'харизматичный', 'FRIENDS_QUESTS_PRIORITY_BONUS', c.HABIT_QUEST_PRIORITY_MODIFIER,
                 u'Герои чаще берут задания, связанные с Мастером, если это их соратник.'),

                personality('REVENGEFUL', 5, u'мстительный', 'ENEMIES_QUESTS_PRIORITY_BONUS', -c.HABIT_QUEST_PRIORITY_MODIFIER / 2.0,
                 u'Герои реже берут задания, связанные с Мастером, если это их противник.'),

                personality('ACTIVE', 6, u'деятельный', 'POLITIC_RADIUS_BONUS', 1,
                 u'Увеличивает радиус влияния города.'),

                personality('RELIABLE', 7, u'надёжный', 'STABILITY_RENEWING_BONUS', 0.25,
                 u'Увеличивает скорость восстановления стабильности.'),

                personality('ORDERLY', 8, u'аккуратный', 'BUILDING_AMORTIZATION_SPEED', -0.5,
                 u'Замедляет амортизацию своего здания.'),

                personality('DEVOUT', 9, u'набожный', 'ON_PROFITE_ENERGY', 4,
                 u'За каждое задание, в котором Мастер получил выгоду, возносит хвалу Хранителям героев, и те получают немного энергии.'),

                personality('HARDWORKING', 10, u'трудолюбивый', 'JOB_POWER_BONUS', 1.0,
                 u'У занятий Мастера более сильный эффект.'),

                personality('ENTERPRISING', 11, u'предприимчивый', 'JOB_GROUP_PRIORITY', {jobs_effects.EFFECT_GROUP.ON_PLACE: 0.5},
                 u'Мастер чаще выполняет занятия, связанные с экономикой города.'),

                personality('ROMANTIC', 12, u'романтичный', 'JOB_GROUP_PRIORITY', {jobs_effects.EFFECT_GROUP.ON_HEROES: 0.5},
                 u'Мастер чаще выполняет занятия, связанные с помощью героям.'),

                personality('RESPONSIBLE', 13, u'ответственный', 'SOCIAL_RELATIONS_PARTNERS_POWER', 0.0,
                 u'Социальные связи с партнёрами действуют сильнее.'),

                personality('INSIDIOUS', 14, u'коварный', 'SOCIAL_RELATIONS_CONCURRENTS_POWER', 0.0,
                 u'Социальные связи с конкурентами действуют сильнее.') )
