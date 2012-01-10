#coding: utf-8

class ABILITY_TYPE:
    BATTLE = 'battle'


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
    

class MagicMashrum(AbilityPrototype):
    
    TYPE = ABILITY_TYPE.BATTLE
    EVENTS = []
    LEVELS = []

    NAME = u'Волшебный гриб'
    
    DESCRIPTION = u'Находясь в бою, герой может силой своей могучей воли вырастить волшебный гриб, съев который, будет наносить увеличеный урон противникам, пока сам не получит повреждения.'


ABILITIES = dict( (ability.get_id(), ability) 
                  for ability in globals().values() 
                  if isinstance(ability, type) and issubclass(ability, AbilityPrototype) and ability != AbilityPrototype)
