
from the_tale.amqp_environment import environment

from the_tale.common.postponed_tasks.prototypes import PostponedTaskPrototype

from the_tale.game import tt_api as game_tt_api


class AbilityPrototype(object):
    TYPE = None

    def activate(self, hero, data):
        from the_tale.game.abilities.postponed_tasks import UseAbilityTask

        data['transaction_id'] = None

        if self.TYPE.cost > 0:

            status, transaction_id = game_tt_api.change_energy_balance(account_id=hero.account_id,
                                                                       type='help-{}'.format(self.TYPE.value),
                                                                       energy=-self.TYPE.cost,
                                                                       async=False,
                                                                       autocommit=False)

            if not status:
                return None

            data['transaction_id'] = transaction_id

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
        return True

    def hero_actions(self, hero, data):
        if data['transaction_id']:
            game_tt_api.commit_transaction(data['transaction_id'])
