# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from questgen import relations as questgen_relations
from questgen.quests.base_quest import RESULTS as QUEST_RESULTS

from the_tale.game import attributes
from the_tale.game import effects

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
                attributes.attr('PLACES_HELP_BONUS', 3, u'бонус к начисляемым «влияниям» за задания'),
                attributes.attr('START_QUESTS_PRIORITY', 4, u'приоритет типов заданий, инициируемых Мастером', default=dict, apply=lambda a, b: (a.update(b) or a)),
                attributes.attr('POLITIC_POWER_BONUS', 5, u'бонус к влиянию за задания с участием Мастера'),
                attributes.attr('EXPERIENCE_BONUS', 6, u'бонус к опыту за задания с участием Мастера'),
                attributes.attr('ON_PROFITE_MONEY_REWARD_BONUS', 7, u'бонус к денежным наградами за задания, если Мастер получает выгоду'),
                attributes.attr('ON_PROFITE_ARTIFACT_RARITY_BONUS', 8, u'бонус к вероятности получить более редкий артефакт, если Мастер получает выгоду'),
                attributes.attr('ON_PROFITE_ARTIFACT_POWER_BONUS', 9, u'бонус к силе получаемых за задания артефактов, если Мастер получает выгоду'),
                attributes.attr('FRIENDS_QUESTS_PRIORITY_BONUS', 10, u'бонус к вероятности соратникам получить задание, связанное с Мастером'),
                attributes.attr('ENEMIES_QUESTS_PRIORITY_BONUS', 11, u'бонус к вероятности противников получить задание, связанное с Мастером'),
                attributes.attr('POLITIC_RADIUS_BONUS', 12, u'бонус к радиусу влияния города'),
                attributes.attr('STABILITY_RENEWING_BONUS', 13, u'бонус к скорости восстановления стабильности в городе'),
                attributes.attr('BUILDING_AMORTIZATION_SPEED', 14, u'скорость амортизации здания Мастера'),
                attributes.attr('ON_PROFITE_ENERGY', 15, u'прибавка энергии Хранителя за задание, если Мастер получает выгоду'),
                attributes.attr('JOB_POWER_BONUS', 16, u'бонус к эффекту занятий Мастера'),
                attributes.attr('JOB_EFFECT_PRIORITY', 17, u'бонус к приоритету типов занятий Мастера'),
                attributes.attr('SOCIAL_RELATIONS_PARTNERS_POWER', 18, u'сила социальных связей с партнёрами'),
                attributes.attr('SOCIAL_RELATIONS_CONCURRENTS_POWER', 19, u'сила социальных связей с конкурентами'),
                attributes.attr('DEMOGRAPHICS_PRESSURE', 20, u'демографическое давление', default=lambda: 1) )

    EFFECTS_ORDER = sorted(set(record[-3] for record in records))


class PERSONALITY(DjangoEnum):
    effect = Column()
    description = Column()


def personality(name, value, text, attribute, attribute_value, description):
    return (name, value, text, effects.Effect(name=text, attribute=getattr(ATTRIBUTE, attribute), value=attribute_value), description)




class PERSONALITY_COSMETIC(PERSONALITY):
    records = ( personality('P_1', 0, u'1', 'ON_QUEST_HABITS', {QUEST_RESULTS.SUCCESSED: heroes_relations.HABIT_CHANGE_SOURCE.MASTER_QUEST_HONORABLE,
                                                                QUEST_RESULTS.FAILED: heroes_relations.HABIT_CHANGE_SOURCE.MASTER_QUEST_DISHONORABLE},
                 u'Увеличивает честь героя, если Мастер получает выгоду от задания и уменьшает, если вред'),

                personality('P_2', 1, u'2', 'ON_QUEST_HABITS', {QUEST_RESULTS.SUCCESSED: heroes_relations.HABIT_CHANGE_SOURCE.MASTER_QUEST_DISHONORABLE,
                                                                QUEST_RESULTS.FAILED: heroes_relations.HABIT_CHANGE_SOURCE.MASTER_QUEST_HONORABLE},
                 u'Уменьшает честь героя, если Мастер получает выгоду от задания и увеличивает, если вред'),

                personality('P_3', 2, u'3', 'ON_QUEST_HABITS', {QUEST_RESULTS.SUCCESSED: heroes_relations.HABIT_CHANGE_SOURCE.MASTER_QUEST_UNAGGRESSIVE,
                                                                QUEST_RESULTS.FAILED: heroes_relations.HABIT_CHANGE_SOURCE.MASTER_QUEST_AGGRESSIVE},
                 u'Увеличивает миролюбие героя, если Мастер получает выгоду от задания и уменьшает, если вред'),

                personality('P_4', 3, u'4', 'ON_QUEST_HABITS', {QUEST_RESULTS.SUCCESSED: heroes_relations.HABIT_CHANGE_SOURCE.MASTER_QUEST_AGGRESSIVE,
                                                                QUEST_RESULTS.FAILED: heroes_relations.HABIT_CHANGE_SOURCE.MASTER_QUEST_UNAGGRESSIVE},
                 u'Уменьшает миролюбие героя, если Мастер получает выгоду от задания и увеличивает, если вред'),

                personality('P_5', 4, u'5', 'TERRAIN_POWER', 0.15,
                 u'Оказывает большее влияние на ландшафт вокруг города'),

                personality('P_6', 5, u'6', 'TERRAIN_RADIUS_BONUS', 1,
                 u'увеличивает радиус изменений ландшафта городом'),

                personality('P_7', 6, u'7', 'PLACES_HELP_BONUS', 0.0,
                 u'за выполнение задания, связанного с мастером, герой получает дополнительную помощь помощи в каждом связанном с заданием городе'),

                personality('P_8', 7, u'8', 'PLACES_HELP_BONUS', 0.0,
                 u'за выполнение задания, связанного с мастером, герой получает меньше помощи в каждом связанном с заданием городе'),

                personality('P_9', 8, u'9', 'START_QUESTS_PRIORITY', {},
                 u'чаще даёт задание на шпионаж'),

                personality('P_10', 10, u'10', 'START_QUESTS_PRIORITY', {},
                 u'чаще даёт задание на доставку'),

                personality('P_11', 11, u'11', 'START_QUESTS_PRIORITY', {},
                 u'чаще даёт задание на караван'),

                personality('P_12', 12, u'12', 'START_QUESTS_PRIORITY', {},
                 u'чаще даёт задание на выбивание долга'),

                personality('P_13', 13, u'13', 'START_QUESTS_PRIORITY', {},
                 u'чаще даёт задание на помощь'),

                personality('P_14', 14, u'14', 'START_QUESTS_PRIORITY', {},
                 u'не даёт косметических бонусов personality(типо заурядность)'),

                personality('P_15', 15, u'15', 'DEMOGRAPHICS_PRESSURE', 1,
                 u'Увеличивает демографическое давление своей расы в городе') )


class PERSONALITY_PRACTICAL(PERSONALITY):
    records = ( personality('P_1', 1, u'1', 'EXPERIENCE_BONUS', 0.25,
                 u'увеличивает опыт в связанных с собой заданиях'),

                personality('P_2', 2, u'2', 'POLITIC_POWER_BONUS', 0.25,
                 u'увеличивает влияние в связанных с собой заданиях'),

                personality('P_3', 3, u'3', 'ON_PROFITE_MONEY_REWARD_BONUS', 0.0,
                 u'увеличивает денежную награду за задания, если получит выгоду от задания'),

                personality('P_5', 4, u'5', 'ON_PROFITE_ARTIFACT_RARITY_BONUS', 0.0,
                 u'больше шанс получить качественный артефакт за задания, если получит выгоду от задания'),

                personality('P_6', 5, u'6', 'ON_PROFITE_ARTIFACT_POWER_BONUS', 0.0,
                 u'даёт более сильные артефакты за задания, если получит выгоду от задания'),

                personality('P_7', 6, u'7', 'FRIENDS_QUESTS_PRIORITY_BONUS', 0.0,
                 u'герои чаще берут задания, связанные с Мастером, если это их соратник'),

                personality('P_8', 7, u'8', 'ENEMIES_QUESTS_PRIORITY_BONUS', 0.0,
                 u'герои реже берут задания, связанные с Мастером, если это их противник'),

                personality('P_9', 8, u'9', 'POLITIC_RADIUS_BONUS', 1,
                 u'увеличивает радиус влияния города'),

                personality('P_10', 9, u'10', 'STABILITY_RENEWING_BONUS', 0.25,
                 u'увеличивает скорость восстановления стабильности'),

                personality('P_11', 10, u'11', 'BUILDING_AMORTIZATION_SPEED', 0.0,
                 u'замедляет амортизацию своего здания'),

                personality('P_12', 11, u'12', 'ON_PROFITE_ENERGY', 0.0,
                 u'за каждое задание, в котором Мастер получил выгоду, дают игроку немного энергии'),

                personality('P_13', 12, u'13', 'JOB_POWER_BONUS', 0.0,
                 u'у занятий Мастера более сильный эффек'),

                personality('P_14', 13, u'14', 'JOB_EFFECT_PRIORITY', 0.0,
                 u'Мастер чаще выполняет занятия, связанные с экономикой города'),

                personality('P_15', 14, u'15', 'JOB_EFFECT_PRIORITY', 0.0,
                 u'Мастер чаще выполняет занятия, связанные с помощью героям'),

                personality('P_16', 15, u'16', 'SOCIAL_RELATIONS_PARTNERS_POWER', 0.0,
                 u'социальные связи с партнёрами действуют сильнее'),

                personality('P_17', 16, u'17', 'SOCIAL_RELATIONS_CONCURRENTS_POWER', 0.0,
                 u'социальные связи с конкурентами действуют сильнее') )
