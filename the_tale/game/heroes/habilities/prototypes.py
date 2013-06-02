#coding: utf-8

from common.utils.enum import create_enum

ABILITY_TYPE = create_enum('ABILITY_TYPE', (('BATTLE', 0, u'боевая'),
                                            ('NONBATTLE', 1, u'небоевая'),) )

ABILITY_ACTIVATION_TYPE = create_enum('ABILITY_ACTIVATION_TYPE', (('ACTIVE', 0, u'активная'),
                                                                  ('PASSIVE', 1, u'пассивная'),))


ABILITY_LOGIC_TYPE = create_enum('ABILITY_LOGIC_TYPE', (('WITHOUT_CONTACT', 0, u'безконтактная'),
                                                        ('WITH_CONTACT', 1, u'контактная'),))

ABILITY_AVAILABILITY = create_enum('ABILITY_AVAILABILITY', (('FOR_PLAYERS', 0b0001, u'только для игроков'),
                                                            ('FOR_MONSTERS', 0b0010, u'только для монстров'),
                                                            ('FOR_ALL', 0b0011, u'для всех')))

DAMAGE_TYPE = create_enum('DAMAGE_TYPE', (('PHYSICAL', 0b0001, u'физический'),
                                          ('MAGICAL', 0b0010, u'магический'),
                                          ('MIXED', 0b0011, u'смешанный')))


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
    def type(self): return ABILITY_TYPE(self.TYPE)

    @property
    def availability(self): return ABILITY_AVAILABILITY(self.AVAILABILITY)

    @property
    def activation_type(self): return ABILITY_ACTIVATION_TYPE(self.ACTIVATION_TYPE)

    @property
    def damage_type(self):
        if self.DAMAGE_TYPE is None: return None
        return DAMAGE_TYPE(self.DAMAGE_TYPE)

    @property
    def has_max_level(self): return self.level == self.MAX_LEVEL

    @property
    def priority(self): return self.PRIORITY[self.level-1]

    @classmethod
    def get_id(cls): return cls.__name__.lower()

    def modify_attribute(self, name, value): return value

    def update_context(self, actor, enemy): pass

    def update_quest_reward(self, hero, money): return money

    def update_buy_price(self, hero, money): return money

    def update_sell_price(self, hero, money): return money

    def update_items_of_expenditure_priorities(self, hero, priorities): return priorities

    def can_get_artifact_for_quest(self, hero): return False

    def can_buy_better_artifact(self, hero): return False

    def can_be_used(self, actor): return True

    def use(self, *argv):
        raise NotImplementedError('you should declare use method in child classes')

    def on_miss(self, *argv):
        raise NotImplementedError('you should declare on_miss method in child classes')

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.level == other.level)
