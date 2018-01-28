
from rels import Column
from rels.django import DjangoEnum

from the_tale.game.balance import constants as c
from the_tale.game.balance.power import PowerDistribution


class INDEX_ORDER_TYPE(DjangoEnum):
   records = (('BY_LEVEL', 'by_level', 'по уровню'),
              ('BY_NAME', 'by_name', 'по имени'))


class ARTIFACT_TYPE(DjangoEnum):

    records = (('USELESS', 0, 'хлам'),
               ('MAIN_HAND', 1, 'основная рука'),
               ('OFF_HAND', 2, 'вторая рука'),
               ('PLATE', 3, 'доспех'),
               ('AMULET', 4, 'амулет'),
               ('HELMET', 5, 'шлем'),
               ('CLOAK', 6, 'плащ'),
               ('SHOULDERS', 7, 'наплечники'),
               ('GLOVES', 8, 'перчатки'),
               ('PANTS', 9, 'штаны'),
               ('BOOTS', 10, 'обувь'),
               ('RING', 11, 'кольцо'))


class ARTIFACT_POWER_TYPE(DjangoEnum):
    distribution = Column()

    records = (('MOST_MAGICAL', 0, 'магическая', PowerDistribution(0.1, 0.9)),
               ('MAGICAL', 1, 'ближе к магии', PowerDistribution(0.25, 0.75)),
               ('NEUTRAL', 2, 'равновесие', PowerDistribution(0.5, 0.5)),
               ('PHYSICAL', 3, 'ближе к физике', PowerDistribution(0.75, 0.25)),
               ('MOST_PHYSICAL', 4, 'физическая', PowerDistribution(0.9, 0.1)))


class ARTIFACT_RECORD_STATE(DjangoEnum):
    records = (('ENABLED', 0, 'в игре'),
               ('DISABLED', 1, 'вне игры'))


class RARITY(DjangoEnum):
    probability = Column()
    max_integrity = Column()
    preference_rating = Column()
    cost = Column()

    records = (('NORMAL', 0, 'обычный артефакт', c.NORMAL_ARTIFACT_PROBABILITY, c.ARTIFACT_MAX_INTEGRITY, 1.0, 1.0),
               ('RARE', 1, 'редкий артефакт', c.RARE_ARTIFACT_PROBABILITY, int(c.ARTIFACT_MAX_INTEGRITY*c.ARTIFACT_RARE_MAX_INTEGRITY_MULTIPLIER), 1.5, 3.0),
               ('EPIC', 2, 'эпический артефакт', c.EPIC_ARTIFACT_PROBABILITY, int(c.ARTIFACT_MAX_INTEGRITY*c.ARTIFACT_EPIC_MAX_INTEGRITY_MULTIPLIER), 2.0, 9.0))


class ARTIFACT_EFFECT(DjangoEnum):

    records = (('PHYSICAL_DAMAGE', 0, 'мощь'),
               ('MAGICAL_DAMAGE', 1, 'колдовство'),
               ('INITIATIVE', 2, 'хорошая реакция'),
               ('HEALTH', 3, 'здоровье'),
               ('EXPERIENCE', 4, 'повышение интуиции'),
               ('POWER', 5, 'хитрость'),
               ('CONCENTRATION', 6, 'концентрация'),
               ('SPEED', 7, 'скороход'),
               ('BAG', 8, 'карманы'),

               ('NO_EFFECT', 666, 'нет эффекта'),

               ('GREAT_PHYSICAL_DAMAGE', 1000, 'небывалая мощь'),
               ('GREAT_MAGICAL_DAMAGE', 1001, 'могучее колдовство'),
               ('GREAT_INITIATIVE', 1002, 'превосходная реакция'),
               ('GREAT_HEALTH', 1003, 'невероятное здоровье'),
               ('GREAT_EXPERIENCE', 1004, 'сверхинтуиция'),
               ('GREAT_POWER', 1005, 'особая хитрость'),
               # ('GREAT_ENERGY', 1006, 'большой астральный сосуд'),
               ('GREAT_SPEED', 1007, 'неутомимый скороход'),
               ('GREAT_BAG', 1008, 'большие карманы'),
               ('REST_LENGTH', 1009, 'выносливость'),
               ('RESURRECT_LENGTH', 1010, 'живучесть'),
               ('IDLE_LENGTH', 1011, 'деятельность'),
               ('CONVICTION', 1012, 'убеждение'),
               ('CHARM', 1013, 'очарование'),
               # ('SPIRITUAL_CONNECTION', 1014, 'духовная связь'),
               ('PEACE_OF_MIND', 1015, 'душевное равновесие'),
               ('SPECIAL_AURA', 1016, 'особая аура'),
               ('REGENERATION', 1017, 'регенерация'),
               ('LAST_CHANCE', 1018, 'последний шанс'),
               ('ICE', 1019, 'лёд'),
               ('FLAME', 1020, 'пламя'),
               ('POISON', 1021, 'яд'),
               ('VAMPIRE_STRIKE', 1022, 'вампиризм'),
               ('ESPRIT', 1023, 'живость ума'),
               ('TERRIBLE_VIEW', 1024, 'ужасный вид'),
               ('CRITICAL_HIT', 1025, 'точные атаки'),
               ('ASTRAL_BARRIER', 1026, 'астральная преграда'),
               ('CLOUDED_MIND', 1027, 'затуманенный разум'),
               ('LUCK_OF_STRANGER', 1028, 'удача странника'),
               ('LUCK_OF_HERO', 1029, 'удача героя'),
               ('FORTITUDE', 1030, 'крепость духа'),
               ('IDEOLOGICAL', 1031, 'идейность'),
               ('UNBREAKABLE', 1032, 'нерушимость'),
               ('SPEEDUP', 1033, 'ускорение'),
               ('RECKLESSNESS', 1034, 'безрассудность'),
               ('CHILD_GIFT', 100001, 'детский подарок'))
