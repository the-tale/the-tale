#coding: utf-8

class ABILITY_TYPE:
    BATTLE = 'battle'


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

    NAME = u''
    NORMALIZED_NAME = u''
    DESCRIPTIN = u''
    
    @property
    def normalized_name(self):  return self.NORMALIZED_NAME
    

    @classmethod
    def get_id(cls): return cls.__name__.lower()

    @classmethod
    def use(self, *argv):
        raise NotImplemented('you should declare use method in child classes')


class Hit(AbilityPrototype):
    
    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITIES_ACTIVATION_TYPE.ACTIVE
    LOGIC_TYPE = ABILITIES_LOGIC_TYPE.WITH_CONTACT
    PRIORITY = 100

    NAME = u'Удар'
    NORMALIZED_NAME = NAME
    DESCRIPTION = u'Каждый уважающий себя герой должен быть в состоянии ударить противника, или пнуть.'

    @classmethod
    def use(cls, messanger, actor, enemy):
        damage = actor.context.modify_initial_damage(actor.get_basic_damage())
        damage = enemy.change_health(-damage)
        messanger.add_message('hero_ability_hit', attacker=actor, defender=enemy, damage=-damage)
    

class MagicMushroom(AbilityPrototype):
    
    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITIES_ACTIVATION_TYPE.ACTIVE
    LOGIC_TYPE = ABILITIES_LOGIC_TYPE.WITHOUT_CONTACT
    PRIORITY = 10

    NAME = u'Волшебный гриб'
    NORMALIZED_NAME = NAME
    DESCRIPTION = u'Находясь в бою, герой может силой своей могучей воли вырастить волшебный гриб, съев который, некоторое время станет наносить увеличеный урон противникам.'

    DAMAGE_FACTORS = [3, 2.5, 2, 1.5]

    @classmethod
    def use(cls, messanger, actor, enemy):
        actor.context.use_ability_magic_mushroom(cls.DAMAGE_FACTORS)
        messanger.add_message('hero_ability_magicmushroom', actor=actor)


class Sidestep(AbilityPrototype):
    
    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITIES_ACTIVATION_TYPE.ACTIVE
    LOGIC_TYPE = ABILITIES_LOGIC_TYPE.WITHOUT_CONTACT
    PRIORITY = 10

    NAME = u'Шаг в сторону'
    NORMALIZED_NAME = NAME
    DESCRIPTION = u'Герой быстро меняет свою позицию, дезариентируя противника из-за чего тот начнёт промахиваться по герою.'

    MISS_PROBABILITIES = [0.8, 0.6, 0.4, 0.2]

    @classmethod
    def use(cls, messanger, actor, enemy):
        enemy.context.use_ability_sidestep(cls.MISS_PROBABILITIES)
        messanger.add_message('hero_ability_sidestep', attacker=actor, defender=enemy)


class RunUpPush(AbilityPrototype):
    
    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITIES_ACTIVATION_TYPE.ACTIVE
    LOGIC_TYPE = ABILITIES_LOGIC_TYPE.WITH_CONTACT
    PRIORITY = 10

    NAME = u'Разбег-толчок'
    NORMALIZED_NAME = NAME
    DESCRIPTION = u'Герой разбегается и наносит урон противнику. Существует вероятность, что противник будет оглушён и пропустит следующую атаку.'

    STUN_LENGTH = 3

    @classmethod
    def use(cls, messanger, actor, enemy):
        damage = actor.context.modify_initial_damage(actor.get_basic_damage())
        damage = enemy.change_health(-damage)
        enemy.context.use_stun(cls.STUN_LENGTH)
        messanger.add_message('hero_ability_runuppush', attacker=actor, defender=enemy, damage=-damage)


class Regeneration(AbilityPrototype):
    
    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITIES_ACTIVATION_TYPE.ACTIVE
    LOGIC_TYPE = ABILITIES_LOGIC_TYPE.WITHOUT_CONTACT
    PRIORITY = 10

    NAME = u'Регенерация'
    NORMALIZED_NAME = NAME
    DESCRIPTION = u'Во время боя герой может восстановить часть своего здоровья'

    RESTORED_PERCENT = 0.4

    @classmethod
    def use(cls, messanger, actor, enemy):
        health_to_regen = actor.max_health * cls.RESTORED_PERCENT
        applied_health = actor.change_health(health_to_regen)
        messanger.add_message('hero_ability_regeneration', actor=actor, health=applied_health)

ABILITIES = dict( (ability.get_id(), ability) 
                  for ability in globals().values() 
                  if isinstance(ability, type) and issubclass(ability, AbilityPrototype) and ability != AbilityPrototype)
