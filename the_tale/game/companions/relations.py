# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from the_tale.game.cards import relations as cards_relations


class STATE(DjangoEnum):
   records = ( ('ENABLED', 0, u'в игре'),
               ('DISABLED', 1, u'вне игры'),)


class TYPE(DjangoEnum):
   records = ( ('LIVING', 0, u'живой'),
               ('CONSTRUCT', 1, u'магомеханический'),
               ('UNUSUAL', 2, u'необычный') )


class DEDICATION(DjangoEnum):
   records = ( ('INDECISIVE', 0, u'нерешительный'),
               ('BOLD', 1, u'смелый'),
               ('BRAVE', 2, u'храбрый'),
               ('VALIANT', 3, u'доблестный'),
               ('HEROIC', 4, u'героический') )


class RARITY(DjangoEnum):
    card_rarity = Column()

    records = ( ('COMMON', 0, u'обычная карта', cards_relations.RARITY.COMMON),
                ('UNCOMMON', 1, u'необычная карта', cards_relations.RARITY.UNCOMMON),
                ('RARE', 2, u'редкая карта', cards_relations.RARITY.RARE),
                ('EPIC', 3, u'эпическая карта', cards_relations.RARITY.EPIC),
                ('LEGENDARY', 4, u'легендарная карта', cards_relations.RARITY.LEGENDARY) )
