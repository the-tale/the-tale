# coding: utf-8

import rels
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


class VOTE_TYPE(DjangoEnum):
    _records = (('REFRAINED', 0, u'воздержался'),
                ('FOR', 1, u'«за»'),
                ('AGAINST', 2, u'«против»'))

class VOTED_TYPE(DjangoEnum):
    vote_type = rels.Column(unique=False, single_type=False)

    _records = (('NO', 'no', u'не голосовал', None),
                ('YES', 'yes', u'проголосовал', None),
                ('FOR', 'for', u'«за»', VOTE_TYPE.FOR),
                ('AGAINST', 'against', u'«против»', VOTE_TYPE.AGAINST),
                ('REFRAINED', 'refrained', u'воздержался', VOTE_TYPE.REFRAINED) )
