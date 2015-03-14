# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from the_tale.game.balance import constants as c

from the_tale.game.cards import relations as cards_relations


class STATE(DjangoEnum):
    records = ( (u'ENABLED', 0, u'в игре'),
                (u'DISABLED', 1, u'вне игры'),)


class TYPE(DjangoEnum):
    records = ( (u'LIVING', 0, u'живой'),
                (u'CONSTRUCT', 1, u'магомеханический'),
                (u'UNUSUAL', 2, u'особый') )


class MODE(DjangoEnum):
    records = ( (u'AUTOMATIC', 0, u'автоматический'),
                (u'MANUAL', 1, u'ручной'),)

class DEDICATION(DjangoEnum):
    block_multiplier = Column()

    records = ( (u'INDECISIVE', 0, u'нерешительный', 1.0 - c.COMPANIONS_BLOCK_MULTIPLIER_COMPANION_DEDICATION_DELTA),
                (u'BOLD', 1, u'смелый', 1.0 - c.COMPANIONS_BLOCK_MULTIPLIER_COMPANION_DEDICATION_DELTA / 2),
                (u'BRAVE', 2, u'храбрый', 1.0),
                (u'VALIANT', 3, u'доблестный', 1.0 + c.COMPANIONS_BLOCK_MULTIPLIER_COMPANION_DEDICATION_DELTA / 2),
                (u'HEROIC', 4, u'героический', 1.0 + c.COMPANIONS_BLOCK_MULTIPLIER_COMPANION_DEDICATION_DELTA) )


class RARITY(DjangoEnum):
    card_rarity = Column()

    records = ( (u'COMMON', 0, u'обычный спутник', cards_relations.RARITY.COMMON),
                (u'UNCOMMON', 1, u'необычный спутник', cards_relations.RARITY.UNCOMMON),
                (u'RARE', 2, u'редкий спутник', cards_relations.RARITY.RARE),
                (u'EPIC', 3, u'эпический спутник', cards_relations.RARITY.EPIC),
                (u'LEGENDARY', 4, u'легендарный спутник', cards_relations.RARITY.LEGENDARY) )
