
from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [
    ('JOB_NAME_PLACE_PLACE_PRODUCTION', 620000, 'Название: выполняется городом, эффект: «производство»', LEXICON_GROUP.JOBS,
     'Название занятия выполняемого городом, эффект: «производство»', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_NAME_PLACE_PLACE_SAFETY', 620001, 'Название: выполняется городом, эффект: «безопасность»', LEXICON_GROUP.JOBS,
     'Название занятия выполняемого городом, эффект: «безопасность»', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_NAME_PLACE_PLACE_TRANSPORT', 620002, 'Название: выполняется городом, эффект: «транспорт»', LEXICON_GROUP.JOBS,
     'Название занятия выполняемого городом, эффект: «транспорт»', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_NAME_PLACE_PLACE_FREEDOM', 620003, 'Название: выполняется городом, эффект: «свобода»', LEXICON_GROUP.JOBS,
     'Название занятия выполняемого городом, эффект: «свобода»', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_NAME_PLACE_PLACE_STABILITY', 620004, 'Название: выполняется городом, эффект: «стабильность»', LEXICON_GROUP.JOBS,
     'Название занятия выполняемого городом, эффект: «стабильность»', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_NAME_PLACE_HERO_MONEY', 620005, 'Название: выполняется городом, эффект: «золото ближнему кругу»', LEXICON_GROUP.JOBS,
     'Название занятия выполняемого городом, эффект: «золото ближнему кругу»', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_NAME_PLACE_HERO_ARTIFACT', 620006, 'Название: выполняется городом, эффект: «артефакт ближнему кругу»', LEXICON_GROUP.JOBS,
     'Название занятия выполняемого городом, эффект: «артефакт ближнему кругу»', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_NAME_PLACE_HERO_EXPERIENCE', 620007, 'Название: выполняется городом, эффект: «опыт ближнему кругу»', LEXICON_GROUP.JOBS,
     'Название занятия выполняемого городом, эффект: «опыт ближнему кругу»', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_NAME_PLACE_HERO_ENERGY', 620008, 'Название: выполняется городом, эффект: «энергию ближнему кругу»', LEXICON_GROUP.JOBS,
     'Название занятия выполняемого городом, эффект: «энергию ближнему кругу»', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_NAME_PERSON_PLACE_PRODUCTION', 620009, 'Название: выполняется мастером, эффект: «производство»', LEXICON_GROUP.JOBS,
     'Название занятия выполняемого мастером, эффект: «производство»', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_NAME_PERSON_PLACE_SAFETY', 620010, 'Название: выполняется мастером, эффект: «безопасность»', LEXICON_GROUP.JOBS,
     'Название занятия выполняемого мастером, эффект: «безопасность»', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_NAME_PERSON_PLACE_TRANSPORT', 620011, 'Название: выполняется мастером, эффект: «транспорт»', LEXICON_GROUP.JOBS,
     'Название занятия выполняемого мастером, эффект: «транспорт»', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_NAME_PERSON_PLACE_FREEDOM', 620012, 'Название: выполняется мастером, эффект: «свобода»', LEXICON_GROUP.JOBS,
     'Название занятия выполняемого мастером, эффект: «свобода»', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_NAME_PERSON_PLACE_STABILITY', 620013, 'Название: выполняется мастером, эффект: «стабильность»', LEXICON_GROUP.JOBS,
     'Название занятия выполняемого мастером, эффект: «стабильность»', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_NAME_PERSON_HERO_MONEY', 620014, 'Название: выполняется мастером, эффект: «золото ближнему кругу»', LEXICON_GROUP.JOBS,
     'Название занятия выполняемого мастером, эффект: «золото ближнему кругу»', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_NAME_PERSON_HERO_ARTIFACT', 620015, 'Название: выполняется мастером, эффект: «артефакт ближнему кругу»', LEXICON_GROUP.JOBS,
     'Название занятия выполняемого мастером, эффект: «артефакт ближнему кругу»', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_NAME_PERSON_HERO_EXPERIENCE', 620016, 'Название: выполняется мастером, эффект: «опыт ближнему кругу»', LEXICON_GROUP.JOBS,
     'Название занятия выполняемого мастером, эффект: «опыт ближнему кругу»', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_NAME_PERSON_HERO_ENERGY', 620017, 'Название: выполняется мастером, эффект: «энергию ближнему кругу»', LEXICON_GROUP.JOBS,
     'Название занятия выполняемого мастером, эффект: «энергию ближнему кругу»', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PLACE_PLACE_PRODUCTION_POSITIVE_FRIENDS', 620018, 'Дневник: работа выполнена городом успешно, эффект: «производство», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом успешно, эффект: «производство», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PLACE_PLACE_PRODUCTION_POSITIVE_ENEMIES', 620019, 'Дневник: работа выполнена городом успешно, эффект: «производство», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом успешно, эффект: «производство», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PLACE_PLACE_PRODUCTION_NEGATIVE_FRIENDS', 620020, 'Дневник: работа выполнена городом не успешно, эффект: «производство», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом не успешно, эффект: «производство», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PLACE_PLACE_PRODUCTION_NEGATIVE_ENEMIES', 620021, 'Дневник: работа выполнена городом не успешно, эффект: «производство», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом не успешно, эффект: «производство», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PLACE_PLACE_SAFETY_POSITIVE_FRIENDS', 620022, 'Дневник: работа выполнена городом успешно, эффект: «безопасность», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом успешно, эффект: «безопасность», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PLACE_PLACE_SAFETY_POSITIVE_ENEMIES', 620023, 'Дневник: работа выполнена городом успешно, эффект: «безопасность», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом успешно, эффект: «безопасность», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PLACE_PLACE_SAFETY_NEGATIVE_FRIENDS', 620024, 'Дневник: работа выполнена городом не успешно, эффект: «безопасность», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом не успешно, эффект: «безопасность», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PLACE_PLACE_SAFETY_NEGATIVE_ENEMIES', 620025, 'Дневник: работа выполнена городом не успешно, эффект: «безопасность», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом не успешно, эффект: «безопасность», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PLACE_PLACE_TRANSPORT_POSITIVE_FRIENDS', 620026, 'Дневник: работа выполнена городом успешно, эффект: «транспорт», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом успешно, эффект: «транспорт», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PLACE_PLACE_TRANSPORT_POSITIVE_ENEMIES', 620027, 'Дневник: работа выполнена городом успешно, эффект: «транспорт», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом успешно, эффект: «транспорт», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PLACE_PLACE_TRANSPORT_NEGATIVE_FRIENDS', 620028, 'Дневник: работа выполнена городом не успешно, эффект: «транспорт», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом не успешно, эффект: «транспорт», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PLACE_PLACE_TRANSPORT_NEGATIVE_ENEMIES', 620029, 'Дневник: работа выполнена городом не успешно, эффект: «транспорт», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом не успешно, эффект: «транспорт», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PLACE_PLACE_FREEDOM_POSITIVE_FRIENDS', 620030, 'Дневник: работа выполнена городом успешно, эффект: «свобода», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом успешно, эффект: «свобода», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PLACE_PLACE_FREEDOM_POSITIVE_ENEMIES', 620031, 'Дневник: работа выполнена городом успешно, эффект: «свобода», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом успешно, эффект: «свобода», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PLACE_PLACE_FREEDOM_NEGATIVE_FRIENDS', 620032, 'Дневник: работа выполнена городом не успешно, эффект: «свобода», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом не успешно, эффект: «свобода», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PLACE_PLACE_FREEDOM_NEGATIVE_ENEMIES', 620033, 'Дневник: работа выполнена городом не успешно, эффект: «свобода», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом не успешно, эффект: «свобода», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PLACE_PLACE_STABILITY_POSITIVE_FRIENDS', 620034, 'Дневник: работа выполнена городом успешно, эффект: «стабильность», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом успешно, эффект: «стабильность», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PLACE_PLACE_STABILITY_POSITIVE_ENEMIES', 620035, 'Дневник: работа выполнена городом успешно, эффект: «стабильность», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом успешно, эффект: «стабильность», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PLACE_PLACE_STABILITY_NEGATIVE_FRIENDS', 620036, 'Дневник: работа выполнена городом не успешно, эффект: «стабильность», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом не успешно, эффект: «стабильность», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PLACE_PLACE_STABILITY_NEGATIVE_ENEMIES', 620037, 'Дневник: работа выполнена городом не успешно, эффект: «стабильность», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом не успешно, эффект: «стабильность», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PLACE_HERO_MONEY_POSITIVE_FRIENDS', 620038, 'Дневник: работа выполнена городом успешно, эффект: «золото ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом успешно, эффект: «золото ближнему кругу», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.COINS], 'hero#N +coins#G'),
    ('JOB_DIARY_PLACE_HERO_MONEY_POSITIVE_ENEMIES', 620039, 'Дневник: работа выполнена городом успешно, эффект: «золото ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом успешно, эффект: «золото ближнему кругу», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PLACE_HERO_MONEY_NEGATIVE_FRIENDS', 620040, 'Дневник: работа выполнена городом не успешно, эффект: «золото ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом не успешно, эффект: «золото ближнему кругу», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PLACE_HERO_MONEY_NEGATIVE_ENEMIES', 620041, 'Дневник: работа выполнена городом не успешно, эффект: «золото ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом не успешно, эффект: «золото ближнему кругу», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.COINS], 'hero#N +coins#G'),
    ('JOB_DIARY_PLACE_HERO_ARTIFACT_POSITIVE_FRIENDS', 620042, 'Дневник: работа выполнена городом успешно, эффект: «артефакт ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом успешно, эффект: «артефакт ближнему кругу», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.ARTIFACT], None),
    ('JOB_DIARY_PLACE_HERO_ARTIFACT_POSITIVE_ENEMIES', 620043, 'Дневник: работа выполнена городом успешно, эффект: «артефакт ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом успешно, эффект: «артефакт ближнему кругу», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PLACE_HERO_ARTIFACT_NEGATIVE_FRIENDS', 620044, 'Дневник: работа выполнена городом не успешно, эффект: «артефакт ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом не успешно, эффект: «артефакт ближнему кругу», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PLACE_HERO_ARTIFACT_NEGATIVE_ENEMIES', 620045, 'Дневник: работа выполнена городом не успешно, эффект: «артефакт ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом не успешно, эффект: «артефакт ближнему кругу», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.ARTIFACT], None),
    ('JOB_DIARY_PLACE_HERO_EXPERIENCE_POSITIVE_FRIENDS', 620046, 'Дневник: работа выполнена городом успешно, эффект: «опыт ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом успешно, эффект: «опыт ближнему кругу», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.EXPERIENCE], 'hero#N +experience#EXP'),
    ('JOB_DIARY_PLACE_HERO_EXPERIENCE_POSITIVE_ENEMIES', 620047, 'Дневник: работа выполнена городом успешно, эффект: «опыт ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом успешно, эффект: «опыт ближнему кругу», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PLACE_HERO_EXPERIENCE_NEGATIVE_FRIENDS', 620048, 'Дневник: работа выполнена городом не успешно, эффект: «опыт ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом не успешно, эффект: «опыт ближнему кругу», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PLACE_HERO_EXPERIENCE_NEGATIVE_ENEMIES', 620049, 'Дневник: работа выполнена городом не успешно, эффект: «опыт ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом не успешно, эффект: «опыт ближнему кругу», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.EXPERIENCE], 'hero#N +experience#EXP'),
    ('JOB_DIARY_PLACE_HERO_ENERGY_POSITIVE_FRIENDS', 620050, 'Дневник: работа выполнена городом успешно, эффект: «энергию ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом успешно, эффект: «энергию ближнему кругу», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.ENERGY], 'hero#N +energy#EN'),
    ('JOB_DIARY_PLACE_HERO_ENERGY_POSITIVE_ENEMIES', 620051, 'Дневник: работа выполнена городом успешно, эффект: «энергию ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом успешно, эффект: «энергию ближнему кругу», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PLACE_HERO_ENERGY_NEGATIVE_FRIENDS', 620052, 'Дневник: работа выполнена городом не успешно, эффект: «энергию ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом не успешно, эффект: «энергию ближнему кругу», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PLACE_HERO_ENERGY_NEGATIVE_ENEMIES', 620053, 'Дневник: работа выполнена городом не успешно, эффект: «энергию ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом не успешно, эффект: «энергию ближнему кругу», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.ENERGY], 'hero#N +energy#EN'),
    ('JOB_DIARY_PERSON_PLACE_PRODUCTION_POSITIVE_FRIENDS', 620054, 'Дневник: работа выполнена мастером успешно, эффект: «производство», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером успешно, эффект: «производство», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PERSON_PLACE_PRODUCTION_POSITIVE_ENEMIES', 620055, 'Дневник: работа выполнена мастером успешно, эффект: «производство», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером успешно, эффект: «производство», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PERSON_PLACE_PRODUCTION_NEGATIVE_FRIENDS', 620056, 'Дневник: работа выполнена мастером не успешно, эффект: «производство», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером не успешно, эффект: «производство», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PERSON_PLACE_PRODUCTION_NEGATIVE_ENEMIES', 620057, 'Дневник: работа выполнена мастером не успешно, эффект: «производство», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером не успешно, эффект: «производство», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PERSON_PLACE_SAFETY_POSITIVE_FRIENDS', 620058, 'Дневник: работа выполнена мастером успешно, эффект: «безопасность», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером успешно, эффект: «безопасность», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PERSON_PLACE_SAFETY_POSITIVE_ENEMIES', 620059, 'Дневник: работа выполнена мастером успешно, эффект: «безопасность», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером успешно, эффект: «безопасность», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PERSON_PLACE_SAFETY_NEGATIVE_FRIENDS', 620060, 'Дневник: работа выполнена мастером не успешно, эффект: «безопасность», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером не успешно, эффект: «безопасность», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PERSON_PLACE_SAFETY_NEGATIVE_ENEMIES', 620061, 'Дневник: работа выполнена мастером не успешно, эффект: «безопасность», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером не успешно, эффект: «безопасность», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PERSON_PLACE_TRANSPORT_POSITIVE_FRIENDS', 620062, 'Дневник: работа выполнена мастером успешно, эффект: «транспорт», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером успешно, эффект: «транспорт», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PERSON_PLACE_TRANSPORT_POSITIVE_ENEMIES', 620063, 'Дневник: работа выполнена мастером успешно, эффект: «транспорт», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером успешно, эффект: «транспорт», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PERSON_PLACE_TRANSPORT_NEGATIVE_FRIENDS', 620064, 'Дневник: работа выполнена мастером не успешно, эффект: «транспорт», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером не успешно, эффект: «транспорт», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PERSON_PLACE_TRANSPORT_NEGATIVE_ENEMIES', 620065, 'Дневник: работа выполнена мастером не успешно, эффект: «транспорт», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером не успешно, эффект: «транспорт», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PERSON_PLACE_FREEDOM_POSITIVE_FRIENDS', 620066, 'Дневник: работа выполнена мастером успешно, эффект: «свобода», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером успешно, эффект: «свобода», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PERSON_PLACE_FREEDOM_POSITIVE_ENEMIES', 620067, 'Дневник: работа выполнена мастером успешно, эффект: «свобода», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером успешно, эффект: «свобода», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PERSON_PLACE_FREEDOM_NEGATIVE_FRIENDS', 620068, 'Дневник: работа выполнена мастером не успешно, эффект: «свобода», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером не успешно, эффект: «свобода», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PERSON_PLACE_FREEDOM_NEGATIVE_ENEMIES', 620069, 'Дневник: работа выполнена мастером не успешно, эффект: «свобода», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером не успешно, эффект: «свобода», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PERSON_PLACE_STABILITY_POSITIVE_FRIENDS', 620070, 'Дневник: работа выполнена мастером успешно, эффект: «стабильность», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером успешно, эффект: «стабильность», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PERSON_PLACE_STABILITY_POSITIVE_ENEMIES', 620071, 'Дневник: работа выполнена мастером успешно, эффект: «стабильность», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером успешно, эффект: «стабильность», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PERSON_PLACE_STABILITY_NEGATIVE_FRIENDS', 620072, 'Дневник: работа выполнена мастером не успешно, эффект: «стабильность», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером не успешно, эффект: «стабильность», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PERSON_PLACE_STABILITY_NEGATIVE_ENEMIES', 620073, 'Дневник: работа выполнена мастером не успешно, эффект: «стабильность», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером не успешно, эффект: «стабильность», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PERSON_HERO_MONEY_POSITIVE_FRIENDS', 620074, 'Дневник: работа выполнена мастером успешно, эффект: «золото ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером успешно, эффект: «золото ближнему кругу», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON, V.COINS], 'hero#N +coins#G'),
    ('JOB_DIARY_PERSON_HERO_MONEY_POSITIVE_ENEMIES', 620075, 'Дневник: работа выполнена мастером успешно, эффект: «золото ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером успешно, эффект: «золото ближнему кругу», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PERSON_HERO_MONEY_NEGATIVE_FRIENDS', 620076, 'Дневник: работа выполнена мастером не успешно, эффект: «золото ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером не успешно, эффект: «золото ближнему кругу», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PERSON_HERO_MONEY_NEGATIVE_ENEMIES', 620077, 'Дневник: работа выполнена мастером не успешно, эффект: «золото ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером не успешно, эффект: «золото ближнему кругу», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON, V.COINS], 'hero#N +coins#G'),
    ('JOB_DIARY_PERSON_HERO_ARTIFACT_POSITIVE_FRIENDS', 620078, 'Дневник: работа выполнена мастером успешно, эффект: «артефакт ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером успешно, эффект: «артефакт ближнему кругу», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON, V.ARTIFACT], None),
    ('JOB_DIARY_PERSON_HERO_ARTIFACT_POSITIVE_ENEMIES', 620079, 'Дневник: работа выполнена мастером успешно, эффект: «артефакт ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером успешно, эффект: «артефакт ближнему кругу», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PERSON_HERO_ARTIFACT_NEGATIVE_FRIENDS', 620080, 'Дневник: работа выполнена мастером не успешно, эффект: «артефакт ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером не успешно, эффект: «артефакт ближнему кругу», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PERSON_HERO_ARTIFACT_NEGATIVE_ENEMIES', 620081, 'Дневник: работа выполнена мастером не успешно, эффект: «артефакт ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером не успешно, эффект: «артефакт ближнему кругу», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON, V.ARTIFACT], None),
    ('JOB_DIARY_PERSON_HERO_EXPERIENCE_POSITIVE_FRIENDS', 620082, 'Дневник: работа выполнена мастером успешно, эффект: «опыт ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером успешно, эффект: «опыт ближнему кругу», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON, V.EXPERIENCE], 'hero#N +experience#EXP'),
    ('JOB_DIARY_PERSON_HERO_EXPERIENCE_POSITIVE_ENEMIES', 620083, 'Дневник: работа выполнена мастером успешно, эффект: «опыт ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером успешно, эффект: «опыт ближнему кругу», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PERSON_HERO_EXPERIENCE_NEGATIVE_FRIENDS', 620084, 'Дневник: работа выполнена мастером не успешно, эффект: «опыт ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером не успешно, эффект: «опыт ближнему кругу», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PERSON_HERO_EXPERIENCE_NEGATIVE_ENEMIES', 620085, 'Дневник: работа выполнена мастером не успешно, эффект: «опыт ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером не успешно, эффект: «опыт ближнему кругу», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON, V.EXPERIENCE], 'hero#N +experience#EXP'),
    ('JOB_DIARY_PERSON_HERO_ENERGY_POSITIVE_FRIENDS', 620086, 'Дневник: работа выполнена мастером успешно, эффект: «энергию ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером успешно, эффект: «энергию ближнему кругу», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON, V.ENERGY], 'hero#N +energy#EN'),
    ('JOB_DIARY_PERSON_HERO_ENERGY_POSITIVE_ENEMIES', 620087, 'Дневник: работа выполнена мастером успешно, эффект: «энергию ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером успешно, эффект: «энергию ближнему кругу», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PERSON_HERO_ENERGY_NEGATIVE_FRIENDS', 620088, 'Дневник: работа выполнена мастером не успешно, эффект: «энергию ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером не успешно, эффект: «энергию ближнему кругу», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PERSON_HERO_ENERGY_NEGATIVE_ENEMIES', 620089, 'Дневник: работа выполнена мастером не успешно, эффект: «энергию ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером не успешно, эффект: «энергию ближнему кругу», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON, V.ENERGY], 'hero#N +energy#EN'),

    ('JOB_NAME_PLACE_PLACE_CULTURE', 620090, 'Название: выполняется городом, эффект: «культура»', LEXICON_GROUP.JOBS,
     'Название занятия выполняемого городом, эффект: «культура»', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_NAME_PERSON_PLACE_CULTURE', 620091, 'Название: выполняется мастером, эффект: «культура»', LEXICON_GROUP.JOBS,
     'Название занятия выполняемого мастером, эффект: «культура»', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PLACE_PLACE_CULTURE_POSITIVE_FRIENDS', 620092, 'Дневник: работа выполнена городом успешно, эффект: «культура», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом успешно, эффект: «культура», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PLACE_PLACE_CULTURE_POSITIVE_ENEMIES', 620093, 'Дневник: работа выполнена городом успешно, эффект: «культура», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом успешно, эффект: «культура», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PLACE_PLACE_CULTURE_NEGATIVE_FRIENDS', 620094, 'Дневник: работа выполнена городом не успешно, эффект: «культура», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом не успешно, эффект: «культура», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PLACE_PLACE_CULTURE_NEGATIVE_ENEMIES', 620095, 'Дневник: работа выполнена городом не успешно, эффект: «культура», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена городом не успешно, эффект: «культура», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE], None),
    ('JOB_DIARY_PERSON_PLACE_CULTURE_POSITIVE_FRIENDS', 620096, 'Дневник: работа выполнена мастером успешно, эффект: «культура», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером успешно, эффект: «культура», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PERSON_PLACE_CULTURE_POSITIVE_ENEMIES', 620097, 'Дневник: работа выполнена мастером успешно, эффект: «культура», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером успешно, эффект: «культура», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PERSON_PLACE_CULTURE_NEGATIVE_FRIENDS', 620098, 'Дневник: работа выполнена мастером не успешно, эффект: «культура», сообщение для соратников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером не успешно, эффект: «культура», сообщение для соратников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
    ('JOB_DIARY_PERSON_PLACE_CULTURE_NEGATIVE_ENEMIES', 620099, 'Дневник: работа выполнена мастером не успешно, эффект: «культура», сообщение для противников', LEXICON_GROUP.JOBS,
     'Работа выполнена мастером не успешно, эффект: «культура», сообщение для противников', [V.DATE, V.TIME, V.HERO, V.PLACE, V.PERSON], None),
         ]


# Код для автоматической генерации типов сообщений

# from the_tale.game.jobs import effects


# DIARY_NAME_TEMPLATE = u'Дневник: работа выполнена {actor} {direction}, эффект: «{effect}», сообщение для {group}'
# DIARY_DESCR_TEMPLATE = u'Работа выполнена {actor} {direction}, эффект: «{effect}», сообщение для {group}'

# NAME_NAME_TEMPLATE = u'Название: выполняется {actor}, эффект: «{effect}»'
# NAME_DESCR_TEMPLATE = u'Название занятия выполняемого {actor}, эффект: «{effect}»'


# def name_record(actor, effect, index):
#     name = u'job_name_{actor}_{effect}'.format(actor=actor, effect=effect.name).upper()

#     arguments = {'actor': {'place': u'городом', 'person': u'мастером'}[actor],
#                  'effect': effect.text}

#     variables = [V.HERO, V.PLACE]
#     if actor == 'person':
#         variables.append(V.PERSON)

#     return (name,
#             LEXICON_GROUP.JOBS.index_group + index,
#             NAME_NAME_TEMPLATE.format(**arguments),
#             LEXICON_GROUP.JOBS,
#             NAME_DESCR_TEMPLATE.format(**arguments),
#             variables,
#             None)


# def diary_record(actor, effect, direction, group, index):
#     name = u'job_diary_{actor}_{effect}_{direction}_{group}'.format(actor=actor,
#                                                                     effect=effect.name,
#                                                                     direction=direction,
#                                                                     group=group).upper()

#     arguments = {'actor': {'place': u'городом', 'person': u'мастером'}[actor],
#                  'direction': {'positive': u'успешно', 'negative': u'не успешно'}[direction],
#                  'effect': effect.text,
#                  'group': {'friends': u'соратников', 'enemies': u'противников'}[group]}

#     ui_template = None

#     variables = [V.HERO, V.PLACE]
#     if actor == 'person':
#         variables.append(V.PERSON)

#     has_rewards = ((direction, group) == ('positive', 'friends')) or ((direction, group) == ('negative', 'enemies'))

#     if effect.is_HERO_MONEY and has_rewards:
#         variables.append(V.COINS)
#         ui_template = u'hero#N +coins#G'

#     if effect.is_HERO_ARTIFACT and has_rewards:
#         variables.append(V.ARTIFACT)

#     if effect.is_HERO_EXPERIENCE and has_rewards:
#         variables.append(V.EXPERIENCE)
#         ui_template = u'hero#N +experience#EXP'

#     if effect.is_HERO_ENERGY and has_rewards:
#         variables.append(V.ENERGY)
#         ui_template = u'hero#N +energy#EN'

#     return (name,
#             LEXICON_GROUP.JOBS.index_group + index,
#             DIARY_NAME_TEMPLATE.format(**arguments),
#             LEXICON_GROUP.JOBS,
#             DIARY_DESCR_TEMPLATE.format(**arguments),
#             variables,
#             ui_template)


# def create_keys():
#     keys = []

#     index = 0

#     for actor in ('place', 'person'):
#         for effect in effects.EFFECT.records:
#             keys.append(name_record(actor, effect, index))
#             index += 1

#     for actor in ('place', 'person'):
#         for effect in effects.EFFECT.records:
#             for direction in ('positive', 'negative'):
#                 for group in ('friends', 'enemies'):
#                     keys.append(diary_record(actor, effect, direction, group, index))
#                     index += 1

#     return keys

# KEYS = create_keys()
