# coding: utf-8
from django.utils.log import getLogger

from dext.settings import settings

from common.amqp_queues import connection, BaseWorker
from common import postponed_tasks

from accounts.models import Account

from game.prototypes import TimePrototype, SupervisorTaskPrototype
from game.bundles import BundlePrototype
from game.models import Bundle, SupervisorTask, SUPERVISOR_TASK_STATE
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

    def cmd_initialize(self):
        self.send_cmd('initialize', {})

    def process_initialize(self):

        self.time = TimePrototype.get_current_time()

        postponed_tasks.PostponedTaskPrototype.reset_all()

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
        self.accounts_owners = {}
        self.accounts_queues = {}

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
                self.send_release_account_cmd(account_id)


    def register_account(self, account_id):
        self.accounts_owners[account_id] = 'supervisor'

        if account_id in self.accounts_for_tasks:
            task = self.tasks[self.accounts_for_tasks[account_id]]
            task.capture_member(account_id)

            if task.all_members_captured:
                del self.tasks[self.accounts_for_tasks[account_id]]
                task.process()
                for member_id in task.members:
                    del self.accounts_for_tasks[member_id]
                    self.send_register_account_cmd(member_id)
                task.remove()
            return

        self.send_register_account_cmd(account_id)

    def send_register_account_cmd(self, account_id):
        self.accounts_owners[account_id] = 'logic'

        self.logic_worker.cmd_register_account(account_id)

        if account_id in self.accounts_queues:
            for cmd_name, kwargs in self.accounts_queues[account_id]:
                getattr(self.logic_worker, 'cmd_' + cmd_name)(**kwargs)
            del self.accounts_queues[account_id]

    def send_release_account_cmd(self, account_id):
        self.accounts_owners[account_id] = None
        self.logic_worker.cmd_release_account(account_id)

    def dispatch_logic_cmd(self, account_id, cmd_name, kwargs):
        if account_id in self.accounts_owners and self.accounts_owners[account_id] == 'logic':
            getattr(self.logic_worker, 'cmd_' + cmd_name)(**kwargs)
        else:
            if account_id not in self.accounts_owners:
                self.logger.warn('try to dispatch command for unregistered account %d (command "%s" args %r)' % (account_id, cmd_name, kwargs))
            if account_id not in self.accounts_queues:
                self.accounts_queues[account_id] = []
            self.accounts_queues[account_id].append((cmd_name, kwargs))

    def cmd_next_turn(self):
        return self.send_cmd('next_turn')

    def process_next_turn(self):
        self.time.increment_turn()
        self.time.save()

        settings.refresh()

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


    def cmd_register_new_account(self, account_id):
        self.send_cmd('register_new_account', {'account_id': account_id})

    def process_register_new_account(self, account_id):
        bundle = BundlePrototype.get_by_account_id(account_id)
        bundle.owner = 'worker'
        bundle.save()
        self.register_account(account_id)

    def cmd_logic_task(self, account_id, task_id):
        self.send_cmd('logic_task', {'task_id': task_id,
                                     'account_id': account_id })

    def process_logic_task(self, account_id, task_id):
        self.dispatch_logic_cmd(account_id, 'logic_task', {'account_id': account_id,
                                                           'task_id': task_id} )

    def cmd_mark_hero_as_not_fast(self, account_id, hero_id):
        self.send_cmd('mark_hero_as_not_fast', {'hero_id': hero_id,
                                                'account_id': account_id})

    def process_mark_hero_as_not_fast(self, account_id, hero_id):
        self.dispatch_logic_cmd(account_id, 'mark_hero_as_not_fast', {'account_id': account_id,
                                                                       'hero_id': hero_id} )

    def cmd_start_hero_caching(self, account_id, hero_id):
        self.send_cmd('start_hero_caching', {'hero_id': hero_id,
                                             'account_id': account_id})

    def process_start_hero_caching(self, account_id, hero_id):
        self.dispatch_logic_cmd(account_id, 'start_hero_caching', {'account_id': account_id,
                                                                   'hero_id': hero_id} )

    def cmd_mark_hero_as_active(self, account_id, hero_id):
        self.send_cmd('mark_hero_as_active', {'hero_id': hero_id,
                                              'account_id': account_id})

    def process_mark_hero_as_active(self, account_id, hero_id):
        self.dispatch_logic_cmd(account_id, 'mark_hero_as_active', {'account_id': account_id,
                                                                    'hero_id': hero_id} )

    def cmd_highlevel_data_updated(self):
        self.send_cmd('highlevel_data_updated')

    def process_highlevel_data_updated(self):
        self.logic_worker.cmd_highlevel_data_updated()

    def cmd_set_might(self, account_id, hero_id, might):
        self.send_cmd('set_might', {'hero_id': hero_id, 'might': might, 'account_id': account_id})

    def process_set_might(self, account_id, hero_id, might):
        self.dispatch_logic_cmd(account_id, 'set_might', {'account_id': account_id,
                                                          'hero_id': hero_id,
                                                          'might': might} )

    def cmd_recalculate_ratings(self):
        return self.send_cmd('recalculate_ratings')

    def process_recalculate_ratings(self):
        self.long_commands_worker.cmd_recalculate_ratings()

    def cmd_run_cleaning(self):
        return self.send_cmd('recalculate_ratings')

    def process_run_cleaning(self):
        self.long_commands_worker.cmd_run_cleaning()

    def cmd_account_release_required(self, account_id):
        return self.send_cmd('account_release_required', {'account_id': account_id})

    def process_account_release_required(self, account_id):
        self.send_release_account_cmd(account_id)

    def cmd_account_released(self, account_id):
        return self.send_cmd('account_released', {'account_id': account_id})

    def process_account_released(self, account_id):
        self.register_account(account_id)

    def cmd_add_task(self, task_id):
        return self.send_cmd('add_task', {'task_id': task_id})

    def process_add_task(self, task_id):
        self.register_task(SupervisorTaskPrototype.get_by_id(task_id))
