# coding: utf-8
from django.utils.log import getLogger

from common.amqp_queues import connection, BaseWorker

from accounts.models import Account

from game.prototypes import TimePrototype, SupervisorTaskPrototype
from game.bundles import BundlePrototype
from game.models import Bundle, SupervisorTask, SUPERVISOR_TASK_STATE
from game.abilities.prototypes import AbilityTaskPrototype
from game.heroes.prototypes import ChooseAbilityTaskPrototype
from game.heroes.preferences import ChoosePreferencesTaskPrototype
from game.conf import game_settings


class SupervisorException(Exception): pass

class Worker(BaseWorker):

    def __init__(self, supervisor_queue, answers_queue, stop_queue):
        super(Worker, self).__init__(logger=getLogger('the-tale.workers.game_supervisor'), command_queue=supervisor_queue)
        self.answers_queue = connection.SimpleQueue(answers_queue)
        self.stop_queue = connection.SimpleQueue(stop_queue)

    def set_turns_loop_worker(self, turns_loop_worker):
        self.turns_loop_worker = turns_loop_worker

    def set_might_calculator_worker(self, might_calculator_worker):
        self.might_calculator_worker = might_calculator_worker

    def set_logic_worker(self, logic_worker):
        self.logic_worker = logic_worker

    def set_highlevel_worker(self, highlevel_worker):
        self.highlevel_worker = highlevel_worker

    def set_long_commands_worker(self, long_commands):
        self.long_commands_worker = long_commands

    def set_pvp_balancer(self, pvp_balancer):
        self.pvp_balancer = pvp_balancer

    def clean_queues(self):
        super(Worker, self).clean_queues()
        self.answers_queue.queue.purge()
        self.stop_queue.queue.purge()

    def run(self):

        while not self.exception_raised and not self.stop_required:
            game_cmd = self.command_queue.get(block=True)
            game_cmd.ack()
            self.process_cmd(game_cmd.payload)

    def initialize(self):
        self.time = TimePrototype.get_current_time()

        #clearing
        AbilityTaskPrototype.reset_all()
        ChooseAbilityTaskPrototype.reset_all()
        ChoosePreferencesTaskPrototype.reset_all()

        #initialization
        self.logic_worker.cmd_initialize(turn_number=self.time.turn_number, worker_id='logic')
        self.wait_answers_from('initialize', workers=['logic'])

        if game_settings.ENABLE_WORKER_HIGHLEVEL:
            self.highlevel_worker.cmd_initialize(turn_number=self.time.turn_number, worker_id='highlevel')
            self.wait_answers_from('initialize', workers=['highlevel'])

        if game_settings.ENABLE_WORKER_TURNS_LOOP:
            self.turns_loop_worker.cmd_initialize(worker_id='turns_loop')
            self.wait_answers_from('initialize', workers=['turns_loop'])

        if game_settings.ENABLE_WORKER_MIGHT_CALCULATOR:
            self.might_calculator_worker.cmd_initialize(worker_id='might_calculator')
            self.wait_answers_from('initialize', workers=['might_calculator'])

        if game_settings.ENABLE_WORKER_LONG_COMMANDS:
            self.long_commands_worker.cmd_initialize(worker_id='long_commands')
            self.wait_answers_from('initialize', workers=['long_commands'])

        if game_settings.ENABLE_PVP:
            self.pvp_balancer.cmd_initialize(worker_id='pvp_balancer')
            self.wait_answers_from('initialize', workers=['pvp_balancer'])

        ####################################
        # register all tasks
        self.tasks = {}
        self.accounts_for_tasks = {}

        for task_model in SupervisorTask.objects.filter(state=SUPERVISOR_TASK_STATE.WAITING):
            task = SupervisorTaskPrototype(task_model)
            self.register_task(task, release_accounts=False)

        ####################################
        # load accounts

        # distribute bundles
        for bundle_model in Bundle.objects.all():
            bundle = BundlePrototype(bundle_model)
            bundle.owner = 'worker'
            bundle.save()

        # distribute accounts
        for account_id in Account.objects.all().values_list('id', flat=True):
            self.register_account(account_id)

        self.initialized = True

        self.logger.info('SUPERVISOR INITIALIZED')

    def register_task(self, task, release_accounts=True):
        if task.id in self.tasks:
            raise SupervisorException('task %d has been registered already' % task.id)

        self.tasks[task.id] = task

        for account_id in task.members:
            if account_id in self.accounts_for_tasks:
                raise SupervisorException('account %d already register for task %d (second task: %d)' % (account_id, self.accounts_for_tasks[account_id], task.id))
            self.accounts_for_tasks[account_id] = task.id

            if release_accounts:
                self.logic_worker.cmd_release_account(account_id)


    def register_account(self, account_id):
        if account_id in self.accounts_for_tasks:
            task = self.tasks[self.accounts_for_tasks[account_id]]
            task.capture_member(account_id)

            if task.all_members_captured:
                del self.tasks[self.accounts_for_tasks[account_id]]
                task.process()
                for member_id in task.members:
                    del self.accounts_for_tasks[member_id]
                    self.logic_worker.cmd_register_account(member_id)
                task.remove()
            return

        self.logic_worker.cmd_register_account(account_id)

    def cmd_next_turn(self):
        return self.send_cmd('next_turn')

    def process_next_turn(self):
        self.time.increment_turn()
        self.time.save()

        self.logic_worker.cmd_next_turn(turn_number=self.time.turn_number)
        self.wait_answers_from('next_turn', workers=['logic'])

        if game_settings.ENABLE_WORKER_HIGHLEVEL:
            self.highlevel_worker.cmd_next_turn(turn_number=self.time.turn_number)
            self.wait_answers_from('next_turn', workers=['highlevel'])

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        self.logic_worker.cmd_stop()
        self.wait_answers_from('stop', workers=['logic'])

        if game_settings.ENABLE_WORKER_HIGHLEVEL:
            self.highlevel_worker.cmd_stop()
            self.wait_answers_from('stop', workers=['highlevel'])

        if game_settings.ENABLE_WORKER_TURNS_LOOP:
            self.turns_loop_worker.cmd_stop()
            self.wait_answers_from('stop', workers=['turns_loop'])

        if game_settings.ENABLE_WORKER_MIGHT_CALCULATOR:
            self.might_calculator_worker.cmd_stop()
            self.wait_answers_from('stop', workers=['might_calculator'])

        if game_settings.ENABLE_WORKER_LONG_COMMANDS:
            self.long_commands_worker.cmd_stop()
            self.wait_answers_from('stop', workers=['long_commands'])

        if game_settings.ENABLE_PVP:
            self.pvp_balancer.cmd_stop()
            self.wait_answers_from('stop', workers=['pvp_balancer'])


        self.stop_queue.put({'code': 'stopped', 'worker': 'supervisor'}, serializer='json', compression=None)

        self.stop_required = True

        self.logger.info('SUPERVISOR STOPPED')


    def cmd_register_bundle(self, bundle_id):
        self.send_cmd('register_bundle', {'bundle_id': bundle_id})

    def process_register_bundle(self, bundle_id):
        bundle = BundlePrototype.get_by_id(bundle_id)
        bundle.owner = 'worker'
        bundle.save()

        for account_id in bundle.get_accounts_ids():
            self.register_account(account_id)

    def cmd_activate_ability(self, ability_task_id):
        self.send_cmd('activate_ability', {'ability_task_id': ability_task_id})

    def process_activate_ability(self, ability_task_id):
        self.logic_worker.cmd_activate_ability(ability_task_id)

    def cmd_choose_hero_ability(self, ability_task_id):
        self.send_cmd('choose_hero_ability', {'ability_task_id': ability_task_id})

    def process_choose_hero_ability(self, ability_task_id):
        self.logic_worker.cmd_choose_hero_ability(ability_task_id)

    def cmd_choose_hero_preference(self, preference_task_id):
        self.send_cmd('choose_hero_preference', {'preference_task_id': preference_task_id})

    def process_choose_hero_preference(self, preference_task_id):
        self.logic_worker.cmd_choose_hero_preference(preference_task_id)

    def cmd_mark_hero_as_not_fast(self, hero_id):
        self.send_cmd('mark_hero_as_not_fast', {'hero_id': hero_id})

    def process_mark_hero_as_not_fast(self, hero_id):
        self.logic_worker.cmd_mark_hero_as_not_fast(hero_id)

    def cmd_mark_hero_as_active(self, hero_id):
        self.send_cmd('mark_hero_as_active', {'hero_id': hero_id})

    def process_mark_hero_as_active(self, hero_id):
        self.logic_worker.cmd_mark_hero_as_active(hero_id)

    def cmd_highlevel_data_updated(self):
        self.send_cmd('highlevel_data_updated')

    def process_highlevel_data_updated(self):
        self.logic_worker.cmd_highlevel_data_updated()

    def cmd_set_might(self, hero_id, might):
        self.send_cmd('set_might', {'hero_id': hero_id, 'might': might})

    def process_set_might(self, hero_id, might):
        self.logic_worker.cmd_set_might(hero_id, might)

    def cmd_recalculate_ratings(self):
        return self.send_cmd('recalculate_ratings')

    def process_recalculate_ratings(self):
        self.long_commands_worker.cmd_recalculate_ratings()

    def cmd_run_vacuum(self):
        return self.send_cmd('recalculate_ratings')

    def process_run_vacuum(self):
        self.long_commands_worker.cmd_run_vacuum()

    def cmd_account_released(self, account_id):
        return self.send_cmd('account_released', {'account_id': account_id})

    def process_account_released(self, account_id):
        self.register_account(account_id)

    def cmd_add_task(self, task_id):
        return self.send_cmd('add_task', {'task_id': task_id})

    def process_add_task(self, task_id):
        self.register_task(SupervisorTaskPrototype.get_by_id(task_id))
