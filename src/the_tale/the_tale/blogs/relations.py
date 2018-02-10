
from rels.django import DjangoEnum


class POST_STATE(DjangoEnum):
    records = (('NOT_MODERATED', 0, 'не проверен'),
               ('ACCEPTED', 1, 'принят'),
               ('DECLINED', 2, 'отклонён'), )
