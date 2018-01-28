
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
    male_text = Column()
    female_text = Column()
    building_type = Column(related_name='person_type')
    quest_profession = Column(unique=False)

    records = ( ('BLACKSMITH',   0, 'кузнец', 'кузнец', 'кузнец', places_relations.BUILDING_TYPE.SMITHY, questgen_relations.PROFESSION.BLACKSMITH),
                ('FISHERMAN',    1, 'рыбак', 'рыбак', 'рыбачка', places_relations.BUILDING_TYPE.FISHING_LODGE, questgen_relations.PROFESSION.NONE),
                ('TAILOR',       2, 'портной', 'портной', 'портная', places_relations.BUILDING_TYPE.TAILOR_SHOP, questgen_relations.PROFESSION.NONE),
                ('CARPENTER',    3, 'плотник', 'плотник', 'плотник', places_relations.BUILDING_TYPE.SAWMILL, questgen_relations.PROFESSION.NONE),
                ('HUNTER',       4, 'охотник', 'охотник', 'охотница', places_relations.BUILDING_TYPE.HUNTER_HOUSE, questgen_relations.PROFESSION.NONE),
                ('WARDEN',       5, 'стражник', 'стражник', 'стражница', places_relations.BUILDING_TYPE.WATCHTOWER, questgen_relations.PROFESSION.NONE),
                ('MERCHANT',     6, 'торговец', 'торговец', 'торговка', places_relations.BUILDING_TYPE.TRADING_POST, questgen_relations.PROFESSION.NONE),
                ('INNKEEPER',    7, 'трактирщик', 'трактирщик', 'трактирщица', places_relations.BUILDING_TYPE.INN, questgen_relations.PROFESSION.NONE),
                ('ROGUE',        8, 'вор', 'вор', 'воровка', places_relations.BUILDING_TYPE.DEN_OF_THIEVE, questgen_relations.PROFESSION.ROGUE),
                ('FARMER',       9, 'фермер', 'фермер', 'фермерша', places_relations.BUILDING_TYPE.FARM, questgen_relations.PROFESSION.NONE),
                ('MINER',        10, 'шахтёр', 'шахтёр', 'шахтёрка', places_relations.BUILDING_TYPE.MINE, questgen_relations.PROFESSION.NONE),
                ('PRIEST',       11, 'священник', 'священник', 'священница', places_relations.BUILDING_TYPE.TEMPLE, questgen_relations.PROFESSION.NONE),
                ('PHYSICIAN',    12, 'лекарь', 'лекарь', 'лекарь', places_relations.BUILDING_TYPE.HOSPITAL, questgen_relations.PROFESSION.NONE),
                ('ALCHEMIST',    13, 'алхимик', 'алхимик', 'алхимик', places_relations.BUILDING_TYPE.LABORATORY, questgen_relations.PROFESSION.NONE),
                ('EXECUTIONER',  14, 'палач', 'палач', 'палач', places_relations.BUILDING_TYPE.SCAFFOLD, questgen_relations.PROFESSION.NONE),
                ('MAGICIAN',     15, 'волшебник', 'волшебник', 'волшебница', places_relations.BUILDING_TYPE.MAGE_TOWER, questgen_relations.PROFESSION.NONE),
                ('USURER',       16, 'ростовщик', 'ростовщик', 'ростовщица', places_relations.BUILDING_TYPE.GUILDHALL, questgen_relations.PROFESSION.NONE),
                ('CLERK',        17, 'писарь', 'писарь', 'писарь', places_relations.BUILDING_TYPE.BUREAU, questgen_relations.PROFESSION.NONE),
                ('MAGOMECHANIC', 18, 'магомеханик', 'магомеханик', 'магомеханик', places_relations.BUILDING_TYPE.MANOR, questgen_relations.PROFESSION.NONE),
                ('BARD',         19, 'бард', 'бард', 'бардесса', places_relations.BUILDING_TYPE.SCENE, questgen_relations.PROFESSION.NONE),
                ('TAMER',        20, 'дрессировщик', 'дрессировщик', 'дрессировщица', places_relations.BUILDING_TYPE.MEWS, questgen_relations.PROFESSION.NONE),
                ('HERDSMAN',     21, 'скотовод', 'скотовод', 'скотовод', places_relations.BUILDING_TYPE.RANCH, questgen_relations.PROFESSION.NONE) )


class SOCIAL_CONNECTION_TYPE(DjangoEnum):
    questgen_type = Column()
    records = ( ('PARTNER', 0, 'партнёр', questgen_relations.SOCIAL_RELATIONS.PARTNER),
                ('CONCURRENT', 1, 'конкурент', questgen_relations.SOCIAL_RELATIONS.CONCURRENT), )

def quest_result_serialize(data):
    return {k: v.value for k,v in data.items()}

def quest_result_deserialize(data):
    return {k: heroes_relations.HABIT_CHANGE_SOURCE(v) for k,v in data.items()}


def job_group_priority_serialize(data):
    return {k.value: v for k,v in data.items()}

def job_group_priority_deserialize(data):
    return {jobs_effects.EFFECT_GROUP(int(k)): v for k, v in data.items()}


class ATTRIBUTE(attributes.ATTRIBUTE):

    records = ( attributes.attr('ON_QUEST_HABITS', 0, 'изменения черт, если Мастер получает выгоду от задания', default=dict, apply=lambda a, b: (a.update(b) or a), serializer=quest_result_serialize, deserializer=quest_result_deserialize),
                attributes.attr('TERRAIN_POWER', 1, 'сила влияния на ланшафт', default=lambda: 0.1),
                attributes.attr('TERRAIN_RADIUS_BONUS', 2, 'бонус к радиусу влияния города на ландшафт'),
                attributes.attr('PLACES_HELP_AMOUNT', 3, 'бонус к начисляемым «влияниям» за задания', default=lambda: 1),
                attributes.attr('POLITIC_POWER_BONUS', 4, 'бонус к влиянию за задания с участием Мастера'),
                attributes.attr('EXPERIENCE_BONUS', 5, 'бонус к опыту за задания с участием Мастера'),
                attributes.attr('ON_PROFITE_REWARD_BONUS', 6, 'бонус к наградами за задания, если Мастер получает выгоду'),
                attributes.attr('FRIENDS_QUESTS_PRIORITY_BONUS', 7, 'бонус к вероятности соратникам получить задание, связанное с Мастером'),
                attributes.attr('ENEMIES_QUESTS_PRIORITY_BONUS', 8, 'бонус к вероятности противников получить задание, связанное с Мастером'),
                attributes.attr('POLITIC_RADIUS_BONUS', 9, 'бонус к радиусу влияния города'),
                attributes.attr('STABILITY_RENEWING_BONUS', 10, 'бонус к скорости восстановления стабильности в городе'),
                attributes.attr('BUILDING_AMORTIZATION_SPEED', 11, 'скорость амортизации здания Мастера', default=lambda: 1),
                attributes.attr('ON_PROFITE_ENERGY', 12, 'прибавка энергии Хранителя за задание, если Мастер получает выгоду'),
                attributes.attr('JOB_POWER_BONUS', 13, 'бонус к эффекту занятий Мастера'),
                attributes.attr('JOB_GROUP_PRIORITY', 14, 'бонус к приоритету типов занятий Мастера', default=dict, apply=lambda a, b: (a.update(b) or a), serializer=job_group_priority_serialize, deserializer=job_group_priority_deserialize),
                attributes.attr('SOCIAL_RELATIONS_PARTNERS_POWER_MODIFIER', 15, 'бонус к влияния для партнёров', default=lambda: 0.1),
                attributes.attr('SOCIAL_RELATIONS_CONCURRENTS_POWER_MODIFIER', 16, 'бонус к влияюнию для конкурентов', default=lambda: 0.1),
                attributes.attr('DEMOGRAPHICS_PRESSURE', 17, 'демографическое давление', default=lambda: 1) )

    EFFECTS_ORDER = sorted(set(record[5] for record in records))


class PERSONALITY(DjangoEnum):
    effect = Column()
    male_text = Column()
    female_text = Column()
    description = Column()


def personality(name, value, text, attribute, attribute_value, male_text, female_text, description):
    return (name, value, text, effects.Effect(name=text, attribute=getattr(ATTRIBUTE, attribute), value=attribute_value), male_text, female_text, description)


class PERSONALITY_COSMETIC(PERSONALITY):
    records = ( personality('TRUTH_SEEKER', 0, 'правдолюб', 'ON_QUEST_HABITS', {QUEST_RESULTS.SUCCESSED: heroes_relations.HABIT_CHANGE_SOURCE.MASTER_QUEST_HONORABLE,
                                                                                 QUEST_RESULTS.FAILED: heroes_relations.HABIT_CHANGE_SOURCE.MASTER_QUEST_DISHONORABLE},
                'правдолюб', 'правдолюбка', 'Увеличивает честь героя, если Мастер получает выгоду от задания и уменьшает, если вред.'),

                personality('KNAVE', 1, 'плут', 'ON_QUEST_HABITS', {QUEST_RESULTS.SUCCESSED: heroes_relations.HABIT_CHANGE_SOURCE.MASTER_QUEST_DISHONORABLE,
                                                                     QUEST_RESULTS.FAILED: heroes_relations.HABIT_CHANGE_SOURCE.MASTER_QUEST_HONORABLE},
                'плут', 'плутовка', 'Уменьшает честь героя, если Мастер получает выгоду от задания и увеличивает, если вред.'),

                personality('GOOD_SOUL', 2, 'добряк', 'ON_QUEST_HABITS', {QUEST_RESULTS.SUCCESSED: heroes_relations.HABIT_CHANGE_SOURCE.MASTER_QUEST_UNAGGRESSIVE,
                                                                           QUEST_RESULTS.FAILED: heroes_relations.HABIT_CHANGE_SOURCE.MASTER_QUEST_AGGRESSIVE},
                'добряк', 'добрячка', 'Увеличивает миролюбие героя, если Мастер получает выгоду от задания и уменьшает, если вред.'),

                personality('BULLY', 3, 'забияка', 'ON_QUEST_HABITS', {QUEST_RESULTS.SUCCESSED: heroes_relations.HABIT_CHANGE_SOURCE.MASTER_QUEST_AGGRESSIVE,
                                                                        QUEST_RESULTS.FAILED: heroes_relations.HABIT_CHANGE_SOURCE.MASTER_QUEST_UNAGGRESSIVE},
                'забияка', 'забияка', 'Уменьшает миролюбие героя, если Мастер получает выгоду от задания и увеличивает, если вред.'),

                personality('LEADER', 4, 'лидер', 'TERRAIN_POWER', 0.1,
                'лидер', 'лидер', 'Оказывает большее влияние на ландшафт вокруг города.'),

                personality('FIDGET', 5, 'непоседа', 'TERRAIN_RADIUS_BONUS', 1,
                'непоседа', 'непоседа', 'Увеличивает радиус изменений ландшафта городом.'),

                personality('GUARANTOR', 6, 'поручитель', 'PLACES_HELP_AMOUNT', 1,
                'поручитель', 'поручительница', 'За выполнение задания, связанного с мастером, герой получает больше известности в каждом городе, связанном с заданием.'),

                personality('NIHILIST', 7, 'нигилист', 'PLACES_HELP_AMOUNT', -0.5,
                'нигилист', 'нигилистка', 'За выполнение задания, связанного с мастером, герой получает меньше известности в каждом городе, связанном с заданием.'),

                personality('RECLUSE', 8, 'затворник', 'PLACES_HELP_AMOUNT', 0,
                'затворник', 'затворница', 'Мастер не оказывает никакого специфического влияния.'),

                personality('ORGANIZER', 9, 'организатор', 'DEMOGRAPHICS_PRESSURE', 1,
                'организатор', 'организатор', 'Увеличивает демографическое давление своей расы в городе.') )


class PERSONALITY_PRACTICAL(PERSONALITY):
    records = ( personality('MULTIWISE', 1, 'многомудрый', 'EXPERIENCE_BONUS', 0.25,
                'многомудрый', 'многомудрая', 'Выполняя задания, связанные с Мастером, герои получают больше опыта.'),

                personality('INFLUENTIAL', 2, 'влиятельный', 'POLITIC_POWER_BONUS', 0.25,
                'влиятельный', 'влиятельная', 'Выполняя задания, связанные с Мастером, герои приносят больше влияния.'),

                personality('GENEROUS', 3, 'щедрый', 'ON_PROFITE_REWARD_BONUS', 2.0,
                'щедрый', 'щедрая', 'Герои получают больше денег за задания, если Мастер получает от него выгоду.'),

                personality('CHARISMATIC', 4, 'харизматичный', 'FRIENDS_QUESTS_PRIORITY_BONUS', c.HABIT_QUEST_PRIORITY_MODIFIER,
                'харизматичный', 'харизматичная', 'Герои чаще берут задания, связанные с Мастером, если это их соратник.'),

                personality('REVENGEFUL', 5, 'мстительный', 'ENEMIES_QUESTS_PRIORITY_BONUS', -c.HABIT_QUEST_PRIORITY_MODIFIER / 2.0,
                'мстительный', 'мстительная', 'Герои реже берут задания, связанные с Мастером, если это их противник.'),

                personality('ACTIVE', 6, 'деятельный', 'POLITIC_RADIUS_BONUS', 1,
                'деятельный', 'деятельная', 'Увеличивает радиус влияния города.'),

                personality('RELIABLE', 7, 'надёжный', 'STABILITY_RENEWING_BONUS', c.PLACE_STABILITY_RECOVER_SPEED * 0.25,
                'надёжный', 'надёжная', 'Увеличивает скорость восстановления стабильности.'),

                personality('ORDERLY', 8, 'аккуратный', 'BUILDING_AMORTIZATION_SPEED', -0.5,
                'аккуратный', 'аккуратная', 'Замедляет амортизацию своего здания.'),

                personality('DEVOUT', 9, 'набожный', 'ON_PROFITE_ENERGY', 4,
                'набожный', 'набожная', 'За каждое задание, в котором Мастер получил выгоду, возносит хвалу Хранителям героев, и те получают немного энергии.'),

                personality('HARDWORKING', 10, 'трудолюбивый', 'JOB_POWER_BONUS', 0.5,
                'трудолюбивый', 'трудолюбивая', 'У занятий Мастера более сильный эффект.'),

                personality('ENTERPRISING', 11, 'предприимчивый', 'JOB_GROUP_PRIORITY', {jobs_effects.EFFECT_GROUP.ON_PLACE: 0.5},
                'предприимчивый', 'предприимчивая', 'Мастер чаще выполняет занятия, связанные с экономикой города.'),

                personality('ROMANTIC', 12, 'романтичный', 'JOB_GROUP_PRIORITY', {jobs_effects.EFFECT_GROUP.ON_HEROES: 0.5},
                'романтичный', 'романтичная', 'Мастер чаще выполняет занятия, связанные с помощью героям.'),

                personality('RESPONSIBLE', 13, 'ответственный', 'SOCIAL_RELATIONS_PARTNERS_POWER_MODIFIER', 0.1,
                'ответственный', 'ответственная', 'Мастер оказывает более сильное влияние на своих парнёров.'),

                personality('INSIDIOUS', 14, 'коварный', 'SOCIAL_RELATIONS_CONCURRENTS_POWER_MODIFIER', 0.1,
                'коварный', 'коварная', 'Мастер оказывает более сильное влияние на своих конкурентов.') )
