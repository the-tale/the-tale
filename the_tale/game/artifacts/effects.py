# coding: utf-8

from the_tale.common.utils import discovering

from the_tale.game.balance.power import Power

from the_tale.game.heroes.habilities import battle

from the_tale.game.artifacts import relations


class BaseEffect(object):
    TYPE = None
    DESCRIPTION = None

    @classmethod
    def modify_attribute(cls, type_, value):
        raise NotImplementedError


class PhysicalDamage(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.PHYSICAL_DAMAGE
    DESCRIPTION = u'Немного увеличивает физический урон'
    MULTIPLIER = 1.02

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_PHYSIC_DAMAGE else value


class MagicalDamage(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.MAGICAL_DAMAGE
    DESCRIPTION = u'Немного увеличивает магический урон'
    MULTIPLIER = 1.02

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_MAGIC_DAMAGE else value


class Initiative(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.INITIATIVE
    DESCRIPTION = u'Немного увеличивает инициативу героя в бою'
    MULTIPLIER = 1.02

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_INITIATIVE else value


class Health(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.HEALTH
    DESCRIPTION = u'Немного увеличивает максимальное здоровье героя'
    MULTIPLIER = 1.02

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_HEALTH else value


class Experience(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.EXPERIENCE
    DESCRIPTION = u'Немного увеличивает получаемый героем опыт'
    MULTIPLIER = 1.02

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_EXPERIENCE else value


class PersonPower(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.POWER
    DESCRIPTION = u'Немного увеличивает влияние героя'
    MODIFIER = 1.02

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MODIFIER if type_.is_POWER else value


class Energy(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.ENERGY
    DESCRIPTION = u'Немного увеличивает максимум энергии Хранителя'
    MODIFIER = 1

    @classmethod
    def modify_attribute(cls, type_, value):
        return value + cls.MODIFIER if type_.is_MAX_ENERGY else value


class Speed(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.SPEED
    DESCRIPTION = u'Немного увеличивает скорость движения героя'
    MODIFIER = 1.02

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MODIFIER if type_.is_SPEED else value


class Bag(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.BAG
    DESCRIPTION = u'Немного увеличивает вместимость рюкзака героя'
    MULTIPLIER = 1

    @classmethod
    def modify_attribute(cls, type_, value):
        return value + cls.MULTIPLIER if type_.is_MAX_BAG_SIZE else value



class GreatPhysicalDamage(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.GREAT_PHYSICAL_DAMAGE
    DESCRIPTION = u'Сильно увеличивает физический урон'
    MULTIPLIER = 1.1

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_PHYSIC_DAMAGE else value


class GreatMagicalDamage(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.GREAT_MAGICAL_DAMAGE
    DESCRIPTION = u'Сильно увеличивает магический урон'
    MULTIPLIER = 1.1

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_MAGIC_DAMAGE else value


class GreatInitiative(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.GREAT_INITIATIVE
    DESCRIPTION = u'Сильно увеличивает инициативу героя в бою'
    MULTIPLIER = 1.1

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_INITIATIVE else value


class GreatHealth(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.GREAT_HEALTH
    DESCRIPTION = u'Сильно увеличивает максимальное здоровье героя'
    MULTIPLIER = 1.1

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_HEALTH else value


class GreatExperience(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.GREAT_EXPERIENCE
    DESCRIPTION = u'Сильно увеличивает получаемый героем опыт'
    MULTIPLIER = 1.1

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_EXPERIENCE else value


class GreatPersonPower(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.GREAT_POWER
    DESCRIPTION = u'Сильно увеличивает влияние героя'
    MODIFIER = 1.1

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MODIFIER if type_.is_POWER else value


class GreatEnergy(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.GREAT_ENERGY
    DESCRIPTION = u'Сильно увеличивает максимум энергии Хранителя'
    MODIFIER = 2

    @classmethod
    def modify_attribute(cls, type_, value):
        return value + cls.MODIFIER if type_.is_MAX_ENERGY else value


class GreatSpeed(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.GREAT_SPEED
    DESCRIPTION = u'Сильно увеличивает скорость движения героя'
    MODIFIER = 1.1

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MODIFIER if type_.is_SPEED else value


class GreatBag(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.GREAT_BAG
    DESCRIPTION = u'Сильно увеличивает вместимость рюкзака героя'
    MULTIPLIER = 3

    @classmethod
    def modify_attribute(cls, type_, value):
        return value + cls.MULTIPLIER if type_.is_MAX_BAG_SIZE else value


class RestLength(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.REST_LENGTH
    DESCRIPTION = u'Герой быстрее восстанавливает здоровье во время отдыха'
    MULTIPLIER = 0.5

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_REST_LENGTH else value


class ResurrectLength(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.RESURRECT_LENGTH
    DESCRIPTION = u'Герой быстрее воскрешается'
    MULTIPLIER = 0.75

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_RESURRECT_LENGTH else value


class IDLELength(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.IDLE_LENGTH
    DESCRIPTION = u'Герой меньше бездельничает'
    MULTIPLIER = 0.75

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_IDLE_LENGTH else value


class Conviction(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.CONVICTION
    DESCRIPTION = u'Уменьшение всех трат'

    MULTIPLIER = 0.75

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_BUY_PRICE else value


class Charm(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.CHARM
    DESCRIPTION = u'Увеличение цены продажи предметов'
    MULTIPLIER = 1.25

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_SELL_PRICE else value


class SpiritualConnection(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.SPIRITUAL_CONNECTION
    DESCRIPTION = u'Все затраты энергии уменьшаются на 1 (но не меньше 1)'
    MULTIPLIER = 1

    @classmethod
    def modify_attribute(cls, type_, value):
        return value + cls.MULTIPLIER if type_.is_ENERGY_DISCOUNT else value

class PeaceOfMind(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.PEACE_OF_MIND
    DESCRIPTION = u'Хранитель иногда получает в два раза больше энергии от героя'
    MULTIPLIER = 0.2

    @classmethod
    def modify_attribute(cls, type_, value):
        return value + cls.MULTIPLIER if type_.is_DOUBLE_ENERGY_REGENERATION else value


class SpecialAura(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.SPECIAL_AURA
    DESCRIPTION = u'Физическая и магическая сила всех артефактов, получаемых героем, увеличивается на 1'
    MULTIPLIER = Power(1, 1)

    @classmethod
    def modify_attribute(cls, type_, value):
        return value + cls.MULTIPLIER if type_.is_BONUS_ARTIFACT_POWER else value


class AdditionalAbilitiesBase(BaseEffect):
    TYPE = None
    DESCRIPTION = None
    ABILITY = None

    @classmethod
    def modify_attribute(cls, type_, value):
        if type_.is_ADDITIONAL_ABILITIES:
            value.append(cls.ABILITY(level=cls.ABILITY.MAX_LEVEL))
        return value


class LastChance(AdditionalAbilitiesBase):
    TYPE = relations.ARTIFACT_EFFECT.LAST_CHANCE
    DESCRIPTION = u'герою становится доступна способность «Последний шанс» максимального уровня'
    ABILITY = battle.LAST_CHANCE

class Regeneration(AdditionalAbilitiesBase):
    TYPE = relations.ARTIFACT_EFFECT.REGENERATION
    DESCRIPTION = u'герою становится доступна способность «Регенерация» максимального уровня'
    ABILITY = battle.REGENERATION

class Ice(AdditionalAbilitiesBase):
    TYPE = relations.ARTIFACT_EFFECT.ICE
    DESCRIPTION = u'герою становится доступна способность «Заморозка» максимального уровня'
    ABILITY = battle.FREEZING

class Flame(AdditionalAbilitiesBase):
    TYPE = relations.ARTIFACT_EFFECT.FLAME
    DESCRIPTION = u'герою становится доступна способность «Огненный шар» максимального уровня'
    ABILITY = battle.FIREBALL

class Poison(AdditionalAbilitiesBase):
    TYPE = relations.ARTIFACT_EFFECT.POISON
    DESCRIPTION = u'герою становится доступна способность «Ядовитое облако» максимального уровня'
    ABILITY = battle.POISON_CLOUD

class VampireStrike(AdditionalAbilitiesBase):
    TYPE = relations.ARTIFACT_EFFECT.VAMPIRE_STRIKE
    DESCRIPTION = u'герою становится доступна способность «Удар вампира» максимального уровня'
    ABILITY = battle.VAMPIRE_STRIKE


EFFECTS = {effect.TYPE: effect
           for effect in discovering.discover_classes(globals().values(), BaseEffect)
           if effect.TYPE is not None}
