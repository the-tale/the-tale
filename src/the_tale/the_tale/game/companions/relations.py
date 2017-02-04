# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from the_tale.game.balance import constants as c

from the_tale.game.cards import relations as cards_relations


class STATE(DjangoEnum):
    records = ( ('ENABLED', 0, 'в игре'),
                ('DISABLED', 1, 'вне игры'),)

class MODE(DjangoEnum):
    records = ( ('AUTOMATIC', 0, 'автоматический'),
                ('MANUAL', 1, 'ручной'),)

class DEDICATION(DjangoEnum):
    block_multiplier = Column()

    records = ( ('INDECISIVE', 0, 'нерешительный', 1.0 - c.COMPANIONS_BLOCK_MULTIPLIER_COMPANION_DEDICATION_DELTA),
                ('BOLD', 1, 'смелый', 1.0 - c.COMPANIONS_BLOCK_MULTIPLIER_COMPANION_DEDICATION_DELTA / 2),
                ('BRAVE', 2, 'храбрый', 1.0),
                ('VALIANT', 3, 'доблестный', 1.0 + c.COMPANIONS_BLOCK_MULTIPLIER_COMPANION_DEDICATION_DELTA / 2),
                ('HEROIC', 4, 'героический', 1.0 + c.COMPANIONS_BLOCK_MULTIPLIER_COMPANION_DEDICATION_DELTA) )


class RARITY(DjangoEnum):
    card_rarity = Column()

    records = ( ('COMMON', 0, 'обычный спутник', cards_relations.RARITY.COMMON),
                ('UNCOMMON', 1, 'необычный спутник', cards_relations.RARITY.UNCOMMON),
                ('RARE', 2, 'редкий спутник', cards_relations.RARITY.RARE),
                ('EPIC', 3, 'эпический спутник', cards_relations.RARITY.EPIC),
                ('LEGENDARY', 4, 'легендарный спутник', cards_relations.RARITY.LEGENDARY) )


class COMPANION_EXISTENCE(DjangoEnum):
    records = (('HAS', 0, 'есть спутник'),
               ('HAS_NO', 1, 'нет спутника'))
