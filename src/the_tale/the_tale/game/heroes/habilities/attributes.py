# coding: utf-8

from the_tale.game.heroes.habilities.prototypes import AbilityPrototype
from the_tale.game.heroes.habilities.relations import ABILITY_TYPE, ABILITY_ACTIVATION_TYPE, ABILITY_AVAILABILITY


class AbilityAttributeBase(AbilityPrototype):

    @property
    def modifier(self):
        return self.MODIFIER[self.level-1]


#######################
# initiative
#######################

class EXTRA_SLOW(AbilityAttributeBase):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_MONSTERS

    NAME = 'Неповоротливый'
    normalized_name = NAME
    DESCRIPTION = 'У обладателя этой способности наверняка в роду были ленивцы — в бою он движется очень медленно.'

    MODIFIER = [0.95, 0.90, 0.85, 0.80, 0.75]

    def modify_attribute(self, type_, value): return value*self.modifier if type_.is_INITIATIVE else value


class SLOW(AbilityAttributeBase):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_MONSTERS

    NAME = 'Медленный'
    normalized_name = NAME
    DESCRIPTION = 'Не всем существам посчастливилось быть быстроногими, некоторых природа обделила и их скорость в бою обычно чуть меньше, чем у противников.'

    MODIFIER = [0.975, 0.95, 0.875, 0.90, 0.875]

    def modify_attribute(self, type_, value): return value*self.modifier if type_.is_INITIATIVE else value


class FAST(AbilityAttributeBase):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_ALL

    NAME = 'Быстрый'
    normalized_name = NAME
    DESCRIPTION = 'Обладатель этой способности имеет хорошую реакцию и действует в бою быстрее.'

    MODIFIER = [1.025, 1.05, 1.075, 1.100, 1.125]

    def modify_attribute(self, type_, value): return value*self.modifier if type_.is_INITIATIVE else value


class EXTRA_FAST(AbilityAttributeBase):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_MONSTERS

    NAME = 'Быстрее ветра'
    normalized_name = NAME
    DESCRIPTION = 'В столкновении со столь быстрым существом далеко не каждому удаётся устоять под градом стремительных атак.'

    MODIFIER = [1.05, 1.10, 1.15, 1.20, 1.25]

    def modify_attribute(self, type_, value): return value*self.modifier if type_.is_INITIATIVE else value


#######################
# health
#######################

class EXTRA_THIN(AbilityAttributeBase):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_MONSTERS

    NAME = 'Кожа да кости'
    normalized_name = NAME
    DESCRIPTION = 'Обладатель способности не может похвастаться хорошим запасом здоровья.'

    MODIFIER = [0.95, 0.90, 0.85, 0.80, 0.75]

    def modify_attribute(self, type_, value): return value*self.modifier if type_.is_HEALTH else value


class THIN(AbilityAttributeBase):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_MONSTERS

    NAME = 'Худой'
    normalized_name = NAME
    DESCRIPTION = 'Мир таков, что не все существа обладают крепкими мышцами и хорошим запасом здоровья. Кому-то приходится мириться с уменьшенным количеством HP.'

    MODIFIER = [0.975, 0.95, 0.875, 0.90, 0.875]

    def modify_attribute(self, type_, value): return value*self.modifier if type_.is_HEALTH else value


class THICK(AbilityAttributeBase):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_ALL

    NAME = 'Здоровяк'
    normalized_name = NAME
    DESCRIPTION = 'Герои и монстры, которые много кушали в детстве, становятся немного здоровее остальных.'

    MODIFIER = [1.025, 1.05, 1.075, 1.100, 1.13]

    def modify_attribute(self, type_, value): return value*self.modifier if type_.is_HEALTH else value


class EXTRA_THICK(AbilityAttributeBase):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_MONSTERS

    NAME = 'Толстяк'
    normalized_name = NAME
    DESCRIPTION = 'Монстр может похвастаться отменным здоровьем и очень большой живучестью.'

    MODIFIER = [1.05, 1.10, 1.15, 1.20, 1.25]

    def modify_attribute(self, type_, value): return value*self.modifier if type_.is_HEALTH else value


#######################
# damage
#######################

class EXTRA_WEAK(AbilityAttributeBase):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_MONSTERS

    NAME = 'Тростинка'
    normalized_name = NAME
    DESCRIPTION = 'Обычные атаки монстра наносят очень мало урона.'

    MODIFIER = [0.95, 0.90, 0.85, 0.80, 0.75]

    def modify_attribute(self, type_, value): return value*self.modifier if type_.is_DAMAGE else value


class WEAK(AbilityAttributeBase):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_MONSTERS

    NAME = 'Слабый'
    normalized_name = NAME
    DESCRIPTION = 'Слабые монстры иногда стараются компенсировать небольшой недостаток урона за счёт хитрости, но мало у кого это получается.'

    MODIFIER = [0.975, 0.95, 0.875, 0.90, 0.875]

    def modify_attribute(self, type_, value): return value*self.modifier if type_.is_DAMAGE else value


class STRONG(AbilityAttributeBase):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_ALL

    NAME = 'Боец'
    normalized_name = NAME
    DESCRIPTION = 'Удары закалённых в постоянных сражениях бойцов наносят больше урона противникам.'

    MODIFIER = [1.025, 1.05, 1.075, 1.100, 1.125]

    def modify_attribute(self, type_, value): return value*self.modifier if type_.is_DAMAGE else value


class EXTRA_STRONG(AbilityAttributeBase):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_MONSTERS

    NAME = 'Громила'
    normalized_name = NAME
    DESCRIPTION = 'Лучше не попадать под удары этого монстра — громила наносит намного больший урон чем другие противники.'

    MODIFIER = [1.05, 1.10, 1.15, 1.20, 1.25]

    def modify_attribute(self, type_, value): return value*self.modifier if type_.is_DAMAGE else value


ABILITIES = dict( (ability.get_id(), ability)
                  for ability in globals().values()
                  if isinstance(ability, type) and issubclass(ability, AbilityAttributeBase) and ability != AbilityAttributeBase)
