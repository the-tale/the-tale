# coding: utf-8
import time

from django.utils.log import getLogger

from dext.settings import settings

from the_tale.common.amqp_queues import connection, BaseWorker, exceptions as amqp_exceptions
from the_tale.common import postponed_tasks

from the_tale.accounts.models import Account

from the_tale.game.prototypes import TimePrototype, SupervisorTaskPrototype, GameState
from the_tale.game.bundles import BundlePrototype
from the_tale.game.models import SupervisorTask, SUPERVISOR_TASK_STATE
from the_tale.game.conf import game_settings


class SupervisorException(Exception): pass


class Worker(BaseWorker):

    logger = getLogger('the-tale.workers.game_supervisor')
    name = 'game supervisor'
    command_name = 'game_supervisor'

    def __init__(self, supervisor_queue, answers_queue, stop_queue):
        super(Worker, self).__init__(command_queue=supervisor_queue)
        self.answers_queue = connection.create_simple_buffer(answers_queue)
        self.stop_queue = connection.create_simple_buffer(stop_queue)

    def clean_queues(self):
        super(Worker, self).clean_queues()
        self.answers_queue.queue.purge()
        self.stop_queue.queue.purge()

    run = BaseWorker.run_simple

    def initialize(self):
        self.cmd_initialize()

    def cmd_initialize(self):
        self.send_cmd('initialize', {})

    def process_initialize(self):
        from the_tale.game.workers.environment import workers_environment as game_environment

        self.time = TimePrototype.get_current_time()

        postponed_tasks.PostponedTaskPrototype.reset_all()

        #initialization
        self.logger.info('initialize logic')
        game_environment.logic.cmd_initialize(turn_number=self.time.turn_number, worker_id='logic')
        self.wait_answers_from('initialize', workers=['logic'])

        self.logger.info('initialize long commands')
        game_environment.long_commands.cmd_initialize(worker_id='game_long_commands')
        self.wait_answers_from('initialize', workers=['game_long_commands'])

        if game_settings.ENABLE_WORKER_HIGHLEVEL:
            self.logger.info('initialize highlevel')
            game_environment.highlevel.cmd_initialize(turn_number=self.time.turn_number, worker_id='highlevel')
            self.wait_answers_from('initialize', workers=['highlevel'])
        else:
            self.logger.info('skip initialization of highlevel')

        if game_settings.ENABLE_WORKER_TURNS_LOOP:
            self.logger.info('initialize turns loop')
            game_environment.turns_loop.cmd_initialize(worker_id='turns_loop')
            self.wait_answers_from('initialize', workers=['turns_loop'])
        else:
            self.logger.info('skip initialization of turns loop')

        if game_settings.ENABLE_PVP:
            self.logger.info('initialize pvp balancer')
            game_environment.pvp_balancer.cmd_initialize(worker_id='pvp_balancer')
            self.wait_answers_from('initialize', workers=['pvp_balancer'])
        else:
            self.logger.info('skip initialization of pvp balancer')

        self.logger.info('child workers initialized')

        ####################################
        # register all tasks

        self.logger.info('register task')

        self.tasks = {}
        self.accounts_for_tasks = {}
        self.accounts_owners = {}
        self.accounts_queues = {}

        for task_model in SupervisorTask.objects.filter(state=SUPERVISOR_TASK_STATE.WAITING):
            task = SupervisorTaskPrototype(task_model)
            self.register_task(task, release_accounts=False)

        ####################################
        # load accounts

        self.logger.info('load accounts')

        # distribute bundles
        self.logger.info('distribute bundles')
        BundlePrototype.distribute('logic')

        # distribute accounts

        self.logger.info('distribute accounts')

        for account_id in Account.objects.all().values_list('id', flat=True):
            self.register_account(account_id)

        self.initialized = True
        self.wait_next_turn_answer = False

        GameState.start()

        self.logger.info('SUPERVISOR INITIALIZED')

    def register_task(self, task, release_accounts=True):
        if task.id in self.tasks:
            self._force_stop()
            raise SupervisorException('task %d has been registered already' % task.id)

        self.tasks[task.id] = task

        for account_id in task.members:
            if account_id in self.accounts_for_tasks:
                self._force_stop()
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
        from the_tale.game.workers.environment import workers_environment as game_environment
        self.accounts_owners[account_id] = 'logic'

        game_environment.logic.cmd_register_account(account_id)

        if account_id in self.accounts_queues:
            for cmd_name, kwargs in self.accounts_queues[account_id]:
                getattr(game_environment.logic, 'cmd_' + cmd_name)(**kwargs)
            del self.accounts_queues[account_id]

    def send_release_account_cmd(self, account_id):
        from the_tale.game.workers.environment import workers_environment as game_environment
        if self.accounts_owners[account_id] is not None:
            self.accounts_owners[account_id] = None
            game_environment.logic.cmd_release_account(account_id)

    def dispatch_logic_cmd(self, account_id, cmd_name, kwargs):
        from the_tale.game.workers.environment import workers_environment as game_environment
        if account_id in self.accounts_owners and self.accounts_owners[account_id] == 'logic':
            getattr(game_environment.logic, 'cmd_' + cmd_name)(**kwargs)
        else:
            if account_id not in self.accounts_owners:
                self.logger.warn('try to dispatch command for unregistered account %d (command "%s" args %r)' % (account_id, cmd_name, kwargs))
            if account_id not in self.accounts_queues:
                self.accounts_queues[account_id] = []
            self.accounts_queues[account_id].append((cmd_name, kwargs))

    def cmd_next_turn(self):
        return self.send_cmd('next_turn')


    def wait_answer_from_next_turn(self):

        if not self.wait_next_turn_answer:
            return

        try:
            # wait answer from previouse turn processing
            # we do not want to increment turn number in middle of turn processing
            self.wait_answers_from('next_turn', workers=['logic'], timeout=game_settings.PROCESS_TURN_WAIT_LOGIC_TIMEOUT)
        except amqp_exceptions.WaitAnswerTimeoutError:
            self.logger.error('next turn timeout while getting answer from logic')
            self._force_stop()
            raise

    def process_next_turn(self):
        from the_tale.game.workers.environment import workers_environment as game_environment

        self.wait_answer_from_next_turn()

        self.time.increment_turn()

        settings.refresh()

        game_environment.logic.cmd_next_turn(turn_number=self.time.turn_number)
        self.wait_next_turn_answer = True

        try:
            if game_settings.ENABLE_WORKER_HIGHLEVEL:
                game_environment.highlevel.cmd_next_turn(turn_number=self.time.turn_number)
        except amqp_exceptions.WaitAnswerTimeoutError:
            self.logger.error('next turn timeout while getting answer from highlevel')
            self._force_stop()
            raise

    def cmd_stop(self):
        return self.send_cmd('stop')

    def _force_stop(self):
        self.logger.error('force stop all workers, send signals.')

        GameState.stop()

        self._send_stop_signals()

        self.logger.error('signals sent')

    def _send_stop_signals(self):
        from the_tale.game.workers.environment import workers_environment as game_environment

        game_environment.logic.cmd_stop()
        game_environment.long_commands.cmd_stop()

        if game_settings.ENABLE_WORKER_HIGHLEVEL:
            game_environment.highlevel.cmd_stop()
        if game_settings.ENABLE_WORKER_TURNS_LOOP:
            game_environment.turns_loop.cmd_stop()
        if game_settings.ENABLE_PVP:
            game_environment.pvp_balancer.cmd_stop()

    def process_stop(self):

        self.wait_answer_from_next_turn()

        GameState.stop()

        self._send_stop_signals()

        wait_answers_from = ['logic', 'game_long_commands']

        if game_settings.ENABLE_WORKER_HIGHLEVEL:
            wait_answers_from.append('highlevel')

        if game_settings.ENABLE_WORKER_TURNS_LOOP:
            wait_answers_from.append('turns_loop')

        if game_settings.ENABLE_PVP:
            wait_answers_from.append('pvp_balancer')

        self.wait_answers_from('stop', workers=wait_answers_from, timeout=game_settings.STOP_WAIT_TIMEOUT)

        self.stop_queue.put({'code': 'stopped', 'worker': 'supervisor'}, serializer='json', compression=None)

        self.stop_required = True

        self.logger.info('SUPERVISOR STOPPED')


    def cmd_register_new_account(self, account_id):
        self.send_cmd('register_new_account', {'account_id': account_id})

    def process_register_new_account(self, account_id):
        BundlePrototype.get_by_account_id(account_id).change_owner('logic')
        self.register_account(account_id)

    def cmd_logic_task(self, account_id, task_id):
        self.send_cmd('logic_task', {'task_id': task_id,
                                     'account_id': account_id })

    def process_logic_task(self, account_id, task_id):
        self.dispatch_logic_cmd(account_id, 'logic_task', {'account_id': account_id,
                                                           'task_id': task_id} )

    def cmd_update_hero_with_account_data(self, account_id, hero_id, is_fast, premium_end_at, active_end_at, ban_end_at, might):
        self.send_cmd('update_hero_with_account_data', {'hero_id': hero_id,
                                                        'account_id': account_id,
                                                        'is_fast': is_fast,
                                                        'premium_end_at': time.mktime(premium_end_at.timetuple()),
                                                        'active_end_at': time.mktime(active_end_at.timetuple()),
                                                        'ban_end_at': time.mktime(ban_end_at.timetuple()),
                                                        'might': might})

    def process_update_hero_with_account_data(self, account_id, hero_id, is_fast, premium_end_at, active_end_at, ban_end_at, might):
        self.dispatch_logic_cmd(account_id, 'update_hero_with_account_data', {'account_id': account_id,
                                                                              'hero_id': hero_id,
                                                                              'is_fast': is_fast,
                                                                              'premium_end_at': premium_end_at,
                                                                              'active_end_at': active_end_at,
                                                                              'ban_end_at': ban_end_at,
                                                                              'might': might} )

    def cmd_start_hero_caching(self, account_id):
        self.send_cmd('start_hero_caching', {'account_id': account_id})

    def process_start_hero_caching(self, account_id):
        self.dispatch_logic_cmd(account_id, 'start_hero_caching', {'account_id': account_id} )

    def cmd_highlevel_data_updated(self):
        self.send_cmd('highlevel_data_updated')

    def process_highlevel_data_updated(self):
        from the_tale.game.workers.environment import workers_environment as game_environment
        game_environment.logic.cmd_highlevel_data_updated()

    def cmd_force_save(self, account_id):
        self.send_cmd('force_save', {'account_id': account_id})

    def process_force_save(self, account_id):
        self.dispatch_logic_cmd(account_id, 'force_save', {'account_id': account_id} )

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
