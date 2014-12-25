# coding: utf-8

from the_tale.amqp_environment import environment

from the_tale.common.postponed_tasks import PostponedTaskPrototype


class AbilityPrototype(object):
    TYPE = None

    def activate(self, hero, data):
        from the_tale.game.abilities.postponed_tasks import UseAbilityTask

        data['hero_id'] = hero.id
        data['account_id'] = hero.account_id

        ability_task = UseAbilityTask(processor_id=self.TYPE.value,
                                      hero_id=hero.id,
                                      data=data)

        task = PostponedTaskPrototype.create(ability_task)

        environment.workers.supervisor.cmd_logic_task(hero.account_id, task.id)

        return task

    def use(self, *argv, **kwargs):
        raise NotImplementedError


    def check_hero_conditions(self, hero, data):
        return hero.energy_full >= max(1, self.TYPE.cost - hero.energy_discount)


    def hero_actions(self, hero, data):
        hero.change_energy(-self.TYPE.cost)
