#coding: utf-8

from game.balance import formulas as f

class ABILITY_TYPE:
    BATTLE = 1
    NONBATTLE = 2


class ABILITIES_ACTIVATION_TYPE:

    ACTIVE = 'active'
    PASSIVE = 'passive'


class ABILITIES_LOGIC_TYPE:

    WITHOUT_CONTACT = 'without_contact'
    WITH_CONTACT = 'with_contact'


class AbilityPrototype(object):

    TYPE = None
    ACTIVATION_TYPE = None
    LOGIC_TYPE = None
    PRIORITY = None
    AVAILABLE_TO_PLAYERS = True

    NAME = u''
    normalized_name = u''
    DESCRIPTIN = u''

    @classmethod
    def is_battle(cls): return cls.TYPE == ABILITY_TYPE.BATTLE

    @classmethod
    def is_nonbattle(cls): return cls.TYPE == ABILITY_TYPE.NONBATTLE

    @classmethod
    def modify_attribute(cls, name, value): return value

    @classmethod
    def update_context(cls, actor, enemy): pass

    @classmethod
    def update_quest_reward(cls, hero, money): return money

    @classmethod
    def update_buy_price(cls, hero, money): return money

    @classmethod
    def update_sell_price(cls, hero, money): return money

    @classmethod
    def get_id(cls): return cls.__name__.lower()

    @classmethod
    def use(self, *argv):
        raise NotImplemented('you should declare use method in child classes')

    @classmethod
    def on_miss(self, *argv):
        raise NotImplemented('you should declare on_miss method in child classes')


class HIT(AbilityPrototype):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITIES_ACTIVATION_TYPE.ACTIVE
    LOGIC_TYPE = ABILITIES_LOGIC_TYPE.WITH_CONTACT
    PRIORITY = 100

    NAME = u'Удар'
    normalized_name = NAME
    DESCRIPTION = u'Каждый уважающий себя герой должен быть в состоянии ударить противника, или пнуть.'

    @classmethod
    def use(cls, messanger, actor, enemy):
        damage = actor.context.modify_initial_damage(actor.basic_damage)
        enemy.change_health(-damage)
        messanger.add_message('hero_ability_hit', attacker=actor, defender=enemy, damage=damage)

    @classmethod
    def on_miss(cls, messanger, actor, enemy):
        messanger.add_message('hero_ability_hit_miss', attacker=actor, defender=enemy)


class MAGIC_MUSHROOM(AbilityPrototype):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITIES_ACTIVATION_TYPE.ACTIVE
    LOGIC_TYPE = ABILITIES_LOGIC_TYPE.WITHOUT_CONTACT
    PRIORITY = 10

    NAME = u'Волшебный гриб'
    normalized_name = NAME
    DESCRIPTION = u'Находясь в бою, герой может силой своей могучей воли вырастить волшебный гриб, съев который, некоторое время станет наносить увеличеный урон противникам.'

    DAMAGE_FACTORS = [3, 2.5, 2, 1.5]

    @classmethod
    def use(cls, messanger, actor, enemy):
        actor.context.use_ability_magic_mushroom(cls.DAMAGE_FACTORS)
        messanger.add_message('hero_ability_magicmushroom', actor=actor)


class SIDESTEP(AbilityPrototype):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITIES_ACTIVATION_TYPE.ACTIVE
    LOGIC_TYPE = ABILITIES_LOGIC_TYPE.WITHOUT_CONTACT
    PRIORITY = 10

    NAME = u'Шаг в сторону'
    normalized_name = NAME
    DESCRIPTION = u'Герой быстро меняет свою позицию, дезориентируя противника из-за чего тот начинает промахиваться.'

    MISS_PROBABILITIES = [0.8, 0.6, 0.4, 0.2]

    @classmethod
    def use(cls, messanger, actor, enemy):
        enemy.context.use_ability_sidestep(cls.MISS_PROBABILITIES)
        messanger.add_message('hero_ability_sidestep', attacker=actor, defender=enemy)

    @classmethod
    def on_miss(cls, messanger, actor, enemy):
        messanger.add_message('hero_ability__miss', attacker=actor, defender=enemy)


class RUN_UP_PUSH(AbilityPrototype):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITIES_ACTIVATION_TYPE.ACTIVE
    LOGIC_TYPE = ABILITIES_LOGIC_TYPE.WITH_CONTACT
    PRIORITY = 10

    NAME = u'Разбег-толчок'
    normalized_name = NAME
    DESCRIPTION = u'Герой разбегается и наносит урон противнику. Враг будет оглушён и пропустит следующую атаку.'

    STUN_LENGTH = 3

    @classmethod
    def use(cls, messanger, actor, enemy):
        damage = actor.context.modify_initial_damage(actor.basic_damage)
        enemy.change_health(-damage)
        enemy.context.use_stun(cls.STUN_LENGTH)
        messanger.add_message('hero_ability_runuppush', attacker=actor, defender=enemy, damage=damage)

    @classmethod
    def on_miss(cls, messanger, actor, enemy):
        messanger.add_message('hero_ability_runuppush_miss', attacker=actor, defender=enemy)



class REGENERATION(AbilityPrototype):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITIES_ACTIVATION_TYPE.ACTIVE
    LOGIC_TYPE = ABILITIES_LOGIC_TYPE.WITHOUT_CONTACT
    PRIORITY = 10

    NAME = u'Регенерация'
    normalized_name = NAME
    DESCRIPTION = u'Во время боя герой может восстановить часть своего здоровья'

    RESTORED_PERCENT = 0.25

    @classmethod
    def use(cls, messanger, actor, enemy):
        health_to_regen = f.mob_hp_to_lvl(actor.level) * cls.RESTORED_PERCENT # !!!MOB HP, NOT HERO!!!
        applied_health = actor.change_health(health_to_regen)
        messanger.add_message('hero_ability_regeneration', actor=actor, health=applied_health)


class CRITICAL_HIT(AbilityPrototype):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITIES_ACTIVATION_TYPE.PASSIVE

    NAME = u'Критический удар'
    normalized_name = NAME
    DESCRIPTION = u'Удача благосклонна к герою - урон от любого удара может существенно увеличится.'

    CRITICAL_CHANCE = 0.1

    @classmethod
    def update_context(cls, actor, enemy):
        actor.context.use_crit_chance(cls.CRITICAL_CHANCE)


class BERSERK(AbilityPrototype):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITIES_ACTIVATION_TYPE.PASSIVE

    NAME = u'Берсерк'
    normalized_name = NAME
    DESCRIPTION = u'Чем меньше у героя остаётся здоровья, тем сильнее его удары.'

    MAXIMUM_BONUS = 0.2

    @classmethod
    def update_context(cls, actor, enemy):
        actor.context.use_berserk(1 + cls.MAXIMUM_BONUS * float(actor.max_health - actor.health) / actor.max_health)


class NINJA(AbilityPrototype):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITIES_ACTIVATION_TYPE.PASSIVE

    NAME = u'Ниндзя'
    normalized_name = NAME
    DESCRIPTION = u'Ниндзя может уклониться от атаки противника.'

    MISS_PROBABILITY = 0.1

    @classmethod
    def update_context(cls, actor, enemy):
        enemy.context.use_ninja(cls.MISS_PROBABILITY)



ABILITIES = dict( (ability.get_id(), ability)
                  for ability in globals().values()
                  if isinstance(ability, type) and issubclass(ability, AbilityPrototype) and ability != AbilityPrototype)
