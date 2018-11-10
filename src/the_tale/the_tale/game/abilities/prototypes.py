
import smart_imports

smart_imports.all()


class AbilityPrototype(object):
    TYPE = None

    def activate(self, hero, data):
        data['transaction_id'] = None

        if self.TYPE.cost > 0:

            status, transaction_id = game_tt_services.energy.cmd_change_balance(account_id=hero.account_id,
                                                                                type='help-{}'.format(self.TYPE.value),
                                                                                energy=-self.TYPE.cost,
                                                                                async=False,
                                                                                autocommit=False)

            if not status:
                return None

            data['transaction_id'] = transaction_id

        data['hero_id'] = hero.id
        data['account_id'] = hero.account_id

        ability_task = postponed_tasks.UseAbilityTask(processor_id=self.TYPE.value,
                                                      hero_id=hero.id,
                                                      data=data)

        task = PostponedTaskPrototype.create(ability_task)

        amqp_environment.environment.workers.supervisor.cmd_logic_task(hero.account_id, task.id)

        return task

    def use(self, *argv, **kwargs):
        raise NotImplementedError

    def check_hero_conditions(self, hero, data):
        return True

    def hero_actions(self, hero, data):
        if data['transaction_id']:
            game_tt_services.energy.cmd_commit_transaction(data['transaction_id'])
