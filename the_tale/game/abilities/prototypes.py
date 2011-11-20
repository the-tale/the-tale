# coding: utf-8

class AbilityPrototype(object):

    COST = None
    COOLDOWN = None
    LIMITED = False
    INITIAL_LIMIT = 0

    NAME = None
    DESCRIPTION = None
    ARTISTIC = None

    FORM = None
    TEMPLATE = None

    def __init__(self):
        self.limit = self.INITIAL_LIMIT

    @classmethod
    def get_type(cls): return cls.__name__.lower()

    @classmethod
    def need_form(cls):
        return True

    def on_cooldown(self):
        # TODO: implement cooldown processing
        return False

    def serialize(self):
        return {'type': self.__class__.__name__.lower(),
                'limit': self.limit}

    def ui_info(self):
        return {'type': self.__class__.__name__.lower(),
                'limit': self.limit,
                'cooldown_end': 0}

    @staticmethod
    def deserialize(data):
        from .deck import ABILITIES
        obj = ABILITIES[data['type']]()
        obj.limit = data.get('limit', obj.INITIAL_LIMIT)
        return obj

    def create_form(self, resource):
        if resource.request.POST:
            return self.FORM(resource.request.POST)
        
        return self.FORM()

    def activate(self, form):
        from .workers.environment import workers_environment
        workers_environment.supervisor.cmd_activate_ability(self.get_type(), form.c.data)

        return { 'available_after': 0,
                 'limit': max(0, self.limit-1)}
        
    @classmethod
    def process(cls, bundle, form):
        angel = bundle.angels[form['angel_id']]
    
        ability = angel.abilities[cls.get_type()]

        if ability.LIMITED:
            ability.limit -= 1

        ability.use(angel, form)


    def use(self, angel, form):
        pass
