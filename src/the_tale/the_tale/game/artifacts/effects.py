
import smart_imports

smart_imports.all()


class BaseEffect(object):
    TYPE = NotImplemented
    DESCRIPTION = NotImplemented
    REMOVE_ON_HELP = False

    @classmethod
    def modify_attribute(cls, type_, value):
        return value


class PhysicalDamage(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.PHYSICAL_DAMAGE
    DESCRIPTION = 'Немного увеличивает физический урон'
    MULTIPLIER = 1.02

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_PHYSIC_DAMAGE else value


class MagicalDamage(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.MAGICAL_DAMAGE
    DESCRIPTION = 'Немного увеличивает магический урон'
    MULTIPLIER = 1.02

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_MAGIC_DAMAGE else value


class Initiative(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.INITIATIVE
    DESCRIPTION = 'Немного увеличивает инициативу героя в бою'
    MULTIPLIER = 1.02

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_INITIATIVE else value


class Health(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.HEALTH
    DESCRIPTION = 'Немного увеличивает максимальное здоровье героя'
    MULTIPLIER = 1.02

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_HEALTH else value


class Experience(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.EXPERIENCE
    DESCRIPTION = 'Немного увеличивает получаемый героем опыт'
    MULTIPLIER = 1.02

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_EXPERIENCE else value


class PersonPower(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.POWER
    DESCRIPTION = 'Немного увеличивает влияние героя (бонус к влиянию: 10%)'
    MODIFIER = 0.1

    @classmethod
    def modify_attribute(cls, type_, value):
        return value + cls.MODIFIER if type_.is_POWER else value


class Speed(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.SPEED
    DESCRIPTION = 'Немного увеличивает скорость движения героя'
    MODIFIER = 1.02

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MODIFIER if type_.is_SPEED else value


class Bag(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.BAG
    DESCRIPTION = 'Немного увеличивает вместимость рюкзака героя'
    MULTIPLIER = 1

    @classmethod
    def modify_attribute(cls, type_, value):
        return value + cls.MULTIPLIER if type_.is_MAX_BAG_SIZE else value


class GreatPhysicalDamage(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.GREAT_PHYSICAL_DAMAGE
    DESCRIPTION = 'Сильно увеличивает физический урон'
    MULTIPLIER = 1.1

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_PHYSIC_DAMAGE else value


class GreatMagicalDamage(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.GREAT_MAGICAL_DAMAGE
    DESCRIPTION = 'Сильно увеличивает магический урон'
    MULTIPLIER = 1.1

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_MAGIC_DAMAGE else value


class GreatInitiative(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.GREAT_INITIATIVE
    DESCRIPTION = 'Сильно увеличивает инициативу героя в бою'
    MULTIPLIER = 1.1

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_INITIATIVE else value


class GreatHealth(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.GREAT_HEALTH
    DESCRIPTION = 'Сильно увеличивает максимальное здоровье героя'
    MULTIPLIER = 1.1

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_HEALTH else value


class GreatExperience(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.GREAT_EXPERIENCE
    DESCRIPTION = 'Сильно увеличивает получаемый героем опыт'
    MULTIPLIER = 1.1

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_EXPERIENCE else value


class GreatPersonPower(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.GREAT_POWER
    DESCRIPTION = 'Сильно увеличивает влияние героя  (бонус к влиянию: 50%)'
    MODIFIER = 0.5

    @classmethod
    def modify_attribute(cls, type_, value):
        return value + cls.MODIFIER if type_.is_POWER else value


class GreatSpeed(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.GREAT_SPEED
    DESCRIPTION = 'Сильно увеличивает скорость движения героя'
    MODIFIER = 1.1

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MODIFIER if type_.is_SPEED else value


class GreatBag(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.GREAT_BAG
    DESCRIPTION = 'Сильно увеличивает вместимость рюкзака героя'
    MULTIPLIER = 3

    @classmethod
    def modify_attribute(cls, type_, value):
        return value + cls.MULTIPLIER if type_.is_MAX_BAG_SIZE else value


class RestLength(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.REST_LENGTH
    DESCRIPTION = 'Герой быстрее восстанавливает здоровье во время отдыха'
    MULTIPLIER = 0.5

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_REST_LENGTH else value


class ResurrectLength(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.RESURRECT_LENGTH
    DESCRIPTION = 'Герой быстрее восстаёт из мёртвых'
    MULTIPLIER = 0.75

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_RESURRECT_LENGTH else value


class IDLELength(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.IDLE_LENGTH
    DESCRIPTION = 'Герой меньше бездельничает'
    MULTIPLIER = 0.75

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_IDLE_LENGTH else value


class Conviction(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.CONVICTION
    DESCRIPTION = 'Уменьшение всех трат'
    BONUS = heroes_abilities_nonbattle.HUCKSTER.BUY_BONUS[-1] / 2

    @classmethod
    def modify_attribute(cls, type_, value):
        return value + cls.BONUS if type_.is_BUY_PRICE else value


class Charm(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.CHARM
    DESCRIPTION = 'Увеличение цены продажи предметов'
    BONUS = heroes_abilities_nonbattle.HUCKSTER._sell_bonus(5) / 2

    @classmethod
    def modify_attribute(cls, type_, value):
        return value + cls.BONUS if type_.is_SELL_PRICE else value


class DoubleEnergy(BaseEffect):
    MULTIPLIER = NotImplemented

    @classmethod
    def modify_attribute(cls, type_, value):
        return value + cls.MULTIPLIER if type_.is_DOUBLE_ENERGY_REGENERATION else value


class PeaceOfMind(DoubleEnergy):
    TYPE = relations.ARTIFACT_EFFECT.PEACE_OF_MIND
    DESCRIPTION = 'Хранитель иногда получает в два раза больше энергии от героя'
    MULTIPLIER = 0.2


class Concentration(DoubleEnergy):
    TYPE = relations.ARTIFACT_EFFECT.CONCENTRATION
    DESCRIPTION = 'Хранитель в редких случаях получает в два раза больше энергии от героя'
    MULTIPLIER = 0.05


class SpecialAura(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.SPECIAL_AURA
    DESCRIPTION = 'Физическая и магическая сила всех артефактов, получаемых героем, увеличивается на 1'
    MULTIPLIER = power.Power(1, 1)

    @classmethod
    def modify_attribute(cls, type_, value):
        return value + cls.MULTIPLIER if type_.is_BONUS_ARTIFACT_POWER else value


class AdditionalAbilitiesBase(BaseEffect):

    @classmethod
    def modify_attribute(cls, type_, value):
        if type_.is_ADDITIONAL_ABILITIES:
            value.append(cls.ABILITY(level=cls.ABILITY.MAX_LEVEL))
        return value


class LastChance(AdditionalAbilitiesBase):
    TYPE = relations.ARTIFACT_EFFECT.LAST_CHANCE
    DESCRIPTION = 'Герою становится доступна способность «%s» максимального уровня' % heroes_abilities_battle.LAST_CHANCE.NAME
    ABILITY = heroes_abilities_battle.LAST_CHANCE


class Regeneration(AdditionalAbilitiesBase):
    TYPE = relations.ARTIFACT_EFFECT.REGENERATION
    DESCRIPTION = 'Герою становится доступна способность «%s» максимального уровня' % heroes_abilities_battle.REGENERATION.NAME
    ABILITY = heroes_abilities_battle.REGENERATION


class Ice(AdditionalAbilitiesBase):
    TYPE = relations.ARTIFACT_EFFECT.ICE
    DESCRIPTION = 'Герою становится доступна способность «%s» максимального уровня' % heroes_abilities_battle.FREEZING.NAME
    ABILITY = heroes_abilities_battle.FREEZING


class Flame(AdditionalAbilitiesBase):
    TYPE = relations.ARTIFACT_EFFECT.FLAME
    DESCRIPTION = 'Герою становится доступна способность «%s» максимального уровня' % heroes_abilities_battle.FIREBALL.NAME
    ABILITY = heroes_abilities_battle.FIREBALL


class Poison(AdditionalAbilitiesBase):
    TYPE = relations.ARTIFACT_EFFECT.POISON
    DESCRIPTION = 'Герою становится доступна способность «%s» максимального уровня' % heroes_abilities_battle.POISON_CLOUD.NAME
    ABILITY = heroes_abilities_battle.POISON_CLOUD


class VampireStrike(AdditionalAbilitiesBase):
    TYPE = relations.ARTIFACT_EFFECT.VAMPIRE_STRIKE
    DESCRIPTION = 'Герою становится доступна способность «%s» максимального уровня' % heroes_abilities_battle.VAMPIRE_STRIKE.NAME
    ABILITY = heroes_abilities_battle.VAMPIRE_STRIKE


class Speedup(AdditionalAbilitiesBase):
    TYPE = relations.ARTIFACT_EFFECT.SPEEDUP
    DESCRIPTION = 'Герою становится доступна способность «%s» максимального уровня' % heroes_abilities_battle.SPEEDUP.NAME
    ABILITY = heroes_abilities_battle.SPEEDUP


class CriticalHit(AdditionalAbilitiesBase):
    TYPE = relations.ARTIFACT_EFFECT.CRITICAL_HIT
    DESCRIPTION = 'Герою становится доступна способность «%s» максимального уровня' % heroes_abilities_battle.CRITICAL_HIT.NAME
    ABILITY = heroes_abilities_battle.CRITICAL_HIT


class AstralBarrier(AdditionalAbilitiesBase):
    TYPE = relations.ARTIFACT_EFFECT.ASTRAL_BARRIER
    DESCRIPTION = 'Герою становится доступна способность «%s» максимального уровня' % heroes_abilities_modifiers.GARGOYLE.NAME
    ABILITY = heroes_abilities_modifiers.GARGOYLE


class Recklessness(AdditionalAbilitiesBase):
    TYPE = relations.ARTIFACT_EFFECT.RECKLESSNESS
    DESCRIPTION = 'Герою становится доступна способность «%s» максимального уровня' % heroes_abilities_battle.INSANE_STRIKE.NAME
    ABILITY = heroes_abilities_battle.INSANE_STRIKE


class Esprit(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.ESPRIT
    DESCRIPTION = 'Слаженность спутника растёт на 25% быстрее'
    MULTIPLIER = 1.25

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_COHERENCE_EXPERIENCE else value


class TerribleView(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.TERRIBLE_VIEW
    DESCRIPTION = 'Герой выглядит настолько ужасно, что некоторые противники в ужасе убегают, не вступая в бой'
    MULTIPLIER = c.KILL_BEFORE_BATTLE_PROBABILITY  # just to be equal to some similar behavour

    @classmethod
    def modify_attribute(cls, type_, value):
        return value + cls.MULTIPLIER if type_.is_FEAR else value


class CloudedMind(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.CLOUDED_MIND
    DESCRIPTION = 'Разум героя затуманивается и тот начинает вести себя независимо от черт'
    MULTIPLIER = True

    @classmethod
    def modify_attribute(cls, type_, value):
        return any((value, cls.MULTIPLIER)) if type_.is_CLOUDED_MIND else value


class LuckOfStranger(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.LUCK_OF_STRANGER
    DESCRIPTION = 'Увеличивается шанс получения редких артефактов'
    MULTIPLIER = 2

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_RARE else value


class LuckOfHero(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.LUCK_OF_HERO
    DESCRIPTION = 'Увеличивается шанс получения эпических артефактов'
    MULTIPLIER = 2

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_EPIC else value


class Fortitude(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.FORTITUDE
    DESCRIPTION = 'Черты героя уменьшаются медленнее'
    MULTIPLIER = 0.5

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_HABITS_DECREASE else value


class Ideological(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.IDEOLOGICAL
    DESCRIPTION = 'Черты героя растут быстрее'
    MULTIPLIER = 2

    @classmethod
    def modify_attribute(cls, type_, value):
        return value * cls.MULTIPLIER if type_.is_HABITS_INCREASE else value


class Unbreakable(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.UNBREAKABLE
    DESCRIPTION = 'Экипировка героя медленнее ломается'
    MULTIPLIER = 0.25

    @classmethod
    def modify_attribute(cls, type_, value):
        return value + cls.MULTIPLIER if type_.is_SAFE_INTEGRITY else value


class NoEffect(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.NO_EFFECT
    DESCRIPTION = 'нет эффекта'


class ChildGift(BaseEffect):
    TYPE = relations.ARTIFACT_EFFECT.CHILD_GIFT
    DESCRIPTION = 'Это потерянный подарок ребёнка. Помогите герою, когда артефакт лежит в рюкзаке, и подарок вернётся к ребёнку.'
    REMOVE_ON_HELP = True


EFFECTS = {effect.TYPE: effect
           for effect in utils_discovering.discover_classes(globals().values(), BaseEffect)
           if effect.TYPE is not NotImplemented}
