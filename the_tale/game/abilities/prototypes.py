# coding: utf-8

from django.utils.log import getLogger

from dext.utils.decorators import nested_commit_on_success

from common.postponed_tasks import postponed_task, PostponedTaskPrototype
from common.utils.enum import create_enum

from game.prototypes import TimePrototype

from game.heroes.prototypes import HeroPrototype

from game.abilities.forms import AbilityForm
from game.abilities.models import AbilitiesData


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
        if PostponedTaskPrototype.check_if_used(self.get_type(), hero_id):
            return True
        return False

    def ui_info(self):
        return {'type': self.__class__.__name__.lower(),
                'available_at': self.available_at}

    def create_form(self, resource):
        form = self.FORM or AbilityForm

        if resource.request.POST:
            return form(resource.request.POST)

        return form()

    def activate(self, form, time):
        from game.workers.environment import workers_environment

        available_at = time.turn_number + (self.COOLDOWN if self.COOLDOWN else 0)

        hero = HeroPrototype.get_by_id(form.c.hero_id)

        ability_task = UseAbilityTask(ability_type=self.get_type(),
                                      hero_id=hero.id,
                                      activated_at=time.turn_number,
                                      available_at=available_at,
                                      data=form.data)

        task = PostponedTaskPrototype.create(ability_task)

        workers_environment.supervisor.cmd_activate_ability(hero.account_id, task.id)

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


ABILITY_TASK_STATE = create_enum('ABILITY_TASK_STATE', (('UNPROCESSED', 0, u'в очереди'),
                                                        ('PROCESSED', 1, u'обработана'),
                                                        ('NO_ENERGY', 2, u'не хватает энергии'),
                                                        ('COOLDOWN', 3, u'способность не готова'),
                                                        ('CAN_NOT_PROCESS', 4, u'способность нельзя применить'), ))

@postponed_task
class UseAbilityTask(object):

    TYPE = 'use-ability'
    INITIAL_STATE = ABILITY_TASK_STATE.UNPROCESSED
    LOGGER = getLogger('the-tale.workers.game_logic')

    def __init__(self, ability_type, hero_id, activated_at, available_at, data, state=INITIAL_STATE):
        self.ability_type = ability_type
        self.hero_id = hero_id
        self.activated_at = activated_at
        self.available_at = available_at
        self.data = data
        self.state = state

    def __eq__(self, other):
        return ( self.ability_type == other.ability_type and
                 self.hero_id == other.hero_id and
                 self.activated_at == other.activated_at and
                 self.available_at == other.available_at and
                 self.data == other.data and
                 self.state == other.state )

    def serialize(self):
        return { 'ability_type': self.ability_type,
                 'hero_id': self.hero_id,
                 'activated_at': self.activated_at,
                 'available_at': self.available_at,
                 'data': self.data,
                 'state': self.state}

    @classmethod
    def deserialize(cls, data):
        return cls(**data)

    @property
    def uuid(self): return self.hero_id

    @property
    def response_data(self): return {'available_at': self.available_at}

    @property
    def error_message(self): return ABILITY_TASK_STATE.CHOICES[self.state]

    @nested_commit_on_success
    def process(self, main_task, storage):
        from game.abilities.deck import ABILITIES

        hero = storage.heroes[self.hero_id]

        ability = ABILITIES[self.ability_type](AbilitiesData.objects.get(hero_id=hero.id))

        turn_number = TimePrototype.get_current_turn_number()

        energy = hero.energy

        if energy < ability.COST:
            main_task.comment = 'energy < ability.COST'
            self.state = ABILITY_TASK_STATE.NO_ENERGY
            return False

        if ability.available_at > turn_number:
            main_task.comment = 'available_at (%d) > turn_number (%d)' % (ability.available_at, turn_number)
            self.state = ABILITY_TASK_STATE.COOLDOWN
            return False

        result = ability.use(storage, hero, self.data)

        if not result:
            main_task.comment = 'result is False'
            self.state = ABILITY_TASK_STATE.CAN_NOT_PROCESS
            return False

        self.state = ABILITY_TASK_STATE.PROCESSED
        hero.change_energy(-ability.COST)

        ability.available_at = self.available_at
        ability.save()

        return True
