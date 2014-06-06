# coding: utf-8

from rels import Column
from rels.django import DjangoEnum


from the_tale.game.cards import forms


class CARD_TYPE(DjangoEnum):
    form = Column(unique=False, primary=False, single_type=False)
    description = Column(primary=False)

    records = (('KEEPERS_GOODS', 0, u'Дары Хранителей', forms.PlaceForm,
                u'Создаёт в указанном городе 5000 «даров Хранителей». Город будет постепенно переводить их в продукцию, пока дары не кончатся.'),)
