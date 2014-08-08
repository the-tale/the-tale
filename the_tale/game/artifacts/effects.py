# coding: utf-8

from dext.common.utils import discovering

from the_tale.game.balance import constants as c
from the_tale.game.balance.power import Power

from the_tale.game.heroes.habilities import battle
from the_tale.game.heroes.habilities import modifiers as battle_modifiers

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
    DESCRIPTION = u'Герою становится доступна способность «Последний шанс» максимального уровня'
    ABILITY = battle.LAST_CHANCE

class Regeneration(AdditionalAbilitiesBase):
    TYPE = relations.ARTIFACT_EFFECT.REGENERATION
    DESCRIPTION = u'Герою становится доступна способность «Регенерация» максимального уровня'
    ABILITY = battle.REGENERATION

class Ice(AdditionalAbilitiesBase):
    TYPE = relations.ARTIFACT_EFFECT.ICE
    DESCRIPTION = u'Герою становится доступна способность «Заморозка» максимального уровня'
    ABILITY = battle.FREEZING

class Flame(AdditionalAbilitiesBase):
    TYPE = relations.ARTIFACT_EFFECT.FLAME
    DESCRIPTION = u'Герою становится доступна способность «Огненный шар» максимального уровня'
    ABILITY = battle.FIREBALL

class Poison(AdditionalAbilitiesBase):
    TYPE = relations.ARTIFACT_EFFECT.POISON
    DESCRIPTION = u'Герою становится доступна способность «Ядовитое облако» максимального уровня'
    ABILITY = battle.POISON_CLOUD

class VampireStrike(AdditionalAbilitiesBase):
    TYPE = relations.ARTIFACT_EFFECT.VAMPIRE_STRIKE
    DESCRIPTION = u'Герою становится доступна способность «Удар вампира» максимального уровня'
    ABILITY = battle.VAMPIRE_STRIKE

class Speedup(AdditionalAbilitiesBase):
    TYPE = relations.ARTIFACT_EFFECT.SPEEDUP
    DESCRIPTION = u'Герою становится доступна способность «Ускорение» максимального уровня'
    ABILITY = battle.SPEEDUP

class CriticalHit(AdditionalAbilitiesBase):
    TYPE = relations.ARTIFACT_EFFECT.CRITICAL_HIT
    DESCRIPTION = u'Герою становится доступна способность «Критический удар» максимального уровня'
    ABILITY = battle.CRITICAL_HIT

class AstralBarrier(AdditionalAbilitiesBase):
    TYPE = relations.ARTIFACT_EFFECT.ASTRAL_BARRIER
    DESCRIPTION = u'Герою становится доступна способность «Горгулья» максимального уровня'
    ABILITY = battle_modifiers.GARGOYLE


class Esprit(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.ESPRIT
    DESCRIPTION = u'Задержка смены предпочтений уменьшается до 1 дня'
    MULTIPLIER = int(60*60*24*1)

    @classmethod
    def modify_attribute(cls, type_, value):
        return min(value, cls.MULTIPLIER) if type_.is_PREFERENCES_CHANCE_DELAY else value


class TerribleView(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.TERRIBLE_VIEW
    DESCRIPTION = u'Герой выглядит настолько ужасно, что некоторые противники в ужасе убегают, не вступая в бой'
    MULTIPLIER = c.KILL_BEFORE_BATTLE_PROBABILITY # just to be equal to some similar behavour

    @classmethod
    def modify_attribute(cls, type_, value):
        return value + cls.MULTIPLIER if type_.is_FEAR else value


class CloudedMind(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.CLOUDED_MIND
    DESCRIPTION = u'Разум героя затуманивается и тот начинает вести себя независимо от черт'
    MULTIPLIER = True

    @classmethod
    def modify_attribute(cls, type_, value):
        return any((value, cls.MULTIPLIER)) if type_.is_CLOUDED_MIND else value


class LuckOfStranger(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.LUCK_OF_STRANGER
    DESCRIPTION = u'Увеличивается шанс получения редких артефактов'
    MULTIPLIER = 2

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_RARE else value


class LuckOfHero(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.LUCK_OF_HERO
    DESCRIPTION = u'Увеличивается шанс получения эпических артефактов'
    MULTIPLIER = 2

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_EPIC else value


class Fortitude(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.FORTITUDE
    DESCRIPTION = u'Черты героя уменьшаются медленнее'
    MULTIPLIER = 0.5

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_HABITS_DECREASE else value


class Ideological(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.IDEOLOGICAL
    DESCRIPTION = u'Черты героя растут быстрее'
    MULTIPLIER = 2

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_HABITS_INCREASE else value


class Unbreakable(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.UNBREAKABLE
    DESCRIPTION = u'Экипировка героя медленнее ломается'
    MULTIPLIER = 0.25

    @classmethod
    def modify_attribute(cls, type_, value):
        return value + cls.MULTIPLIER if type_.is_SAFE_INTEGRITY else value

class NoEffect(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.NO_EFFECT
    DESCRIPTION = u'нет эффекта'

    @classmethod
    def modify_attribute(cls, type_, value): return value



EFFECTS = {effect.TYPE: effect
           for effect in discovering.discover_classes(globals().values(), BaseEffect)
           if effect.TYPE is not None}
