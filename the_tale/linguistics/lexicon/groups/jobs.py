# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [
    (u'JOB_NAME_PLACE_PLACE_PRODUCTION', 620000, u'Название: выполняется городом, эффект: «производство»', LEXICON_GROUP.JOBS,
     u'Название занятия выполняемого городом, эффект: «производство»', [V.HERO, V.PLACE], None),
    (u'JOB_NAME_PLACE_PLACE_SAFETY', 620001, u'Название: выполняется городом, эффект: «безопасность»', LEXICON_GROUP.JOBS,
     u'Название занятия выполняемого городом, эффект: «безопасность»', [V.HERO, V.PLACE], None),
    (u'JOB_NAME_PLACE_PLACE_TRANSPORT', 620002, u'Название: выполняется городом, эффект: «транспорт»', LEXICON_GROUP.JOBS,
     u'Название занятия выполняемого городом, эффект: «транспорт»', [V.HERO, V.PLACE], None),
    (u'JOB_NAME_PLACE_PLACE_FREEDOM', 620003, u'Название: выполняется городом, эффект: «свобода»', LEXICON_GROUP.JOBS,
     u'Название занятия выполняемого городом, эффект: «свобода»', [V.HERO, V.PLACE], None),
    (u'JOB_NAME_PLACE_PLACE_STABILITY', 620004, u'Название: выполняется городом, эффект: «стабильность»', LEXICON_GROUP.JOBS,
     u'Название занятия выполняемого городом, эффект: «стабильность»', [V.HERO, V.PLACE], None),
    (u'JOB_NAME_PLACE_HERO_MONEY', 620005, u'Название: выполняется городом, эффект: «золото ближнему кругу»', LEXICON_GROUP.JOBS,
     u'Название занятия выполняемого городом, эффект: «золото ближнему кругу»', [V.HERO, V.PLACE], None),
    (u'JOB_NAME_PLACE_HERO_ARTIFACT', 620006, u'Название: выполняется городом, эффект: «артефакт ближнему кругу»', LEXICON_GROUP.JOBS,
     u'Название занятия выполняемого городом, эффект: «артефакт ближнему кругу»', [V.HERO, V.PLACE], None),
    (u'JOB_NAME_PLACE_HERO_EXPERIENCE', 620007, u'Название: выполняется городом, эффект: «опыт ближнему кругу»', LEXICON_GROUP.JOBS,
     u'Название занятия выполняемого городом, эффект: «опыт ближнему кругу»', [V.HERO, V.PLACE], None),
    (u'JOB_NAME_PLACE_HERO_ENERGY', 620008, u'Название: выполняется городом, эффект: «энергию ближнему кругу»', LEXICON_GROUP.JOBS,
     u'Название занятия выполняемого городом, эффект: «энергию ближнему кругу»', [V.HERO, V.PLACE], None),
    (u'JOB_NAME_PERSON_PLACE_PRODUCTION', 620009, u'Название: выполняется мастером, эффект: «производство»', LEXICON_GROUP.JOBS,
     u'Название занятия выполняемого мастером, эффект: «производство»', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_NAME_PERSON_PLACE_SAFETY', 620010, u'Название: выполняется мастером, эффект: «безопасность»', LEXICON_GROUP.JOBS,
     u'Название занятия выполняемого мастером, эффект: «безопасность»', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_NAME_PERSON_PLACE_TRANSPORT', 620011, u'Название: выполняется мастером, эффект: «транспорт»', LEXICON_GROUP.JOBS,
     u'Название занятия выполняемого мастером, эффект: «транспорт»', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_NAME_PERSON_PLACE_FREEDOM', 620012, u'Название: выполняется мастером, эффект: «свобода»', LEXICON_GROUP.JOBS,
     u'Название занятия выполняемого мастером, эффект: «свобода»', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_NAME_PERSON_PLACE_STABILITY', 620013, u'Название: выполняется мастером, эффект: «стабильность»', LEXICON_GROUP.JOBS,
     u'Название занятия выполняемого мастером, эффект: «стабильность»', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_NAME_PERSON_HERO_MONEY', 620014, u'Название: выполняется мастером, эффект: «золото ближнему кругу»', LEXICON_GROUP.JOBS,
     u'Название занятия выполняемого мастером, эффект: «золото ближнему кругу»', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_NAME_PERSON_HERO_ARTIFACT', 620015, u'Название: выполняется мастером, эффект: «артефакт ближнему кругу»', LEXICON_GROUP.JOBS,
     u'Название занятия выполняемого мастером, эффект: «артефакт ближнему кругу»', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_NAME_PERSON_HERO_EXPERIENCE', 620016, u'Название: выполняется мастером, эффект: «опыт ближнему кругу»', LEXICON_GROUP.JOBS,
     u'Название занятия выполняемого мастером, эффект: «опыт ближнему кругу»', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_NAME_PERSON_HERO_ENERGY', 620017, u'Название: выполняется мастером, эффект: «энергию ближнему кругу»', LEXICON_GROUP.JOBS,
     u'Название занятия выполняемого мастером, эффект: «энергию ближнему кругу»', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_DIARY_PLACE_PLACE_PRODUCTION_POSITIVE_FRIENDS', 620018, u'Дневник: работа выполнена городом успешно, эффект: «производство», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом успешно, эффект: «производство», сообщение для соратников', [V.HERO, V.PLACE], None),
    (u'JOB_DIARY_PLACE_PLACE_PRODUCTION_POSITIVE_ENEMIES', 620019, u'Дневник: работа выполнена городом успешно, эффект: «производство», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом успешно, эффект: «производство», сообщение для противников', [V.HERO, V.PLACE], None),
    (u'JOB_DIARY_PLACE_PLACE_PRODUCTION_NEGATIVE_FRIENDS', 620020, u'Дневник: работа выполнена городом не успешно, эффект: «производство», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом не успешно, эффект: «производство», сообщение для соратников', [V.HERO, V.PLACE], None),
    (u'JOB_DIARY_PLACE_PLACE_PRODUCTION_NEGATIVE_ENEMIES', 620021, u'Дневник: работа выполнена городом не успешно, эффект: «производство», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом не успешно, эффект: «производство», сообщение для противников', [V.HERO, V.PLACE], None),
    (u'JOB_DIARY_PLACE_PLACE_SAFETY_POSITIVE_FRIENDS', 620022, u'Дневник: работа выполнена городом успешно, эффект: «безопасность», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом успешно, эффект: «безопасность», сообщение для соратников', [V.HERO, V.PLACE], None),
    (u'JOB_DIARY_PLACE_PLACE_SAFETY_POSITIVE_ENEMIES', 620023, u'Дневник: работа выполнена городом успешно, эффект: «безопасность», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом успешно, эффект: «безопасность», сообщение для противников', [V.HERO, V.PLACE], None),
    (u'JOB_DIARY_PLACE_PLACE_SAFETY_NEGATIVE_FRIENDS', 620024, u'Дневник: работа выполнена городом не успешно, эффект: «безопасность», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом не успешно, эффект: «безопасность», сообщение для соратников', [V.HERO, V.PLACE], None),
    (u'JOB_DIARY_PLACE_PLACE_SAFETY_NEGATIVE_ENEMIES', 620025, u'Дневник: работа выполнена городом не успешно, эффект: «безопасность», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом не успешно, эффект: «безопасность», сообщение для противников', [V.HERO, V.PLACE], None),
    (u'JOB_DIARY_PLACE_PLACE_TRANSPORT_POSITIVE_FRIENDS', 620026, u'Дневник: работа выполнена городом успешно, эффект: «транспорт», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом успешно, эффект: «транспорт», сообщение для соратников', [V.HERO, V.PLACE], None),
    (u'JOB_DIARY_PLACE_PLACE_TRANSPORT_POSITIVE_ENEMIES', 620027, u'Дневник: работа выполнена городом успешно, эффект: «транспорт», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом успешно, эффект: «транспорт», сообщение для противников', [V.HERO, V.PLACE], None),
    (u'JOB_DIARY_PLACE_PLACE_TRANSPORT_NEGATIVE_FRIENDS', 620028, u'Дневник: работа выполнена городом не успешно, эффект: «транспорт», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом не успешно, эффект: «транспорт», сообщение для соратников', [V.HERO, V.PLACE], None),
    (u'JOB_DIARY_PLACE_PLACE_TRANSPORT_NEGATIVE_ENEMIES', 620029, u'Дневник: работа выполнена городом не успешно, эффект: «транспорт», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом не успешно, эффект: «транспорт», сообщение для противников', [V.HERO, V.PLACE], None),
    (u'JOB_DIARY_PLACE_PLACE_FREEDOM_POSITIVE_FRIENDS', 620030, u'Дневник: работа выполнена городом успешно, эффект: «свобода», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом успешно, эффект: «свобода», сообщение для соратников', [V.HERO, V.PLACE], None),
    (u'JOB_DIARY_PLACE_PLACE_FREEDOM_POSITIVE_ENEMIES', 620031, u'Дневник: работа выполнена городом успешно, эффект: «свобода», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом успешно, эффект: «свобода», сообщение для противников', [V.HERO, V.PLACE], None),
    (u'JOB_DIARY_PLACE_PLACE_FREEDOM_NEGATIVE_FRIENDS', 620032, u'Дневник: работа выполнена городом не успешно, эффект: «свобода», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом не успешно, эффект: «свобода», сообщение для соратников', [V.HERO, V.PLACE], None),
    (u'JOB_DIARY_PLACE_PLACE_FREEDOM_NEGATIVE_ENEMIES', 620033, u'Дневник: работа выполнена городом не успешно, эффект: «свобода», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом не успешно, эффект: «свобода», сообщение для противников', [V.HERO, V.PLACE], None),
    (u'JOB_DIARY_PLACE_PLACE_STABILITY_POSITIVE_FRIENDS', 620034, u'Дневник: работа выполнена городом успешно, эффект: «стабильность», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом успешно, эффект: «стабильность», сообщение для соратников', [V.HERO, V.PLACE], None),
    (u'JOB_DIARY_PLACE_PLACE_STABILITY_POSITIVE_ENEMIES', 620035, u'Дневник: работа выполнена городом успешно, эффект: «стабильность», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом успешно, эффект: «стабильность», сообщение для противников', [V.HERO, V.PLACE], None),
    (u'JOB_DIARY_PLACE_PLACE_STABILITY_NEGATIVE_FRIENDS', 620036, u'Дневник: работа выполнена городом не успешно, эффект: «стабильность», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом не успешно, эффект: «стабильность», сообщение для соратников', [V.HERO, V.PLACE], None),
    (u'JOB_DIARY_PLACE_PLACE_STABILITY_NEGATIVE_ENEMIES', 620037, u'Дневник: работа выполнена городом не успешно, эффект: «стабильность», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом не успешно, эффект: «стабильность», сообщение для противников', [V.HERO, V.PLACE], None),
    (u'JOB_DIARY_PLACE_HERO_MONEY_POSITIVE_FRIENDS', 620038, u'Дневник: работа выполнена городом успешно, эффект: «золото ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом успешно, эффект: «золото ближнему кругу», сообщение для соратников', [V.HERO, V.PLACE, V.COINS], u'hero#N +coins#G'),
    (u'JOB_DIARY_PLACE_HERO_MONEY_POSITIVE_ENEMIES', 620039, u'Дневник: работа выполнена городом успешно, эффект: «золото ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом успешно, эффект: «золото ближнему кругу», сообщение для противников', [V.HERO, V.PLACE], None),
    (u'JOB_DIARY_PLACE_HERO_MONEY_NEGATIVE_FRIENDS', 620040, u'Дневник: работа выполнена городом не успешно, эффект: «золото ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом не успешно, эффект: «золото ближнему кругу», сообщение для соратников', [V.HERO, V.PLACE], None),
    (u'JOB_DIARY_PLACE_HERO_MONEY_NEGATIVE_ENEMIES', 620041, u'Дневник: работа выполнена городом не успешно, эффект: «золото ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом не успешно, эффект: «золото ближнему кругу», сообщение для противников', [V.HERO, V.PLACE, V.COINS], u'hero#N +coins#G'),
    (u'JOB_DIARY_PLACE_HERO_ARTIFACT_POSITIVE_FRIENDS', 620042, u'Дневник: работа выполнена городом успешно, эффект: «артефакт ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом успешно, эффект: «артефакт ближнему кругу», сообщение для соратников', [V.HERO, V.PLACE, V.ARTIFACT], None),
    (u'JOB_DIARY_PLACE_HERO_ARTIFACT_POSITIVE_ENEMIES', 620043, u'Дневник: работа выполнена городом успешно, эффект: «артефакт ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом успешно, эффект: «артефакт ближнему кругу», сообщение для противников', [V.HERO, V.PLACE], None),
    (u'JOB_DIARY_PLACE_HERO_ARTIFACT_NEGATIVE_FRIENDS', 620044, u'Дневник: работа выполнена городом не успешно, эффект: «артефакт ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом не успешно, эффект: «артефакт ближнему кругу», сообщение для соратников', [V.HERO, V.PLACE], None),
    (u'JOB_DIARY_PLACE_HERO_ARTIFACT_NEGATIVE_ENEMIES', 620045, u'Дневник: работа выполнена городом не успешно, эффект: «артефакт ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом не успешно, эффект: «артефакт ближнему кругу», сообщение для противников', [V.HERO, V.PLACE, V.ARTIFACT], None),
    (u'JOB_DIARY_PLACE_HERO_EXPERIENCE_POSITIVE_FRIENDS', 620046, u'Дневник: работа выполнена городом успешно, эффект: «опыт ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом успешно, эффект: «опыт ближнему кругу», сообщение для соратников', [V.HERO, V.PLACE, V.EXPERIENCE], u'hero#N +experience#EXP'),
    (u'JOB_DIARY_PLACE_HERO_EXPERIENCE_POSITIVE_ENEMIES', 620047, u'Дневник: работа выполнена городом успешно, эффект: «опыт ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом успешно, эффект: «опыт ближнему кругу», сообщение для противников', [V.HERO, V.PLACE], None),
    (u'JOB_DIARY_PLACE_HERO_EXPERIENCE_NEGATIVE_FRIENDS', 620048, u'Дневник: работа выполнена городом не успешно, эффект: «опыт ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом не успешно, эффект: «опыт ближнему кругу», сообщение для соратников', [V.HERO, V.PLACE], None),
    (u'JOB_DIARY_PLACE_HERO_EXPERIENCE_NEGATIVE_ENEMIES', 620049, u'Дневник: работа выполнена городом не успешно, эффект: «опыт ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом не успешно, эффект: «опыт ближнему кругу», сообщение для противников', [V.HERO, V.PLACE, V.EXPERIENCE], u'hero#N +experience#EXP'),
    (u'JOB_DIARY_PLACE_HERO_ENERGY_POSITIVE_FRIENDS', 620050, u'Дневник: работа выполнена городом успешно, эффект: «энергию ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом успешно, эффект: «энергию ближнему кругу», сообщение для соратников', [V.HERO, V.PLACE, V.ENERGY], u'hero#N +energy#EN'),
    (u'JOB_DIARY_PLACE_HERO_ENERGY_POSITIVE_ENEMIES', 620051, u'Дневник: работа выполнена городом успешно, эффект: «энергию ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом успешно, эффект: «энергию ближнему кругу», сообщение для противников', [V.HERO, V.PLACE], None),
    (u'JOB_DIARY_PLACE_HERO_ENERGY_NEGATIVE_FRIENDS', 620052, u'Дневник: работа выполнена городом не успешно, эффект: «энергию ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом не успешно, эффект: «энергию ближнему кругу», сообщение для соратников', [V.HERO, V.PLACE], None),
    (u'JOB_DIARY_PLACE_HERO_ENERGY_NEGATIVE_ENEMIES', 620053, u'Дневник: работа выполнена городом не успешно, эффект: «энергию ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена городом не успешно, эффект: «энергию ближнему кругу», сообщение для противников', [V.HERO, V.PLACE, V.ENERGY], u'hero#N +energy#EN'),
    (u'JOB_DIARY_PERSON_PLACE_PRODUCTION_POSITIVE_FRIENDS', 620054, u'Дневник: работа выполнена мастером успешно, эффект: «производство», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером успешно, эффект: «производство», сообщение для соратников', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_DIARY_PERSON_PLACE_PRODUCTION_POSITIVE_ENEMIES', 620055, u'Дневник: работа выполнена мастером успешно, эффект: «производство», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером успешно, эффект: «производство», сообщение для противников', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_DIARY_PERSON_PLACE_PRODUCTION_NEGATIVE_FRIENDS', 620056, u'Дневник: работа выполнена мастером не успешно, эффект: «производство», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером не успешно, эффект: «производство», сообщение для соратников', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_DIARY_PERSON_PLACE_PRODUCTION_NEGATIVE_ENEMIES', 620057, u'Дневник: работа выполнена мастером не успешно, эффект: «производство», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером не успешно, эффект: «производство», сообщение для противников', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_DIARY_PERSON_PLACE_SAFETY_POSITIVE_FRIENDS', 620058, u'Дневник: работа выполнена мастером успешно, эффект: «безопасность», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером успешно, эффект: «безопасность», сообщение для соратников', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_DIARY_PERSON_PLACE_SAFETY_POSITIVE_ENEMIES', 620059, u'Дневник: работа выполнена мастером успешно, эффект: «безопасность», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером успешно, эффект: «безопасность», сообщение для противников', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_DIARY_PERSON_PLACE_SAFETY_NEGATIVE_FRIENDS', 620060, u'Дневник: работа выполнена мастером не успешно, эффект: «безопасность», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером не успешно, эффект: «безопасность», сообщение для соратников', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_DIARY_PERSON_PLACE_SAFETY_NEGATIVE_ENEMIES', 620061, u'Дневник: работа выполнена мастером не успешно, эффект: «безопасность», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером не успешно, эффект: «безопасность», сообщение для противников', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_DIARY_PERSON_PLACE_TRANSPORT_POSITIVE_FRIENDS', 620062, u'Дневник: работа выполнена мастером успешно, эффект: «транспорт», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером успешно, эффект: «транспорт», сообщение для соратников', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_DIARY_PERSON_PLACE_TRANSPORT_POSITIVE_ENEMIES', 620063, u'Дневник: работа выполнена мастером успешно, эффект: «транспорт», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером успешно, эффект: «транспорт», сообщение для противников', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_DIARY_PERSON_PLACE_TRANSPORT_NEGATIVE_FRIENDS', 620064, u'Дневник: работа выполнена мастером не успешно, эффект: «транспорт», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером не успешно, эффект: «транспорт», сообщение для соратников', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_DIARY_PERSON_PLACE_TRANSPORT_NEGATIVE_ENEMIES', 620065, u'Дневник: работа выполнена мастером не успешно, эффект: «транспорт», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером не успешно, эффект: «транспорт», сообщение для противников', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_DIARY_PERSON_PLACE_FREEDOM_POSITIVE_FRIENDS', 620066, u'Дневник: работа выполнена мастером успешно, эффект: «свобода», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером успешно, эффект: «свобода», сообщение для соратников', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_DIARY_PERSON_PLACE_FREEDOM_POSITIVE_ENEMIES', 620067, u'Дневник: работа выполнена мастером успешно, эффект: «свобода», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером успешно, эффект: «свобода», сообщение для противников', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_DIARY_PERSON_PLACE_FREEDOM_NEGATIVE_FRIENDS', 620068, u'Дневник: работа выполнена мастером не успешно, эффект: «свобода», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером не успешно, эффект: «свобода», сообщение для соратников', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_DIARY_PERSON_PLACE_FREEDOM_NEGATIVE_ENEMIES', 620069, u'Дневник: работа выполнена мастером не успешно, эффект: «свобода», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером не успешно, эффект: «свобода», сообщение для противников', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_DIARY_PERSON_PLACE_STABILITY_POSITIVE_FRIENDS', 620070, u'Дневник: работа выполнена мастером успешно, эффект: «стабильность», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером успешно, эффект: «стабильность», сообщение для соратников', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_DIARY_PERSON_PLACE_STABILITY_POSITIVE_ENEMIES', 620071, u'Дневник: работа выполнена мастером успешно, эффект: «стабильность», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером успешно, эффект: «стабильность», сообщение для противников', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_DIARY_PERSON_PLACE_STABILITY_NEGATIVE_FRIENDS', 620072, u'Дневник: работа выполнена мастером не успешно, эффект: «стабильность», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером не успешно, эффект: «стабильность», сообщение для соратников', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_DIARY_PERSON_PLACE_STABILITY_NEGATIVE_ENEMIES', 620073, u'Дневник: работа выполнена мастером не успешно, эффект: «стабильность», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером не успешно, эффект: «стабильность», сообщение для противников', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_DIARY_PERSON_HERO_MONEY_POSITIVE_FRIENDS', 620074, u'Дневник: работа выполнена мастером успешно, эффект: «золото ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером успешно, эффект: «золото ближнему кругу», сообщение для соратников', [V.HERO, V.PLACE, V.PERSON, V.COINS], u'hero#N +coins#G'),
    (u'JOB_DIARY_PERSON_HERO_MONEY_POSITIVE_ENEMIES', 620075, u'Дневник: работа выполнена мастером успешно, эффект: «золото ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером успешно, эффект: «золото ближнему кругу», сообщение для противников', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_DIARY_PERSON_HERO_MONEY_NEGATIVE_FRIENDS', 620076, u'Дневник: работа выполнена мастером не успешно, эффект: «золото ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером не успешно, эффект: «золото ближнему кругу», сообщение для соратников', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_DIARY_PERSON_HERO_MONEY_NEGATIVE_ENEMIES', 620077, u'Дневник: работа выполнена мастером не успешно, эффект: «золото ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером не успешно, эффект: «золото ближнему кругу», сообщение для противников', [V.HERO, V.PLACE, V.PERSON, V.COINS], u'hero#N +coins#G'),
    (u'JOB_DIARY_PERSON_HERO_ARTIFACT_POSITIVE_FRIENDS', 620078, u'Дневник: работа выполнена мастером успешно, эффект: «артефакт ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером успешно, эффект: «артефакт ближнему кругу», сообщение для соратников', [V.HERO, V.PLACE, V.PERSON, V.ARTIFACT], None),
    (u'JOB_DIARY_PERSON_HERO_ARTIFACT_POSITIVE_ENEMIES', 620079, u'Дневник: работа выполнена мастером успешно, эффект: «артефакт ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером успешно, эффект: «артефакт ближнему кругу», сообщение для противников', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_DIARY_PERSON_HERO_ARTIFACT_NEGATIVE_FRIENDS', 620080, u'Дневник: работа выполнена мастером не успешно, эффект: «артефакт ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером не успешно, эффект: «артефакт ближнему кругу», сообщение для соратников', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_DIARY_PERSON_HERO_ARTIFACT_NEGATIVE_ENEMIES', 620081, u'Дневник: работа выполнена мастером не успешно, эффект: «артефакт ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером не успешно, эффект: «артефакт ближнему кругу», сообщение для противников', [V.HERO, V.PLACE, V.PERSON, V.ARTIFACT], None),
    (u'JOB_DIARY_PERSON_HERO_EXPERIENCE_POSITIVE_FRIENDS', 620082, u'Дневник: работа выполнена мастером успешно, эффект: «опыт ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером успешно, эффект: «опыт ближнему кругу», сообщение для соратников', [V.HERO, V.PLACE, V.PERSON, V.EXPERIENCE], u'hero#N +experience#EXP'),
    (u'JOB_DIARY_PERSON_HERO_EXPERIENCE_POSITIVE_ENEMIES', 620083, u'Дневник: работа выполнена мастером успешно, эффект: «опыт ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером успешно, эффект: «опыт ближнему кругу», сообщение для противников', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_DIARY_PERSON_HERO_EXPERIENCE_NEGATIVE_FRIENDS', 620084, u'Дневник: работа выполнена мастером не успешно, эффект: «опыт ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером не успешно, эффект: «опыт ближнему кругу», сообщение для соратников', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_DIARY_PERSON_HERO_EXPERIENCE_NEGATIVE_ENEMIES', 620085, u'Дневник: работа выполнена мастером не успешно, эффект: «опыт ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером не успешно, эффект: «опыт ближнему кругу», сообщение для противников', [V.HERO, V.PLACE, V.PERSON, V.EXPERIENCE], u'hero#N +experience#EXP'),
    (u'JOB_DIARY_PERSON_HERO_ENERGY_POSITIVE_FRIENDS', 620086, u'Дневник: работа выполнена мастером успешно, эффект: «энергию ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером успешно, эффект: «энергию ближнему кругу», сообщение для соратников', [V.HERO, V.PLACE, V.PERSON, V.ENERGY], u'hero#N +energy#EN'),
    (u'JOB_DIARY_PERSON_HERO_ENERGY_POSITIVE_ENEMIES', 620087, u'Дневник: работа выполнена мастером успешно, эффект: «энергию ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером успешно, эффект: «энергию ближнему кругу», сообщение для противников', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_DIARY_PERSON_HERO_ENERGY_NEGATIVE_FRIENDS', 620088, u'Дневник: работа выполнена мастером не успешно, эффект: «энергию ближнему кругу», сообщение для соратников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером не успешно, эффект: «энергию ближнему кругу», сообщение для соратников', [V.HERO, V.PLACE, V.PERSON], None),
    (u'JOB_DIARY_PERSON_HERO_ENERGY_NEGATIVE_ENEMIES', 620089, u'Дневник: работа выполнена мастером не успешно, эффект: «энергию ближнему кругу», сообщение для противников', LEXICON_GROUP.JOBS,
     u'Работа выполнена мастером не успешно, эффект: «энергию ближнему кругу», сообщение для противников', [V.HERO, V.PLACE, V.PERSON, V.ENERGY], u'hero#N +energy#EN') ]


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
