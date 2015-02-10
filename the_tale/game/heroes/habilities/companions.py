# coding: utf-8

from the_tale.game.companions.abilities import relations as companions_abilities_relations

from the_tale.game.heroes import relations as heroes_relations

from the_tale.game.heroes.habilities.prototypes import AbilityPrototype
from the_tale.game.heroes.habilities.relations import ABILITY_TYPE, ABILITY_ACTIVATION_TYPE, ABILITY_AVAILABILITY


class _CompanionAbilityModifier(AbilityPrototype):
    TYPE = ABILITY_TYPE.COMPANION
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = None
    normalized_name = None
    DESCRIPTION = None
    EFFECT_TYPE = None

    def modify_attribute(self, type_, value):
        if type_.is_COMPANION_ABILITIES_LEVELS:
            value[self.EFFECT_TYPE] = self.level
        return value



class WALKER(_CompanionAbilityModifier):
    NAME = u'Ходок'
    normalized_name = NAME
    DESCRIPTION = u'усиливает способности спутника, связанные с путешествиям.'
    EFFECT_TYPE = companions_abilities_relations.METATYPE.TRAVEL


class COMRADE(_CompanionAbilityModifier):
    NAME = u'Боевой товарищ'
    normalized_name = NAME
    DESCRIPTION = u'усиливает способности спутиника, связанные с боем.'
    EFFECT_TYPE = companions_abilities_relations.METATYPE.BATTLE


class IMPROVISER(_CompanionAbilityModifier):
    NAME = u'Импровизатор'
    normalized_name = NAME
    DESCRIPTION = u'усиливает способности спутника, не связанные с боем, путешествиями и имуществом.'
    EFFECT_TYPE = companions_abilities_relations.METATYPE.OTHER


class ECONOMIC(_CompanionAbilityModifier):
    NAME = u'Бережливый'
    normalized_name = NAME
    DESCRIPTION = u'усиливает способности спутника, связанные с деньгами и прочей добычей.'
    EFFECT_TYPE = companions_abilities_relations.METATYPE.MONEY


class THOUGHTFUL(AbilityPrototype):

    TYPE = ABILITY_TYPE.COMPANION
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = u'Заботливый'
    normalized_name = NAME
    DESCRIPTION = u'герой заботится о своём спутнике, увеличивая максимальную живучесть.'

    MULTIPLIER = [1.1, 1.2, 1.3, 1.4, 1.5]

    @property
    def multiplier(self): return self.MULTIPLIER[self.level-1]

    def modify_attribute(self, type_, value): return value * self.multiplier if type_.is_COMPANION_MAX_HEALTH else value


class COHERENCE(AbilityPrototype):

    TYPE = ABILITY_TYPE.COMPANION
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = u'Слаженность'
    normalized_name = NAME
    DESCRIPTION = u'Слаженность — определяет максимальный уровень слаженности, все герои начинает с этой способностью 1-ого уровня. (указать уровни для каждого уровн)'

    COHERENCE = [20, 40, 60, 80, 100]

    @property
    def coherence(self): return self.COHERENCE[self.level-1]

    def modify_attribute(self, type_, value): return value + self.coherence if type_.is_COMPANION_MAX_COHERENCE else value



class _CompanionHealBase(AbilityPrototype):
    TYPE = ABILITY_TYPE.COMPANION
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = None
    normalized_name = None
    DESCRIPTION = None

    PROBABILITY = [0.01, 0.02, 0.03, 0.04, 0.05]
    MODIFIER = None

    @property
    def probability(self): return self.PROBABILITY[self.level-1]

    def modify_attribute(self, type_, value):
        if type_ == self.MODIFIER:
            value += self.probability
        return value



class HEALING(_CompanionHealBase):
    NAME = u'Врачевание'
    normalized_name = NAME
    DESCRIPTION = u'герой иногда лечит «живых» спутников.'
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_LIVING_HEAL


class MAGE_MECHANICS(_CompanionHealBase):
    NAME = u'Магомеханика'
    normalized_name = NAME
    DESCRIPTION = u'герой иногда лечит «механических» спутников'
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_CONSTRUCT_HEAL


class WITCHCRAFT(_CompanionHealBase):
    NAME = u'Ведовство'
    normalized_name = NAME
    DESCRIPTION = u'герой иногда лечит «необычных» спутников'
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_UNUSUAL_HEAL



class _CompanionCoherenceSpeedBase(AbilityPrototype):
    TYPE = ABILITY_TYPE.COMPANION
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = None
    normalized_name = None
    DESCRIPTION = None

    SPEED = [1.2, 1.4, 1.6, 1.8, 2.0]
    MODIFIER = None

    @property
    def speed(self): return self.SPEED[self.level-1]

    def modify_attribute(self, type_, value):
        if type_ == self.MODIFIER:
            value *= self.speed
        return value


class SOCIABILITY(_CompanionCoherenceSpeedBase):
    NAME = u'Коммуникабельность'
    normalized_name = NAME
    DESCRIPTION = u'слаженность живых спутников героя растёт быстрее'
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_LIVING_COHERENCE_SPEED

class SERVICE(_CompanionCoherenceSpeedBase):
    NAME = u'Обслуживание'
    normalized_name = NAME
    DESCRIPTION = u'слаженность спутников-конструктов героя растёт быстрее'
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_CONSTRUCT_COHERENCE_SPEED

class SACREDNESS(_CompanionCoherenceSpeedBase):
    NAME = u'Сакральность'
    normalized_name = NAME
    DESCRIPTION = u'слаженность необычных спутников героя растёт быстрее'
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_UNUSUAL_COHERENCE_SPEED


ABILITIES = dict( (ability.get_id(), ability)
                  for ability in globals().values()
                  if isinstance(ability, type) and issubclass(ability, AbilityPrototype) and ability != AbilityPrototype and not ability.__name__.startswith('_'))
