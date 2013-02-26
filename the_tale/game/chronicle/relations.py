# coding: utf-8

from rels import DjangoEnum


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

                ('PLACE_CHANGE_RACE', 15, u'раса города: изменение основной расы') )


class ACTOR_ROLE(DjangoEnum):

    _records = ( ('BILL', 0, u'закон'),
                 ('PLACE', 1, u'город'),
                 ('PERSON', 2, u'персонаж') )
