# coding: utf-8

from common.postponed_tasks import PostponedTaskPrototype

from game.heroes.prototypes import HeroPrototype

from game.abilities.forms import AbilityForm


class AbilityPrototype(object):

    COST = None

    NAME = None
    DESCRIPTION = None

    FORM = None
    TEMPLATE = None

    COMMAND_PREFIX = None

    @classmethod
    def get_type(cls): return cls.__name__.lower()

    @classmethod
    def need_form(cls):
        return cls.FORM is not None

    def ui_info(self):
        return {'type': self.__class__.__name__.lower()}

    def create_form(self, resource):
        form = self.FORM or AbilityForm

        if resource.request.POST:
            return form(resource.request.POST)

        return form()

    def activate(self, form, time):
        from game.workers.environment import workers_environment
        from game.abilities.postponed_tasks import UseAbilityTask

        hero = HeroPrototype.get_by_id(form.c.hero_id)

        ability_task = UseAbilityTask(ability_type=self.get_type(),
                                      hero_id=hero.id,
                                      data=form.c.data)

        task = PostponedTaskPrototype.create(ability_task)

        workers_environment.supervisor.cmd_logic_task(hero.account_id, task.id)

        return task

    def use(self, form):
        pass

    def save(self):
        self.model.save()
