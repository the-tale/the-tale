# coding: utf-8

from the_tale.game.companions.abilities import relations as companions_abilities_relations

from the_tale.game.balance import constants as c

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
    DESCRIPTION = u'Ходоки знают как лучше использовать дорожные особенности спутников.'
    EFFECT_TYPE = companions_abilities_relations.METATYPE.TRAVEL


class COMRADE(_CompanionAbilityModifier):
    NAME = u'Боевой товарищ'
    normalized_name = NAME
    DESCRIPTION = u'Герой обращается со спутником как с боевым товарищем, благодаря чему улучшаются все боевые особенности спутника.'
    EFFECT_TYPE = companions_abilities_relations.METATYPE.BATTLE


class ECONOMIC(_CompanionAbilityModifier):
    NAME = u'Бухгалтер'
    normalized_name = NAME
    DESCRIPTION = u'Герои с бухгалтерской жилкой ответственно подходят не только к своему имуществу, но и к имуществу спутника. Способность улучшают денежные особенности спутника.'
    EFFECT_TYPE = companions_abilities_relations.METATYPE.MONEY


class IMPROVISER(_CompanionAbilityModifier):
    NAME = u'Импровизатор'
    normalized_name = NAME
    DESCRIPTION = u'Герой всегда готов помочь своему спутнику в любых его делах, что усиливает его необычные особенности.'
    EFFECT_TYPE = companions_abilities_relations.METATYPE.OTHER


class THOUGHTFUL(AbilityPrototype):

    TYPE = ABILITY_TYPE.COMPANION
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = u'Заботливый'
    normalized_name = NAME
    DESCRIPTION = u'Окружённый заботой героя, спутник увеличивает своё максимальное здоровье.'

    MULTIPLIER = [1.1, 1.2, 1.3, 1.4, 1.5]

    @property
    def multiplier(self): return self.MULTIPLIER[self.level-1]

    def modify_attribute(self, type_, value): return value * self.multiplier if type_.is_COMPANION_MAX_HEALTH else value


class COHERENCE(AbilityPrototype):

    TYPE = ABILITY_TYPE.COMPANION
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = u'Товарищ'
    normalized_name = NAME
    DESCRIPTION = u'Путешествия со спутником сложны и требуют от героя особых навыков. Умение по-товарищески относиться к спутнику определяет максимальную слаженность спутника. Она увеличивается на 20 за уровень способности. При сбросе навыка зарабатотанная слаженность не теряется, но ограничивается его актуальным значением.'

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

    PROBABILITY = [c.COMPANIONS_HERO_REGEN_ON_HEAL_PER_HEAL * 0.2,
                   c.COMPANIONS_HERO_REGEN_ON_HEAL_PER_HEAL * 0.4,
                   c.COMPANIONS_HERO_REGEN_ON_HEAL_PER_HEAL * 0.6,
                   c.COMPANIONS_HERO_REGEN_ON_HEAL_PER_HEAL * 0.8,
                   c.COMPANIONS_HERO_REGEN_ON_HEAL_PER_HEAL * 1.0]
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
    DESCRIPTION = u'Умение обращаться с ниткой, иголкой и хирургическим ножом позволяет иногда восстановить немного здоровья живому спутнику.'
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_LIVING_HEAL


class MAGE_MECHANICS(_CompanionHealBase):
    NAME = u'Магомеханика'
    normalized_name = NAME
    DESCRIPTION = u'С помощью плоскогубцев, проволоки и толики магии магомеханик иногда может отремонтировать своего магомеханического спутника.'
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_CONSTRUCT_HEAL


class WITCHCRAFT(_CompanionHealBase):
    NAME = u'Ведовство'
    normalized_name = NAME
    DESCRIPTION = u'Герой, сведущий в нетрадиционных областях знаний, иногда может восстановить здоровье особого спутника.'
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
    DESCRIPTION = u'Хороший разговор сближает лучше кровавой стычки, коммуникабельный герой быстрее увеличивает слаженность живого спутника.'
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_LIVING_COHERENCE_SPEED

class SERVICE(_CompanionCoherenceSpeedBase):
    NAME = u'Обслуживание'
    normalized_name = NAME
    DESCRIPTION = u'Каждому магомеханическому спутнику требуется регулярная смазка, или подзарядка кристаллов, или ещё какая-нибудь заумная операция. Чем ответственнее герой относится к обслуживанию своего спутника, тем быстрее растёт его слаженность.'
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_CONSTRUCT_COHERENCE_SPEED

class SACREDNESS(_CompanionCoherenceSpeedBase):
    NAME = u'Сакральность'
    normalized_name = NAME
    DESCRIPTION = u'Особые спутники настолько необычны, что герою приходится учиться думать как его напарник. Если герою удаётся найти схожие струны в душе спутника, то их слаженность начинает расти быстрее.'
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_UNUSUAL_COHERENCE_SPEED


ABILITIES = dict( (ability.get_id(), ability)
                  for ability in globals().values()
                  if isinstance(ability, type) and issubclass(ability, AbilityPrototype) and ability != AbilityPrototype and not ability.__name__.startswith('_'))
