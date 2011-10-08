# coding: utf-8

class ABILITY_TYPE:
    INSTANT = 'instant'

class AbilityPrototype(object):

    TYPE = None
    COST = None
    COOLDOWN = None

    NAME = None
    DESCRIPTION = None
    ARTISTIC = None

    FORM = None
    TEMPLATE = None

    def __init__(self):
        pass

    @classmethod
    def get_type(cls): return cls.__name__.lower()

    def on_cooldown(self):
        # TODO: implement cooldown processing
        return False

    def serrialize(self):
        return {'type': self.__class__.__name__.lower()}

    def ui_info(self):
        return {'type': self.__class__.__name__.lower(),
                'cooldown_end': 0}

    @staticmethod
    def deserrialize(data):
        from .deck import ABILITIES
        obj = ABILITIES[data['type']]()
        return obj

    def create_form(self, resource):
        if resource.request.POST:
            return self.FORM(resource.request.POST)
        
        return self.FORM()

    def activate(self, form):
        from ..tasks import supervisor
        supervisor.cmd_activate_ability(self.get_type(), form.c.data)

        return { 'available_after': 0}
        
    @classmethod
    def process(cls, bundle, form):
        angel = bundle.angels[form['angel_id']]
    
        ability = angel.abilities[cls.get_type()]

        ability.use(angel, form)


    def use(self, angel, form):
        pass
