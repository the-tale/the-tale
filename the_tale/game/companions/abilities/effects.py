# coding: utf-8
from rels import Column
from rels.django import DjangoEnum

from the_tale.game import relations as game_relations

from the_tale.game.heroes import relations as heroes_relations

from the_tale.game.companions.abilities import relations


class Base(object):
    TYPE = None

    def __init__(self):
        pass

    @property
    def uid(self):
        return (self.TYPE, None)

    def modify_attribute(self, modifier, value):
        return self._modify_attribute(modifier, value)

    def check_attribute(self, modifier):
        return self._check_attribute(modifier)

    def update_context(self, actor, enemy):
        return self._update_context(actor, enemy)


    def _modify_attribute(self, modifier, value):
        return value

    def _check_attribute(self, modifier):
        return False

    def _update_context(self, actor, enemy):
        pass


class Multiplier(Base):
    MODIFIER = None

    def __init__(self, multiplier):
        super(Multiplier, self).__init__()
        self.multiplier = multiplier

    def _modify_attribute(self, modifier, value):
        if modifier == self.MODIFIER:
            return value *self.multiplier
        return value


class Summand(Base):
    MODIFIER = None

    def __init__(self, summand):
        super(Summand, self).__init__()
        self.summand = summand

    def _modify_attribute(self, modifier, value):
        if modifier == self.MODIFIER:
            return value + self.summand
        return value



class CoherenceSpeed(Multiplier):
    TYPE = relations.EFFECT.COHERENCE_SPEED
    MODIFIER = heroes_relations.MODIFIERS.COHERENCE_EXPERIENCE


class ChangeHabits(Base):
    TYPE = relations.EFFECT.CHANGE_HABITS

    def __init__(self, habit_type, habit_sources, **kwargs):
        super(ChangeHabits, self).__init__(**kwargs)
        self.habit_type = habit_type
        self.habit_sources = frozenset(habit_sources)

    @property
    def uid(self):
        return (self.TYPE, self.habit_type)

    def _modify_attribute(self, modifier, value):
        if modifier.is_HABITS_SOURCES:
            return value | self.habit_sources
        return value


class QuestMoneyReward(Multiplier):
    TYPE = relations.EFFECT.QUEST_MONEY_REWARD
    MODIFIER = heroes_relations.MODIFIERS.QUEST_MONEY_REWARD


class MaxBagSize(Summand):
    TYPE = relations.EFFECT.MAX_BAG_SIZE
    MODIFIER = heroes_relations.MODIFIERS.MAX_BAG_SIZE


class PoliticsPower(Multiplier):
    TYPE = relations.EFFECT.POLITICS_POWER
    MODIFIER = heroes_relations.MODIFIERS.POWER


class MagicDamageBonus(Multiplier):
    TYPE = relations.EFFECT.MAGIC_DAMAGE_BONUS
    MODIFIER = heroes_relations.MODIFIERS.MAGIC_DAMAGE

class PhysicDamageBonus(Multiplier):
    TYPE = relations.EFFECT.PHYSIC_DAMAGE_BONUS
    MODIFIER = heroes_relations.MODIFIERS.PHYSIC_DAMAGE


class ABILITIES(DjangoEnum):
    description = Column()
    only_start = Column(unique=False)
    effect = Column(single_type=False)

    records = (
        (u'OBSTINATE', 0, u'строптивый', u'очень медленный рост слаженности', True, CoherenceSpeed(multiplier=0.70)),
        (u'STUBBORN', 1, u'упрямый', u'медленный рост слаженности', True, CoherenceSpeed(multiplier=0.85)),
        (u'BONA_FIDE', 2, u'добросовестный', u'быстрый рост слаженности', True, CoherenceSpeed(multiplier=1.15)),
        (u'MANAGING', 3, u'исполнительный', u'очень быстрый рост слаженности', True, CoherenceSpeed(multiplier=1.30)),

        (u'AGGRESSIVE', 4, u'агрессивный', u'повышает агрессивность героя', True,
         ChangeHabits(habit_type=game_relations.HABIT_TYPE.PEACEFULNESS, habit_sources=(heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_AGGRESSIVE, ))),
        (u'PEACEFUL', 5, u'миролюбивый', u'понижает агрессивность героя', True,
         ChangeHabits(habit_type=game_relations.HABIT_TYPE.PEACEFULNESS, habit_sources=(heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_PEACEFULL,))),
        (u'RESERVED', 6, u'сдержанный', u'склоняет героя к сдержанности', True,
         ChangeHabits(habit_type=game_relations.HABIT_TYPE.PEACEFULNESS, habit_sources=(heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_PEACEFULL_NEUTRAL_1,
                                                                                        heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_PEACEFULL_NEUTRAL_2))),
        (u'CANNY', 7, u'себе на уме', u'склоняет героя быть себе на уме', True,
         ChangeHabits(habit_type=game_relations.HABIT_TYPE.HONOR, habit_sources=(heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_HONOR_NEUTRAL_1,
                                                                                 heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_HONOR_NEUTRAL_2))),
        (u'HONEST', 8, u'честный', u'повышает честь героя', True,
         ChangeHabits(habit_type=game_relations.HABIT_TYPE.HONOR, habit_sources=(heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_HONORABLE,))),
        (u'SNEAKY', 9, u'подлый', u'понижает честь героя', True,
         ChangeHabits(habit_type=game_relations.HABIT_TYPE.HONOR, habit_sources=(heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_DISHONORABLE,))),

        (u'CHARMING', 10, u'очаровательный', u'симпатичен горожанам. Крупный бонус к денежной награде за квесты', True, QuestMoneyReward(multiplier=2.0)),
        (u'CUTE', 11, u'милый', u'симпатичен горожанам. Небольшой бонус к денежной награде за квесты', True, QuestMoneyReward(multiplier=1.5)),
        (u'FRIGHTFUL', 12, u'страшный', u'пугает горожан своим видом. Маленький штраф к оплате квестов.', True, QuestMoneyReward(multiplier=0.75)),
        (u'TERRIBLE', 13, u'мороз по коже', u'пугает горожан своим видом. Болшой штраф к оплате квестов.', True, QuestMoneyReward(multiplier=0.50)),

        (u'PACK', 14, u'вьючный', u'1 дополнительное место для лута', False, MaxBagSize(summand=1)),
        (u'FREIGHT', 15, u'грузовой', u'2 дополнительных места для лута', False, MaxBagSize(summand=2)),
        (u'DRAFT', 16, u'тягловой', u'3 дополнительных места для лута', False, MaxBagSize(summand=3)),

        (u'KNOWN', 17, u'известный', u'находит более политически важную работу', False, PoliticsPower(multiplier=1.5)),
        (u'CAD', 18, u'хам', u'хамит горожанам. Минус к влиянию заданий', True, PoliticsPower(multiplier=0.75)),

        (u'FIT_OF_ENERGY', 19, u'прилив сил', u'бонус к физическому урону, наносимому героем', False, MagicDamageBonus(multiplier=1.1)),
        (u'PEP', 20, u'бодрость духа', u'бонус к магическому урону, наносимому героем', False, PhysicDamageBonus(multiplier=1.1)),
    )
