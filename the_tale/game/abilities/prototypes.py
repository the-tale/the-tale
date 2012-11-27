# coding: utf-8

from common.postponed_tasks import PostponedTaskPrototype

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
        from game.abilities.postponed_tasks import UseAbilityTask

        available_at = time.turn_number + (self.COOLDOWN if self.COOLDOWN else 0)

        hero = HeroPrototype.get_by_id(form.c.hero_id)

        ability_task = UseAbilityTask(ability_type=self.get_type(),
                                      hero_id=hero.id,
                                      activated_at=time.turn_number,
                                      available_at=available_at,
                                      data=form.c.data)

        task = PostponedTaskPrototype.create(ability_task)

        workers_environment.supervisor.cmd_logic_task(hero.account_id, task.id)

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
