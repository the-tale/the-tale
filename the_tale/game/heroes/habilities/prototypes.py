#coding: utf-8

from the_tale.game.heroes.habilities.relations import ABILITY_AVAILABILITY


class AbilityPrototype(object):

    TYPE = None
    ACTIVATION_TYPE = None
    LOGIC_TYPE = None
    PRIORITY = None
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_ALL
    DAMAGE_TYPE = None

    NAME = u''
    normalized_name = u''
    DESCRIPTIN = u''
    MAX_LEVEL = 5

    def __init__(self, level=1):
        self.level = level

    def serialize(self):
        return {'level': self.level}

    @classmethod
    def deserialize(cls, data):
        return cls(level=data['level'])

    @property
    def type(self): return self.TYPE

    @property
    def availability(self): return self.AVAILABILITY

    @property
    def activation_type(self): return self.ACTIVATION_TYPE

    @property
    def damage_type(self): return self.DAMAGE_TYPE

    @property
    def has_max_level(self): return self.level == self.MAX_LEVEL

    @property
    def priority(self): return self.PRIORITY[self.level-1]

    @classmethod
    def get_id(cls): return cls.__name__.lower()

    def modify_attribute(self, name, value): return value # pylint: disable=W0613

    def update_context(self, actor, enemy): pass

    def update_quest_reward(self, hero, money): return money # pylint: disable=W0613

    def update_buy_price(self, hero, money): return money # pylint: disable=W0613

    def update_sell_price(self, hero, money): return money # pylint: disable=W0613

    def update_items_of_expenditure_priorities(self, hero, priorities): return priorities # pylint: disable=W0613

    def can_get_artifact_for_quest(self, hero): return False # pylint: disable=W0613

    def can_buy_better_artifact(self, hero): return False # pylint: disable=W0613

    def can_be_used(self, actor): return True # pylint: disable=W0613

    def use(self, *argv):
        raise NotImplementedError('you should declare use method in child classes')

    def on_miss(self, *argv):
        raise NotImplementedError('you should declare on_miss method in child classes')

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.level == other.level)
