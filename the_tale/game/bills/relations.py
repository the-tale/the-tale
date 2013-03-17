# coding: utf-8

from rels.django_staff import DjangoEnum

class BILL_STATE(DjangoEnum):
    _records = ( ('VOTING', 1, u'на голосовании'),
                 ('ACCEPTED', 2, u'принят'),
                 ('REJECTED', 3, u'отклонён'),
                 ('REMOVED', 4, u'удалён'))


class BILL_TYPE(DjangoEnum):
    _records = ( ('PLACE_RENAMING', 0, u'переименование места'),
                 ('PERSON_REMOVE', 1, u'удаление персонажа'),
                 ('PLACE_DESCRIPTION', 2, u'изменить описание места'),
                 ('PLACE_MODIFIER', 3, u'изменить тип места'),
                 ('BUILDING_CREATE', 4, u'возвести постройку'),
                 ('BUILDING_DESTROY', 5, u'разрушить постройку'))


class VOTED_TYPE(DjangoEnum):
    _records = (('NO', 'no', u'воздержался'),
                ('YES', 'yes', u'проголосовал'),
                ('FOR', 'for', u'«за»'),
                ('AGAINST', 'against', u'«против»'))
