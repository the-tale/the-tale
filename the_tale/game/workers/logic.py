# coding: utf-8
import gc
import datetime

from django.utils.log import getLogger
from django.conf import settings as project_settings

from dext.settings import settings
# from dext.utils.profile import profile_decorator

from the_tale.common.amqp_queues import BaseWorker
from the_tale.common import postponed_tasks

from the_tale.game.prototypes import TimePrototype
from the_tale.game.logic_storage import LogicStorage
from the_tale.game.workers.environment import workers_environment as game_environment
from the_tale.game.conf import game_settings


class LogicException(Exception): pass



class Worker(BaseWorker):

    logger = getLogger('the-tale.workers.game_logic')
    name = 'game logic'
    command_name = 'game_logic'
    stop_signal_required = False

    def __init__(self, game_queue):
        super(Worker, self).__init__(command_queue=game_queue)

    # run = profile_decorator('game_logic.profiled')(BaseWorker.run_simple)
    run = BaseWorker.run_simple

    def initialize(self):
        # worker initialized by supervisor
        pass

    def cmd_initialize(self, turn_number, worker_id):
        self.send_cmd('initialize', {'turn_number': turn_number, 'worker_id': worker_id})

    def process_initialize(self, turn_number, worker_id):

        if self.initialized:
            self.logger.warn('WARNING: game already initialized, do reinitialization')

        postponed_tasks.autodiscover()

        self.storage = LogicStorage()

        self.initialized = True
        self.turn_number = turn_number
        self.queue = []
        self.worker_id = worker_id

        self.logger.info('GAME INITIALIZED')

        game_environment.supervisor.cmd_answer('initialize', self.worker_id)

    def cmd_next_turn(self, turn_number):
        return self.send_cmd('next_turn', data={'turn_number': turn_number})

    def process_next_turn(self, turn_number):
        from the_tale.game.logic import log_sql_queries

        settings.refresh()

        self.turn_number += 1

        if turn_number != self.turn_number:
            raise LogicException('dessinchonization: workers turn number (%d) not equal to command turn number (%d)' % (self.turn_number, turn_number))


        if TimePrototype.get_current_turn_number() != self.turn_number:
            raise LogicException('dessinchonization: workers turn number (%d) not equal to saved turn number (%d)' % (self.turn_number,
                                                                                                                      TimePrototype.get_current_turn_number()))

        self.storage.process_turn(logger=self.logger)
        self.storage.save_changed_data(logger=self.logger)

        for hero_id in self.storage.skipped_heroes:
            game_environment.supervisor.cmd_account_release_required(self.storage.heroes[hero_id].account_id)


        if project_settings.DEBUG_DATABASE_USAGE:
            log_sql_queries(turn_number)

        game_environment.supervisor.cmd_answer('next_turn', self.worker_id)

        if game_settings.COLLECT_GARBAGE:
            gc.collect()

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        # no need to save data, since they automaticaly saved on every turn
        self.initialized = False
        self.storage.save_all(logger=self.logger)
        game_environment.supervisor.cmd_answer('stop', self.worker_id)
        self.stop_required = True
        self.logger.info('LOGIC STOPPED')

    def cmd_register_account(self, account_id):
        return self.send_cmd('register_account', {'account_id': account_id})

    def process_register_account(self, account_id):
        from the_tale.accounts.prototypes import AccountPrototype
        account = AccountPrototype.get_by_id(account_id)
        if account is None:
            raise LogicException('can not get account with id "%d"' % (account_id,))
        self.storage.load_account_data(account)

    def cmd_release_account(self, account_id):
        return self.send_cmd('release_account', {'account_id': account_id})

    def process_release_account(self, account_id):
        from the_tale.accounts.prototypes import AccountPrototype
        self.storage.release_account_data(AccountPrototype.get_by_id(account_id))
        game_environment.supervisor.cmd_account_released(account_id)

    def cmd_logic_task(self, account_id, task_id):
        return self.send_cmd('logic_task', {'task_id': task_id,
                                            'account_id': account_id})

    def process_logic_task(self, account_id, task_id): # pylint: disable=W0613
        settings.refresh()

        task = postponed_tasks.PostponedTaskPrototype.get_by_id(task_id)
        task.process(self.logger, storage=self.storage)
        task.do_postsave_actions()

        self.storage.recache_account_data(account_id)


    def cmd_start_hero_caching(self, account_id, hero_id):
        self.send_cmd('start_hero_caching', {'hero_id': hero_id,
                                             'account_id': account_id})

    def process_start_hero_caching(self, account_id, hero_id):
        self.storage.heroes[hero_id].ui_caching_started_at = datetime.datetime.now()
        self.storage.recache_account_data(account_id)

    def cmd_update_hero_with_account_data(self, account_id, hero_id, is_fast, premium_end_at, active_end_at, ban_end_at, might):
        self.send_cmd('update_hero_with_account_data', {'hero_id': hero_id,
                                                        'account_id': account_id,
                                                        'is_fast': is_fast,
                                                        'premium_end_at': premium_end_at,
                                                        'active_end_at': active_end_at,
                                                        'ban_end_at': ban_end_at,
                                                        'might': might})

    def process_update_hero_with_account_data(self, account_id, hero_id, is_fast, premium_end_at, active_end_at, ban_end_at, might):
        self.storage.heroes[hero_id].update_with_account_data(is_fast=is_fast,
                                                              premium_end_at=datetime.datetime.fromtimestamp(premium_end_at),
                                                              active_end_at=datetime.datetime.fromtimestamp(active_end_at),
                                                              ban_end_at=datetime.datetime.fromtimestamp(ban_end_at),
                                                              might=might)
        self.storage.save_account_data(account_id, update_cache=True)

    def cmd_highlevel_data_updated(self):
        self.send_cmd('highlevel_data_updated')

    def process_highlevel_data_updated(self):
        settings.refresh()
        self.storage.on_highlevel_data_updated()
