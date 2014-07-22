# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from the_tale.game.cards import forms


class RARITY(DjangoEnum):
    probability = Column()

    records = ( ('COMMON', 0, u'обычная', 3**4),
                ('UNCOMMON', 1, u'необычная', 3**3),
                ('RARE', 3, u'редкая', 3**2),
                ('EPIC', 4, u'эпическая', 3**1),
                ('LEGENDARY', 5, u'легендарная', 3**0) )

class CARD_TYPE(DjangoEnum):
    rarity = Column(unique=False)
    form = Column(unique=False, primary=False, single_type=False)
    description = Column(primary=False)

    records = (('KEEPERS_GOODS', 0, u'Дары Хранителей', RARITY.LEGENDARY, forms.PlaceForm,
                u'Создаёт в указанном городе 5000 «даров Хранителей». Город будет постепенно переводить их в продукцию, пока дары не кончатся.'),)
