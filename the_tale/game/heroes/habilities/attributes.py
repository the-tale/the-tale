# coding: utf-8

from game.heroes.habilities.prototypes import AbilityPrototype, ABILITY_TYPE, ABILITIES_ACTIVATION_TYPE
from game.game_info import ATTRIBUTES

#######################
# initiative
#######################

class EXTRA_SLOW(AbilityPrototype):

    TYPE = ABILITY_TYPE.STATIC
    ACTIVATION_TYPE = ABILITIES_ACTIVATION_TYPE.PASSIVE
    AVAILABLE_TO_PLAYERS = False

    NAME = u'очень медленный'
    NORMALIZED_NAME = NAME
    DESCRIPTIN = u''

    @classmethod
    def modify_attribute(cls, type_, value): return value*0.6 if type_ == ATTRIBUTES.INITIATIVE else value


class SLOW(AbilityPrototype):

    TYPE = ABILITY_TYPE.STATIC
    ACTIVATION_TYPE = ABILITIES_ACTIVATION_TYPE.PASSIVE
    AVAILABLE_TO_PLAYERS = False

    NAME = u'медленный'
    NORMALIZED_NAME = NAME
    DESCRIPTIN = u''

    @classmethod
    def modify_attribute(cls, type_, value): return value*0.8 if type_ == ATTRIBUTES.INITIATIVE else value


class FAST(AbilityPrototype):

    TYPE = ABILITY_TYPE.STATIC
    ACTIVATION_TYPE = ABILITIES_ACTIVATION_TYPE.PASSIVE
    AVAILABLE_TO_PLAYERS = False

    NAME = u'быстрый'
    NORMALIZED_NAME = NAME
    DESCRIPTIN = u'герой выделяется своей скоростью'

    @classmethod
    def modify_attribute(cls, type_, value): return value*1.2 if type_ == ATTRIBUTES.INITIATIVE else value


class EXTRA_FAST(AbilityPrototype):

    TYPE = ABILITY_TYPE.STATIC
    ACTIVATION_TYPE = ABILITIES_ACTIVATION_TYPE.PASSIVE
    AVAILABLE_TO_PLAYERS = False

    NAME = u'очень быстрый'
    NORMALIZED_NAME = NAME
    DESCRIPTIN = u''

    @classmethod
    def modify_attribute(cls, type_, value): return value*1.4 if type_ == ATTRIBUTES.INITIATIVE else value


#######################
# health
#######################

class EXTRA_THIN(AbilityPrototype):

    TYPE = ABILITY_TYPE.STATIC
    ACTIVATION_TYPE = ABILITIES_ACTIVATION_TYPE.PASSIVE
    AVAILABLE_TO_PLAYERS = False

    NAME = u'очень худой'
    NORMALIZED_NAME = NAME
    DESCRIPTIN = u''

    @classmethod
    def modify_attribute(cls, type_, value): return value*0.6 if type_ == ATTRIBUTES.HEALTH else value


class THIN(AbilityPrototype):

    TYPE = ABILITY_TYPE.STATIC
    ACTIVATION_TYPE = ABILITIES_ACTIVATION_TYPE.PASSIVE
    AVAILABLE_TO_PLAYERS = False

    NAME = u'худой'
    NORMALIZED_NAME = NAME
    DESCRIPTIN = u''

    @classmethod
    def modify_attribute(cls, type_, value): return value*0.8 if type_ == ATTRIBUTES.HEALTH else value


class THICK(AbilityPrototype):

    TYPE = ABILITY_TYPE.STATIC
    ACTIVATION_TYPE = ABILITIES_ACTIVATION_TYPE.PASSIVE
    AVAILABLE_TO_PLAYERS = False

    NAME = u'толстый'
    NORMALIZED_NAME = NAME
    DESCRIPTIN = u'герой выделяется своим здоровьем'

    @classmethod
    def modify_attribute(cls, type_, value): return value*1.2 if type_ == ATTRIBUTES.HEALTH else value


class EXTRA_THICK(AbilityPrototype):

    TYPE = ABILITY_TYPE.STATIC
    ACTIVATION_TYPE = ABILITIES_ACTIVATION_TYPE.PASSIVE
    AVAILABLE_TO_PLAYERS = False

    NAME = u'очень толстый'
    NORMALIZED_NAME = NAME
    DESCRIPTIN = u''

    @classmethod
    def modify_attribute(cls, type_, value): return value*1.4 if type_ == ATTRIBUTES.HEALTH else value


#######################
# damage
#######################

class EXTRA_WEAK(AbilityPrototype):

    TYPE = ABILITY_TYPE.STATIC
    ACTIVATION_TYPE = ABILITIES_ACTIVATION_TYPE.PASSIVE
    AVAILABLE_TO_PLAYERS = False

    NAME = u'очень слабый'
    NORMALIZED_NAME = NAME
    DESCRIPTIN = u''

    @classmethod
    def modify_attribute(cls, type_, value): return value*0.6 if type_ == ATTRIBUTES.DAMAGE else value


class WEAK(AbilityPrototype):

    TYPE = ABILITY_TYPE.STATIC
    ACTIVATION_TYPE = ABILITIES_ACTIVATION_TYPE.PASSIVE
    AVAILABLE_TO_PLAYERS = False

    NAME = u'слабый'
    NORMALIZED_NAME = NAME
    DESCRIPTIN = u''

    @classmethod
    def modify_attribute(cls, type_, value): return value*0.8 if type_ == ATTRIBUTES.DAMAGE else value


class STRONG(AbilityPrototype):

    TYPE = ABILITY_TYPE.STATIC
    ACTIVATION_TYPE = ABILITIES_ACTIVATION_TYPE.PASSIVE
    AVAILABLE_TO_PLAYERS = False

    NAME = u'сильный'
    NORMALIZED_NAME = NAME
    DESCRIPTIN = u'герой выделяется своей силой'

    @classmethod
    def modify_attribute(cls, type_, value): return value*1.2 if type_ == ATTRIBUTES.DAMAGE else value


class EXTRA_STRONG(AbilityPrototype):

    TYPE = ABILITY_TYPE.STATIC
    ACTIVATION_TYPE = ABILITIES_ACTIVATION_TYPE.PASSIVE
    AVAILABLE_TO_PLAYERS = False

    NAME = u'очень сильный'
    NORMALIZED_NAME = NAME
    DESCRIPTIN = u''

    @classmethod
    def modify_attribute(cls, type_, value): return value*1.4 if type_ == ATTRIBUTES.DAMAGE else value


ABILITIES = dict( (ability.get_id(), ability)
                  for ability in globals().values()
                  if isinstance(ability, type) and issubclass(ability, AbilityPrototype) and ability != AbilityPrototype)
