# coding: utf-8

from rels.django_staff import DjangoEnum


class RECORD_TYPE(DjangoEnum):
    _records = (('PLACE_CHANGE_NAME_BILL_STARTED', 0, u'название города: предложен закон об изменении'),
                ('PLACE_CHANGE_NAME_BILL_SUCCESSED', 1, u'название города: принят закон об изменении'),
                ('PLACE_CHANGE_NAME_BILL_FAILED', 2, u'название города: отклонён закон об изменении'),

                ('PLACE_CHANGE_DESCRIPTION_BILL_STARTED', 3, u'описание города: предложен закон об изменении'),
                ('PLACE_CHANGE_DESCRIPTION_BILL_SUCCESSED', 4, u'описание города: принят закон об изменении'),
                ('PLACE_CHANGE_DESCRIPTION_BILL_FAILED', 5, u'описание города: отклонён закон об изменении'),

                ('PLACE_CHANGE_MODIFIER_BILL_STARTED', 6, u'специализация города: предложен закон об изменении'),
                ('PLACE_CHANGE_MODIFIER_BILL_SUCCESSED', 7, u'специализация города: принят закон об изменении'),
                ('PLACE_CHANGE_MODIFIER_BILL_FAILED', 8, u'специализация города: отклонён закон об изменении'),
                ('PLACE_LOSED_MODIFIER', 9, u'специализация города: утеряна из-за недостатка развития'),

                ('PERSON_REMOVE_BILL_STARTED', 10, u'персонаж: предложен закон об изгнании'),
                ('PERSON_REMOVE_BILL_SUCCESSED', 11, u'персонаж: принят закон об изгнании'),
                ('PERSON_REMOVE_BILL_FAILED', 12, u'персонаж: отклонён закон об изгнании'),
                ('PERSON_LEFT_PLACE', 13, u'персонаж: покину место из-за потери влияния'),
                ('PERSON_ARRIVED_TO_PLACE', 14, u'персонаж: приехал в город'),

                ('PLACE_CHANGE_RACE', 15, u'раса города: изменение основной расы'),

                ('BUILDING_CREATE_BILL_STARTED', 16, u'строение: предложен закон о возведении '),
                ('BUILDING_CREATE_BILL_SUCCESSED', 17, u'строение: принят закон о возведении'),
                ('BUILDING_CREATE_BILL_FAILED', 18, u'строение: отклонён закон о возведении'),

                ('BUILDING_DESTROY_BILL_STARTED', 19, u'строение: предложен закон об удалении '),
                ('BUILDING_DESTROY_BILL_SUCCESSED', 20, u'строение: принят закон об удалении'),
                ('BUILDING_DESTROY_BILL_FAILED', 21, u'строение: отклонён закон об удалении'),

                ('BUILDING_DESTROYED_BY_AMORTIZATION', 22, u'строение: разрушено из-за амортизации'),

                ('BUILDING_RENAMING_BILL_STARTED', 23, u'строение: предложен закон о переименовании '),
                ('BUILDING_RENAMING_BILL_SUCCESSED', 24, u'строение: принят закон о переименовании'),
                ('BUILDING_RENAMING_BILL_FAILED', 25, u'строение: отклонён закон о переименовании'),

                ('PLACE_RESOURCE_EXCHANGE_BILL_STARTED', 26, u'обмен ресурсами: предложен закон'),
                ('PLACE_RESOURCE_EXCHANGE_BILL_SUCCESSED', 27, u'обмен ресурсами: принят закон'),
                ('PLACE_RESOURCE_EXCHANGE_BILL_FAILED', 28, u'обмен ресурсами: отклонён закон'),

                ('BILL_DECLINE_BILL_STARTED', 29, u'отмена закона: предложен закон'),
                ('BILL_DECLINE_BILL_SUCCESSED', 30, u'отмена закона: принят закон'),
                ('BILL_DECLINE_BILL_FAILED', 31, u'отмена закона: отклонён закон'),

                ('PLACE_RESOURCE_EXCHANGE_BILL_ENDED', 32, u'обмен ресурсами: действие закона окончено'))


class ACTOR_ROLE(DjangoEnum):

    _records = ( ('BILL', 0, u'закон'),
                 ('PLACE', 1, u'город'),
                 ('PERSON', 2, u'персонаж') )
