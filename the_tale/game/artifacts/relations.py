# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from the_tale.game.balance import constants as c
from the_tale.game.balance.power import PowerDistribution


class INDEX_ORDER_TYPE(DjangoEnum):
   records = ( ('BY_LEVEL', 'by_level', u'по уровню'),
               ('BY_NAME', 'by_name', u'по имени') )


class ARTIFACT_TYPE(DjangoEnum):

    records = ( ('USELESS', 0, u'хлам'),
                 ('MAIN_HAND', 1, u'основная рука'),
                 ('OFF_HAND', 2, u'вторая рука'),
                 ('PLATE', 3, u'доспех'),
                 ('AMULET', 4, u'амулет'),
                 ('HELMET', 5, u'шлем'),
                 ('CLOAK', 6, u'плащ'),
                 ('SHOULDERS', 7, u'наплечники'),
                 ('GLOVES', 8, u'перчатки'),
                 ('PANTS', 9, u'штаны'),
                 ('BOOTS', 10, u'обувь'),
                 ('RING', 11, u'кольцо') )



class ARTIFACT_POWER_TYPE(DjangoEnum):
    distribution = Column()

    records = ( ('MOST_MAGICAL', 0, u'магическая', PowerDistribution(0.1, 0.9)),
                ('MAGICAL', 1, u'ближе к магии', PowerDistribution(0.25, 0.75)),
                ('NEUTRAL', 2, u'равновесие', PowerDistribution(0.5, 0.5)),
                ('PHYSICAL', 3, u'ближе к физике', PowerDistribution(0.75, 0.25)),
                ('MOST_PHYSICAL', 4, u'физическая', PowerDistribution(0.9, 0.1)) )


class ARTIFACT_RECORD_STATE(DjangoEnum):
    records = ( ('ENABLED', 0, u'в игре'),
                ('DISABLED', 1, u'вне игры') )


class RARITY(DjangoEnum):
    probability = Column()
    max_integrity = Column()
    preference_rating = Column()
    cost = Column()

    records = ( ('NORMAL', 0, u'обычный артефакт', c.NORMAL_ARTIFACT_PROBABILITY, c.ARTIFACT_MAX_INTEGRITY, 1.0, 1.0),
                ('RARE', 1, u'редкий артефакт', c.RARE_ARTIFACT_PROBABILITY, int(c.ARTIFACT_MAX_INTEGRITY*c.ARTIFACT_RARE_MAX_INTEGRITY_MULTIPLIER), 1.5, 3.0),
                ('EPIC', 2, u'эпический артефакт', c.EPIC_ARTIFACT_PROBABILITY, int(c.ARTIFACT_MAX_INTEGRITY*c.ARTIFACT_EPIC_MAX_INTEGRITY_MULTIPLIER), 2.0, 9.0) )


class ARTIFACT_EFFECT(DjangoEnum):

    records = ( ('PHYSICAL_DAMAGE', 0, u'мощь'),
                ('MAGICAL_DAMAGE', 1, u'колдовство'),
                ('INITIATIVE', 2, u'хорошая реакция'),
                ('HEALTH', 3, u'здоровье'),
                ('EXPERIENCE', 4, u'повышение интуиции'),
                ('POWER', 5, u'хитрость'),
                ('ENERGY', 6, u'астральный сосуд'),
                ('SPEED', 7, u'скороход'),
                ('BAG', 8, u'карманы'),

                ('NO_EFFECT', 666, u'нет эффекта'),

                ('GREAT_PHYSICAL_DAMAGE', 1000, u'небывалая мощь'),
                ('GREAT_MAGICAL_DAMAGE', 1001, u'могучее колдовство'),
                ('GREAT_INITIATIVE', 1002, u'превосходная реакция'),
                ('GREAT_HEALTH', 1003, u'невероятное здоровье'),
                ('GREAT_EXPERIENCE', 1004, u'сверхинтуиция'),
                ('GREAT_POWER', 1005, u'особая хитрость'),
                ('GREAT_ENERGY', 1006, u'большой астральный сосуд'),
                ('GREAT_SPEED', 1007, u'неутомимый скороход'),
                ('GREAT_BAG', 1008, u'большие карманы'),
                ('REST_LENGTH', 1009, u'выносливость'),
                ('RESURRECT_LENGTH', 1010, u'живучесть'),
                ('IDLE_LENGTH', 1011, u'деятельность'),
                ('CONVICTION', 1012, u'убеждение'),
                ('CHARM', 1013, u'очарование'),
                ('SPIRITUAL_CONNECTION', 1014, u'духовная связь'),
                ('PEACE_OF_MIND', 1015, u'душевное равновесие'),
                ('SPECIAL_AURA', 1016, u'особая аура'),
                ('REGENERATION', 1017, u'регенерация'),
                ('LAST_CHANCE', 1018, u'последний шанс'),
                ('ICE', 1019, u'лёд'),
                ('FLAME', 1020, u'пламя'),
                ('POISON', 1021, u'яд'),
                ('VAMPIRE_STRIKE', 1022, u'вампиризм'),
                ('ESPRIT', 1023, u'живость ума'),
                ('TERRIBLE_VIEW', 1024, u'ужасный вид'),
                ('CRITICAL_HIT', 1025, u'точные атаки'),
                ('ASTRAL_BARRIER', 1026, u'астральная преграда'),
                ('CLOUDED_MIND', 1027, u'затуманенный разум'),
                ('LUCK_OF_STRANGER', 1028, u'удача странника'),
                ('LUCK_OF_HERO', 1029, u'удача героя'),
                ('FORTITUDE', 1030, u'крепость духа'),
                ('IDEOLOGICAL', 1031, u'идейность'),
                ('UNBREAKABLE', 1032, u'нерушимость'),
                ('SPEEDUP', 1033, u'ускорение'))
