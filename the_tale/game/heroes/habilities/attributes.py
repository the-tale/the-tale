# coding: utf-8

from game.heroes.habilities.prototypes import AbilityPrototype, ABILITY_TYPE, ABILITY_ACTIVATION_TYPE, ABILITY_AVAILABILITY
from game.game_info import ATTRIBUTES

#######################
# initiative
#######################

class EXTRA_SLOW(AbilityPrototype):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_MONSTERS

    NAME = u'Неповоротливый'
    normalized_name = NAME
    DESCRIPTION = u'У обладателя этой способности наверняка в роду были ленивцы — в бою он движется очень медленно.'

    def modify_attribute(self, type_, value): return value*0.7 if type_ == ATTRIBUTES.INITIATIVE else value


class SLOW(AbilityPrototype):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_MONSTERS

    NAME = u'Медленный'
    normalized_name = NAME
    DESCRIPTION = u'Не всем существам посчастливилось быть быстроногими, некоторых природа обделила и их скорость в бою обычно чуть меньше, чем у противников.'

    def modify_attribute(self, type_, value): return value*0.85 if type_ == ATTRIBUTES.INITIATIVE else value


class FAST(AbilityPrototype):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_ALL

    NAME = u'Быстрый'
    normalized_name = NAME
    DESCRIPTION = u'Обладатель этой способности имеет хорошую реакцию и действует в бою быстрее.'

    def modify_attribute(self, type_, value): return value*1.15 if type_ == ATTRIBUTES.INITIATIVE else value


class EXTRA_FAST(AbilityPrototype):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_MONSTERS

    NAME = u'Быстрее ветра'
    normalized_name = NAME
    DESCRIPTION = u'В столкновении со столь быстрым существом далеко не каждому удаётся устоять под градом стремительных атак.'

    def modify_attribute(self, type_, value): return value*1.3 if type_ == ATTRIBUTES.INITIATIVE else value


#######################
# health
#######################

class EXTRA_THIN(AbilityPrototype):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_MONSTERS

    NAME = u'Кожа да кости'
    normalized_name = NAME
    DESCRIPTION = u'Обладатель способности не может похвастаться хорошим запасом здоровья.'

    def modify_attribute(self, type_, value): return value*0.7 if type_ == ATTRIBUTES.HEALTH else value


class THIN(AbilityPrototype):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_MONSTERS

    NAME = u'Худой'
    normalized_name = NAME
    DESCRIPTION = u'Мир таков, что не все существа обладают крепкими мышцами и хорошим запасом здоровья. Кому-то приходится мириться с уменьшенным количеством HP.'

    def modify_attribute(self, type_, value): return value*0.85 if type_ == ATTRIBUTES.HEALTH else value


class THICK(AbilityPrototype):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_ALL

    NAME = u'Здоровяк'
    normalized_name = NAME
    DESCRIPTION = u'Герои и монстры, которые много кушали в детстве, становятся чуть здоровее остальных.'

    def modify_attribute(self, type_, value): return value*1.15 if type_ == ATTRIBUTES.HEALTH else value


class EXTRA_THICK(AbilityPrototype):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_MONSTERS

    NAME = u'Толстяк'
    normalized_name = NAME
    DESCRIPTION = u'У этого монстра с этой способностью очень, очень много этого здоровья.'

    def modify_attribute(self, type_, value): return value*1.3 if type_ == ATTRIBUTES.HEALTH else value


#######################
# damage
#######################

class EXTRA_WEAK(AbilityPrototype):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_MONSTERS

    NAME = u'Тростинка'
    normalized_name = NAME
    DESCRIPTION = u'Обычные атаки монстра наносят очень мало урона.'

    def modify_attribute(self, type_, value): return value*0.7 if type_ == ATTRIBUTES.DAMAGE else value


class WEAK(AbilityPrototype):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_MONSTERS

    NAME = u'Слабый'
    normalized_name = NAME
    DESCRIPTION = u'Слабые монстры иногда стараются компенсировать небольшой недостаток урона за счёт хитрости, но мало у кого это получается.'

    def modify_attribute(self, type_, value): return value*0.85 if type_ == ATTRIBUTES.DAMAGE else value


class STRONG(AbilityPrototype):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_ALL

    NAME = u'Боец'
    normalized_name = NAME
    DESCRIPTION = u'Удары героев и монстров с этой способностью становятся немного сильнее.'

    def modify_attribute(self, type_, value): return value*1.15 if type_ == ATTRIBUTES.DAMAGE else value


class EXTRA_STRONG(AbilityPrototype):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_MONSTERS

    NAME = u'Громила'
    normalized_name = NAME
    DESCRIPTION = u'Лучше не попадать под удары этого монстра — громила наносит на много больший урон чем другие противники.'

    def modify_attribute(self, type_, value): return value*1.3 if type_ == ATTRIBUTES.DAMAGE else value


ABILITIES = dict( (ability.get_id(), ability)
                  for ability in globals().values()
                  if isinstance(ability, type) and issubclass(ability, AbilityPrototype) and ability != AbilityPrototype)
