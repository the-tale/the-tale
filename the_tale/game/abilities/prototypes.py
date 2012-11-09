# coding: utf-8
from dext.utils import s11n

from game.prototypes import TimePrototype

from game.abilities.forms import AbilityForm
from game.abilities.models import AbilitiesData, AbilityTask, ABILITY_TASK_STATE


class AbilityPrototype(object):

    COST = None
    COOLDOWN = None

    NAME = None
    DESCRIPTION = None

    FORM = None
    TEMPLATE = None

    COMMAND_PREFIX = None

    def __init__(self, model):
        self.model = model

    @classmethod
    def get_by_hero_id(cls, hero_id):
        try:
            return cls(AbilitiesData.objects.get(hero_id=hero_id))
        except AbilitiesData.DoesNotExist:
            return None

    @classmethod
    def get_type(cls): return cls.__name__.lower()

    def get_available_at(self): return getattr(self.model, '%s_available_at' % self.COMMAND_PREFIX)
    def set_available_at(self, value): setattr(self.model, '%s_available_at' % self.COMMAND_PREFIX, value)
    available_at = property(get_available_at, set_available_at)

    @classmethod
    def need_form(cls):
        return cls.FORM is not None

    def on_cooldown(self, time, hero_id):
        if self.COOLDOWN is None:
            return False
        if self.available_at < time.turn_number:
            return False
        if AbilityTaskPrototype.check_if_used(self.get_type(), hero_id):
            return True

    def ui_info(self):
        return {'type': self.__class__.__name__.lower(),
                'available_at': self.available_at}

    def create_form(self, resource):
        form = self.FORM or AbilityForm

        if resource.request.POST:
            return form(resource.request.POST)

        return form()

    def activate(self, form, time):
        from ..workers.environment import workers_environment

        available_at = time.turn_number + (self.COOLDOWN if self.COOLDOWN else 0)

        task = AbilityTaskPrototype.create(task_type=self.get_type(),
                                           hero_id=form.c.hero_id,
                                           activated_at=time.turn_number,
                                           available_at=available_at,
                                           data=form.data)

        workers_environment.supervisor.cmd_activate_ability(task.id)

        return task

    def use(self, form):
        pass

    def save(self):
        self.model.save()

    @classmethod
    def create(cls, hero):
        AbilitiesData.objects.create(hero=hero.model)

    def __eq__(self, other):
        return ( self.available_at == other.available_at and
                 self.__class__ == other.__class__ )


class AbilityTaskPrototype(object):

    def __init__(self, model):
        self.model = model

    @classmethod
    def get_by_id(cls, task_id):
        return cls(AbilityTask.objects.get(id=task_id))

    @classmethod
    def reset_all(cls):
        AbilityTask.objects.filter(state=ABILITY_TASK_STATE.WAITING).update(state=ABILITY_TASK_STATE.RESET)

    @classmethod
    def check_if_used(cls, ability_type, hero_id):
        return AbilityTask.objects.filter(type=ability_type,
                                          hero__id=hero_id,
                                          state=ABILITY_TASK_STATE.WAITING).exists()

    @property
    def id(self): return self.model.id

    def get_state(self): return self.model.state
    def set_state(self, value): self.model.state = value
    state = property(get_state, set_state)

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
    def create(cls, task_type, hero_id, activated_at, available_at, data):
        model = AbilityTask.objects.create(hero_id=hero_id,
                                           type=task_type,
                                           activated_at=activated_at,
                                           available_at=available_at,
                                           data=s11n.to_json(data))
        return cls(model)

    def save(self):
        self.model.data = s11n.to_json(self.data)
        self.model.save()

    def process(self, storage):
        from game.abilities.deck import ABILITIES

        hero = storage.heroes[self.hero_id]

        ability = ABILITIES[self.type](AbilitiesData.objects.get(hero_id=hero.id))

        turn_number = TimePrototype.get_current_turn_number()

        energy = hero.energy

        if energy < ability.COST:
            self.model.comment = 'energy < ability.COST'
            self.state = ABILITY_TASK_STATE.ERROR
            return

        if ability.available_at > turn_number:
            self.state = ABILITY_TASK_STATE.ERROR
            self.model.comment = 'available_at (%d) > turn_number (%d)' % (ability.available_at, turn_number)
            return

        result = ability.use(storage, hero, self.data)

        if not result:
            self.model.comment = 'result is False'
            self.state = ABILITY_TASK_STATE.ERROR
            return

        self.state = ABILITY_TASK_STATE.PROCESSED
        hero.change_energy(-ability.COST)

        ability.available_at = self.available_at
        ability.save()
