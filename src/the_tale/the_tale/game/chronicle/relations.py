# coding: utf-8

from rels import Column
from rels.django import DjangoEnum


class RECORD_TYPE(DjangoEnum):
    deprecated = Column(unique=False)

    records = ( ('PLACE_CHANGE_NAME_BILL_STARTED', 0, 'название города: предложен закон об изменении', True),
                ('PLACE_CHANGE_NAME_BILL_SUCCESSED', 1, 'название города: принят закон об изменении', False),
                ('PLACE_CHANGE_NAME_BILL_FAILED', 2, 'название города: отклонён закон об изменении', True),

                ('PLACE_CHANGE_DESCRIPTION_BILL_STARTED', 3, 'описание города: предложен закон об изменении', True),
                ('PLACE_CHANGE_DESCRIPTION_BILL_SUCCESSED', 4, 'описание города: принят закон об изменении', False),
                ('PLACE_CHANGE_DESCRIPTION_BILL_FAILED', 5, 'описание города: отклонён закон об изменении', True),

                ('PLACE_CHANGE_MODIFIER_BILL_STARTED', 6, 'специализация города: предложен закон об изменении', True),
                ('PLACE_CHANGE_MODIFIER_BILL_SUCCESSED', 7, 'специализация города: принят закон об изменении', False),
                ('PLACE_CHANGE_MODIFIER_BILL_FAILED', 8, 'специализация города: отклонён закон об изменении', True),

                ('PLACE_LOSED_MODIFIER', 9, 'специализация города: утеряна из-за недостатка развития', True),

                ('PERSON_REMOVE_BILL_STARTED', 10, 'житель: предложен закон об изгнании', True),
                ('PERSON_REMOVE_BILL_SUCCESSED', 11, 'житель: принят закон об изгнании', True),
                ('PERSON_REMOVE_BILL_FAILED', 12, 'житель: отклонён закон об изгнании', True),
                ('PERSON_LEFT_PLACE', 13, 'житель: покину место из-за потери влияния', True),

                ('PERSON_ARRIVED_TO_PLACE', 14, 'житель: приехал в город', True),

                ('PLACE_CHANGE_RACE', 15, 'раса города: изменение основной расы', False),

                ('BUILDING_CREATE_BILL_STARTED', 16, 'строение: предложен закон о возведении ', True),
                ('BUILDING_CREATE_BILL_SUCCESSED', 17, 'строение: принят закон о возведении', False),
                ('BUILDING_CREATE_BILL_FAILED', 18, 'строение: отклонён закон о возведении', True),

                ('BUILDING_DESTROY_BILL_STARTED', 19, 'строение: предложен закон об удалении ', True),
                ('BUILDING_DESTROY_BILL_SUCCESSED', 20, 'строение: принят закон об удалении', False),
                ('BUILDING_DESTROY_BILL_FAILED', 21, 'строение: отклонён закон об удалении', True),

                ('BUILDING_DESTROYED_BY_AMORTIZATION', 22, 'строение: разрушено из-за амортизации', True),

                ('BUILDING_RENAMING_BILL_STARTED', 23, 'строение: предложен закон о переименовании ', True),
                ('BUILDING_RENAMING_BILL_SUCCESSED', 24, 'строение: принят закон о переименовании', False),
                ('BUILDING_RENAMING_BILL_FAILED', 25, 'строение: отклонён закон о переименовании', True),

                ('PLACE_RESOURCE_EXCHANGE_BILL_STARTED', 26, 'обмен ресурсами: предложен закон', True),
                ('PLACE_RESOURCE_EXCHANGE_BILL_SUCCESSED', 27, 'обмен ресурсами: принят закон', False),
                ('PLACE_RESOURCE_EXCHANGE_BILL_FAILED', 28, 'обмен ресурсами: отклонён закон', True),

                ('BILL_DECLINE_BILL_STARTED', 29, 'отмена закона: предложен закон', True),
                ('BILL_DECLINE_BILL_SUCCESSED', 30, 'отмена закона: принят закон', False),
                ('BILL_DECLINE_BILL_FAILED', 31, 'отмена закона: отклонён закон', True),

                ('PLACE_RESOURCE_EXCHANGE_BILL_ENDED', 32, 'обмен ресурсами: действие закона окончено', True),

                ('PLACE_RESOURCE_CONVERSION_BILL_STARTED', 33, 'изменение параметров города: предложен закон', True),
                ('PLACE_RESOURCE_CONVERSION_BILL_SUCCESSED', 34, 'изменение параметров города: принят закон', False),
                ('PLACE_RESOURCE_CONVERSION_BILL_FAILED', 35, 'изменение параметров города: отклонён закон', True),
                ('PLACE_RESOURCE_CONVERSION_BILL_ENDED', 36, 'оизменение параметров города: действие закона окончено', True),

                ('PERSON_CHRONICLE_BILL_SUCCESSED', 37, 'житель: принят закон о занесении записи в летопись', False),
                ('PLACE_CHRONICLE_BILL_SUCCESSED', 38, 'город: принят закон о занесении записи в летопись', False),

                ('PERSON_MOVE_TO_PLACE', 39, 'житель: принят закон о переезде в другой город', False),
                ('PERSON_ADD_SOCIAL_CONNECTION', 40, 'житель: принят закон об установлении социальной связи', False),
                ('PERSON_REMOVE_SOCIAL_CONNECTION', 41, 'житель: принят закон об удалении социальной связи', False)
              )


class ACTOR_ROLE(DjangoEnum):
    records = ( ('BILL', 0, 'закон'),
                ('PLACE', 1, 'город'),
                ('PERSON', 2, 'житель') )


class ACTOR_TYPE(DjangoEnum):
    records = ( ('BILL', 0, 'закон'),
                ('PLACE', 1, 'город'),
                ('PERSON', 2, 'житель') )
