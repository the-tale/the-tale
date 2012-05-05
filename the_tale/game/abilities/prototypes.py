# coding: utf-8
from dext.utils import s11n

from .forms import AbilityForm
from .models import AbilityTask, ABILITY_STATE

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
        self.available_at = None

    @classmethod
    def get_type(cls): return cls.__name__.lower()

    @classmethod
    def need_form(cls):
        return cls.FORM is not None

    def on_cooldown(self, time, angel_id):
        if self.available_at < time.turn_number:
            return False
        if AbilityTaskPrototype.check_if_used(self.get_type(), angel_id):
            return True

    def serialize(self):
        return {'type': self.__class__.__name__.lower(),
                'limit': self.limit,
                'available_at': self.available_at}

    def ui_info(self):
        return {'type': self.__class__.__name__.lower(),
                'limit': self.limit,
                'available_at': self.available_at}

    @staticmethod
    def deserialize(data):
        from .deck import ABILITIES
        obj = ABILITIES[data['type']]()
        obj.limit = data.get('limit', obj.INITIAL_LIMIT)
        obj.available_at = data.get('available_at', 0)
        return obj

    def create_form(self, resource):
        form = self.FORM or AbilityForm

        if resource.request.POST:
            return form(resource.request.POST)

        return form()

    def activate(self, form, time):
        from ..workers.environment import workers_environment

        available_at = time.turn_number + (self.COOLDOWN if self.COOLDOWN else 0)

        task = AbilityTaskPrototype.create(task_type=self.get_type(),
                                           angel_id=form.c.angel_id,
                                           hero_id=form.c.hero_id,
                                           activated_at=time.turn_number,
                                           available_at=available_at,
                                           data=form.data)

        workers_environment.supervisor.cmd_activate_ability(task.id)

        return task

    def use(self, angel, form):
        pass


class AbilityTaskPrototype(object):

    def __init__(self, model):
        self.model = model

    @classmethod
    def get_by_id(cls, task_id):
        return cls(AbilityTask.objects.get(id=task_id))

    @classmethod
    def reset_all(cls):
        AbilityTask.objects.filter(state=ABILITY_STATE.WAITING).update(state=ABILITY_STATE.RESET)

    @classmethod
    def check_if_used(cls, ability_type, angel_id):
        return AbilityTask.objects.filter(type=ability_type,
                                          angel__id=angel_id,
                                          state=ABILITY_STATE.WAITING).exists()

    @property
    def id(self): return self.model.id

    def get_state(self): return self.model.state
    def set_state(self, value): self.model.state = value
    state = property(get_state, set_state)

    @property
    def angel_id(self): return self.model.angel_id

    @property
    def type(self): return self.model.type

    @property
    def hero_id(self): return self.model.hero_id

    def get_activated_at(self): return self.model.activated_at
    def set_activated_at(self, value): self.model.activated_at = value
    activated_at = property(get_activated_at, set_activated_at)

    def get_available_at(self): return self.model.available_at
    def set_available_at(self, value): self.model.available_at = value
    available_at = property(get_available_at, set_available_at)

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = s11n.from_json(self.model.data)
        return self._data

    @classmethod
    def create(cls, task_type, angel_id, hero_id, activated_at, available_at, data):
        model = AbilityTask.objects.create(angel_id=angel_id,
                                           hero_id=hero_id,
                                           type=task_type,
                                           activated_at=activated_at,
                                           available_at=available_at,
                                           data=s11n.to_json(data))
        return cls(model)

    def save(self):
        self.model.data = s11n.to_json(self.data)
        self.model.save()

    def process(self, bundle, turn_number):

        angel = bundle.angels[self.angel_id]

        ability = angel.abilities[self.type]

        energy = angel.get_energy_at_turn(turn_number)

        if energy < ability.COST:
            self.state = ABILITY_STATE.ERROR
            return

        if ability.LIMITED and not ability.limit:
            self.state = ABILITY_STATE.ERROR
            return

        if ability.available_at > turn_number:
            self.state = ABILITY_STATE.ERROR
            return

        if self.hero_id:
            hero = bundle.heroes[self.hero_id]
            result = ability.use(bundle, angel, hero, self.data)
        else:
            result = ability.use(bundle, angel, self.data)

        if not result:
            self.state = ABILITY_STATE.ERROR
            return

        self.state = ABILITY_STATE.PROCESSED
        angel.set_energy_at_turn(turn_number, energy - ability.COST)

        if ability.LIMITED:
            ability.limit -= 1

        ability.available_at = self.available_at
