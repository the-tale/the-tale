#coding: utf-8

class ABILITY_TYPE:
    BATTLE = 'battle'


class ABILITIES_EVENTS:
    
    STRIKE_MOB = 'strike_mob'


class AbilityPrototype(object):

    TYPE = None
    EVENTS = []
    LEVELS = []
    
    NAME = u''
    DESCRIPTIN = u''

    def __init__(self, level):
        self.level = level

    @classmethod
    def get_id(cls): return cls.__name__.lower()

    def use(self, *argv):
        raise NotImplemented('you should declare use method in child classes')

    @property
    def priority(self): return self.LEVELS[self.level][0]
    

class MagicMushroom(AbilityPrototype):
    
    TYPE = ABILITY_TYPE.BATTLE
    EVENTS = [ABILITIES_EVENTS.STRIKE_MOB]
    LEVELS = [(1, 1.5),
              (1, 2.0),
              (1, 2.5),
              (1, 3.0)]

    NAME = u'Волшебный гриб'
    
    DESCRIPTION = u'Находясь в бою, герой может силой своей могучей воли вырастить волшебный гриб, съев который, станет наносить увеличеный урон противникам, пока сам не получит повреждения.'

    def use(self, hero):
        hero.context.ability_magick_mushroom = self.LEVELS[self.level][1]
        hero.create_tmp_log_message('Hero use ability "Magic Mushroom"')


ABILITIES = dict( (ability.get_id(), ability) 
                  for ability in globals().values() 
                  if isinstance(ability, type) and issubclass(ability, AbilityPrototype) and ability != AbilityPrototype)
