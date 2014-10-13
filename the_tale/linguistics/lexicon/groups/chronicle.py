# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [(u'CHRONICLE_BILL_DECLINE_BILL_FAILED', 260000, u'Отмена закона: отклонён закон', LEXICON_GROUP.CHRONICLE,
        u'Отклонён закон об отмене другого закона.',
        [V.DECLINED_BILL, V.BILL]),

        (u'CHRONICLE_BILL_DECLINE_BILL_STARTED', 260001, u'Отмена закона: выдвинут закон', LEXICON_GROUP.CHRONICLE,
        u'Выдвинут закон об отмене действия другого закона.',
        [V.DECLINED_BILL, V.BILL]),

        (u'CHRONICLE_BILL_DECLINE_BILL_SUCCESSED', 260002, u'Отмена закона: принят закон', LEXICON_GROUP.CHRONICLE,
        u'Принят закон об отмене действия другого закона.',
        [V.DECLINED_BILL, V.BILL]),

        (u'CHRONICLE_BUILDING_CREATE_BILL_FAILED', 260003, u'Строение: отклонён закон о возведении', LEXICON_GROUP.CHRONICLE,
        u'Отклонён закон о возведении строения для жителя города.',
        [V.PERSON, V.BILL, V.PLACE]),

        (u'CHRONICLE_BUILDING_CREATE_BILL_STARTED', 260004, u'Строение: выдвинут закон о возведении строения', LEXICON_GROUP.CHRONICLE,
        u'Выдвинут закон о возведении строения для жителя города.',
        [V.PERSON, V.BILL, V.PLACE]),

        (u'CHRONICLE_BUILDING_CREATE_BILL_SUCCESSED', 260005, u'Строение: принят закон о возведении', LEXICON_GROUP.CHRONICLE,
        u'Принят закон о возведении строения для жителя города.',
        [V.PERSON, V.BILL, V.PLACE]),

        (u'CHRONICLE_BUILDING_DESTROY_BILL_FAILED', 260006, u'Строение: отклонён закон о разрушении', LEXICON_GROUP.CHRONICLE,
        u'Отклонён закон о разрушении строения жителя города.',
        [V.PERSON, V.BILL, V.PLACE]),

        (u'CHRONICLE_BUILDING_DESTROY_BILL_STARTED', 260007, u'Строение: выдвинут закон о разрушении строения', LEXICON_GROUP.CHRONICLE,
        u'Выдвинут закон о разрушении строения жителя города.',
        [V.PERSON, V.BILL, V.PLACE]),

        (u'CHRONICLE_BUILDING_DESTROY_BILL_SUCCESSED', 260008, u'Строение: принят закон о разрушении строения', LEXICON_GROUP.CHRONICLE,
        u'Принят закон о разрушении строения жителя города.',
        [V.PERSON, V.BILL, V.PLACE]),

        (u'CHRONICLE_BUILDING_DESTROYED_BY_AMORTIZATION', 260009, u'Строение: разрушилось от старости', LEXICON_GROUP.CHRONICLE,
        u'Строение разрушилось т.к. его никто не ремонтировал.',
        [V.PERSON, V.PLACE]),

        (u'CHRONICLE_BUILDING_RENAMING_BILL_FAILED', 260010, u'Строение: отклонён закон о переименовании', LEXICON_GROUP.CHRONICLE,
        u'Отклонён закон о переименовании строения жителя города.',
        [V.NEW_NAME, V.PERSON, V.BILL, V.PLACE, V.OLD_NAME]),

        (u'CHRONICLE_BUILDING_RENAMING_BILL_STARTED', 260011, u'Строение: выдвинут закон о переименовании строения', LEXICON_GROUP.CHRONICLE,
        u'Выдвинут закон о переименовании строения жителя города.',
        [V.NEW_NAME, V.PERSON, V.BILL, V.PLACE, V.OLD_NAME]),

        (u'CHRONICLE_BUILDING_RENAMING_BILL_SUCCESSED', 260012, u'Строение: принят закон о переименовании', LEXICON_GROUP.CHRONICLE,
        u'Принят закон о переименовании строения жителя города.',
        [V.NEW_NAME, V.PERSON, V.BILL, V.PLACE, V.OLD_NAME]),

        (u'CHRONICLE_PERSON_ARRIVED_TO_PLACE', 260013, u'Член Совета: в совет вошёл новый житель', LEXICON_GROUP.CHRONICLE,
        u'Новый житель вошёл в совет города.',
        [V.PERSON, V.PLACE]),

        (u'CHRONICLE_PERSON_LEFT_PLACE', 260014, u'Член Совета: автоматически покинул Совет', LEXICON_GROUP.CHRONICLE,
        u'Член Совета потерял влияние и оставил свою должность.',
        [V.PERSON, V.PLACE]),

        (u'CHRONICLE_PERSON_REMOVE_BILL_FAILED', 260015, u'Член Совета: отклонён закон об исключении', LEXICON_GROUP.CHRONICLE,
        u'Отклонён закон об исключении жителя из городского Совета (житель остался в Совете).',
        [V.PERSON, V.BILL, V.PLACE]),

        (u'CHRONICLE_PERSON_REMOVE_BILL_STARTED', 260016, u'Член Совета: выдвинут закон об исключении из Совета ', LEXICON_GROUP.CHRONICLE,
        u'Выдвинут закон об исключении жителя из Совета.',
        [V.PERSON, V.BILL, V.PLACE]),

        (u'CHRONICLE_PERSON_REMOVE_BILL_SUCCESSED', 260017, u'Член Совета: принят закон об исключении из Совета', LEXICON_GROUP.CHRONICLE,
        u'Принят закон об исключении жителя из городского Совета (житель покинул Совет).',
        [V.PERSON, V.BILL, V.PLACE]),

        (u'CHRONICLE_PLACE_CHANGE_DESCRIPTION_BILL_FAILED', 260018, u'Описание города: отлонён закон об изменении', LEXICON_GROUP.CHRONICLE,
        u'Отклонён закон об изменении описания города (осталось прежнее описание).',
        [V.BILL, V.PLACE]),

        (u'CHRONICLE_PLACE_CHANGE_DESCRIPTION_BILL_STARTED', 260019, u'Описание города: выдвинут закон об изменении', LEXICON_GROUP.CHRONICLE,
        u'Выдвинут закон об изменении описания города.',
        [V.BILL, V.PLACE]),

        (u'CHRONICLE_PLACE_CHANGE_DESCRIPTION_BILL_SUCCESSED', 260020, u'Описание города: принят закон об изменении', LEXICON_GROUP.CHRONICLE,
        u'Принят закон об изменении описания города (описание изменено).',
        [V.BILL, V.PLACE]),

        (u'CHRONICLE_PLACE_CHANGE_MODIFIER_BILL_FAILED_WITH_OLD_MODIFIER', 260021, u'Специализация города: отклонён закон об изменении', LEXICON_GROUP.CHRONICLE,
        u'Отклонён закон об изменении специализации города (осталась прежняя специализация).',
        [V.NEW_MODIFIER, V.BILL, V.PLACE, V.OLD_MODIFIER]),

        (u'CHRONICLE_PLACE_CHANGE_MODIFIER_BILL_FAILED_WITHOUT_OLD_MODIFIER', 260022, u'Специализация города: отклонён закон об установке', LEXICON_GROUP.CHRONICLE,
        u'Отклонён закон об установке специализации города (осталась прежняя специализация).',
        [V.NEW_MODIFIER, V.BILL, V.PLACE]),

        (u'CHRONICLE_PLACE_CHANGE_MODIFIER_BILL_STARTED_WITH_OLD_MODIFIER', 260023, u'Специализация города: выдвинут закон об изменении', LEXICON_GROUP.CHRONICLE,
        u'Выдвинут закон об изменении специализации города',
        [V.NEW_MODIFIER, V.BILL, V.PLACE, V.OLD_MODIFIER]),

        (u'CHRONICLE_PLACE_CHANGE_MODIFIER_BILL_STARTED_WITHOUT_OLD_MODIFIER', 260024, u'Специализация города: выдвинут закон об установке', LEXICON_GROUP.CHRONICLE,
        u'Выдвинут закон об установке специализации города',
        [V.NEW_MODIFIER, V.BILL, V.PLACE]),

        (u'CHRONICLE_PLACE_CHANGE_MODIFIER_BILL_SUCCESSED_WITH_OLD_MODIFIER', 260025, u'Специализациия города: принят закон об изменении', LEXICON_GROUP.CHRONICLE,
        u'Принят закон об изменении специализации города (установлена новая специализация).',
        [V.NEW_MODIFIER, V.BILL, V.PLACE, V.OLD_MODIFIER]),

        (u'CHRONICLE_PLACE_CHANGE_MODIFIER_BILL_SUCCESSED_WITHOUT_OLD_MODIFIER', 260026, u'Специализациия города: принят закон об установке', LEXICON_GROUP.CHRONICLE,
        u'Принят закон об установке специализации города (установлена новая специализация).',
        [V.NEW_MODIFIER, V.BILL, V.PLACE]),

        (u'CHRONICLE_PLACE_CHANGE_NAME_BILL_FAILED', 260027, u'Название города: отклонён закон об изменении', LEXICON_GROUP.CHRONICLE,
        u'Отклонён закон о переименовании города (город остался со старым названием).',
        [V.NEW_NAME, V.BILL, V.OLD_NAME]),

        (u'CHRONICLE_PLACE_CHANGE_NAME_BILL_STARTED', 260028, u'Название города: выдвинут закон об изменении', LEXICON_GROUP.CHRONICLE,
        u'Выдвинут закон о переименовании города.',
        [V.NEW_NAME, V.BILL, V.OLD_NAME]),

        (u'CHRONICLE_PLACE_CHANGE_NAME_BILL_SUCCESSED', 260029, u'Название города: принят закон об изменении', LEXICON_GROUP.CHRONICLE,
        u'Принят закон о переименовании города (город переименован).',
        [V.NEW_NAME, V.BILL, V.OLD_NAME]),

        (u'CHRONICLE_PLACE_CHANGE_RACE', 260030, u'Раса города: изменение', LEXICON_GROUP.CHRONICLE,
        u'Изменилась доминирующая раса города.',
        [V.OLD_RACE, V.NEW_RACE, V.PLACE]),

        (u'CHRONICLE_PLACE_LOSED_MODIFIER', 260031, u'Специализация города: автоматически сброшена', LEXICON_GROUP.CHRONICLE,
        u'Специализация сброшена из-за того, что её развитие стало меньше необходимого барьера',
        [V.PLACE, V.OLD_MODIFIER]),

        (u'CHRONICLE_PLACE_RESOURCE_CONVERSION_BILL_ENDED', 260032, u'Изменение параметров города: отклонён закон об изменении параметров города', LEXICON_GROUP.CHRONICLE,
        u'Отклонён закон закон об изменении параметров города.',
        [V.BILL, V.PLACE, V.CONVERSION]),

        (u'CHRONICLE_PLACE_RESOURCE_CONVERSION_BILL_FAILED', 260033, u'Изменение параметров города: отклонён закон об изменении параметров города', LEXICON_GROUP.CHRONICLE,
        u'Отклонён закон об изменении параметров города.',
        [V.BILL, V.PLACE, V.CONVERSION]),

        (u'CHRONICLE_PLACE_RESOURCE_CONVERSION_BILL_STARTED', 260034, u'Изменение параметров города: выдвинут закон об изменении параметров города', LEXICON_GROUP.CHRONICLE,
        u'Выдвинут закон об изменении параметров города.',
        [V.BILL, V.PLACE, V.CONVERSION]),

        (u'CHRONICLE_PLACE_RESOURCE_CONVERSION_BILL_SUCCESSED', 260035, u'Изменение параметров города: принят закон об изменении параметров города', LEXICON_GROUP.CHRONICLE,
        u'Принят закон об изменении параметров города.',
        [V.BILL, V.PLACE, V.CONVERSION]),

        (u'CHRONICLE_PLACE_RESOURCE_EXCHANGE_BILL_ENDED', 260036, u'Обмен ресурсами: отклонён закон об обмене ресурами', LEXICON_GROUP.CHRONICLE,
        u'Отклонён закон об обмене ресурсами между городами.',
        [V.PLACE_2, V.PLACE_1, V.BILL, V.RESOURCE_1, V.RESOURCE_2]),

        (u'CHRONICLE_PLACE_RESOURCE_EXCHANGE_BILL_FAILED', 260037, u'Обмен ресурсами: отклонён закон об обмене ресурами', LEXICON_GROUP.CHRONICLE,
        u'Отклонён закон об обмене ресурсами между городами.',
        [V.PLACE_2, V.PLACE_1, V.BILL, V.RESOURCE_1, V.RESOURCE_2]),

        (u'CHRONICLE_PLACE_RESOURCE_EXCHANGE_BILL_STARTED', 260038, u'Обмен ресурсами: выдвинут закон об обмене ресурами', LEXICON_GROUP.CHRONICLE,
        u'Выдвинут закон об обмене ресурсами между городами.',
        [V.PLACE_2, V.PLACE_1, V.BILL, V.RESOURCE_1, V.RESOURCE_2]),

        (u'CHRONICLE_PLACE_RESOURCE_EXCHANGE_BILL_SUCCESSED', 260039, u'Обмен ресурсами: принят закон об обмене ресурами', LEXICON_GROUP.CHRONICLE,
        u'Принят закон об обмене ресурсами между городами.',
        [V.PLACE_2, V.PLACE_1, V.BILL, V.RESOURCE_1, V.RESOURCE_2]),

        ]
