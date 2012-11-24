# coding: utf-8

import datetime

from django.utils.log import getLogger
from django.conf import settings as project_settings

from dext.settings import settings
from dext.utils.decorators import nested_commit_on_success

from common.amqp_queues import BaseWorker
from common import postponed_tasks

from game.prototypes import TimePrototype
from game.logic_storage import LogicStorage

class LogicException(Exception): pass



class Worker(BaseWorker):

    def __init__(self, game_queue):
        super(Worker, self).__init__(logger=getLogger('the-tale.workers.game_logic'), command_queue=game_queue)

    def set_supervisor_worker(self, supervisor_worker):
        self.supervisor_worker = supervisor_worker

    # @profile_decorator('game_logic.profiled')
    def run(self):

        while not self.exception_raised and not self.stop_required:
            cmd = self.command_queue.get(block=True)
            cmd.ack()
            self.process_cmd(cmd.payload)

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

        self.supervisor_worker.cmd_answer('initialize', self.worker_id)

    def cmd_next_turn(self, turn_number):
        return self.send_cmd('next_turn', data={'turn_number': turn_number})

    def process_next_turn(self, turn_number):
        from game.logic import log_sql_queries

        settings.refresh()

        with nested_commit_on_success():
            self.turn_number += 1

            if turn_number != self.turn_number:
                raise LogicException('dessinchonization: workers turn number (%d) not equal to command turn number (%d)' % (self.turn_number, turn_number))


            if TimePrototype.get_current_turn_number() != self.turn_number:
                raise LogicException('dessinchonization: workers turn number (%d) not equal to saved turn number (%d)' % (self.turn_number,
                                                                                                                          TimePrototype.get_current_turn_number()))

            self.storage.process_turn()
            self.storage.save_changed_data()

            for hero_id in self.storage.skipped_heroes:
                self.supervisor_worker.cmd_account_release_required(self.storage.heroes[hero_id].account_id)


        if project_settings.DEBUG_DATABASE_USAGE:
            log_sql_queries(turn_number)

        self.supervisor_worker.cmd_answer('next_turn', self.worker_id)

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        # no need to save data, since they automaticaly saved on every turn
        self.initialized = False
        self.supervisor_worker.cmd_answer('stop', self.worker_id)
        self.stop_required = True
        self.logger.info('LOGIC STOPPED')

    def cmd_register_account(self, account_id):
        return self.send_cmd('register_account', {'account_id': account_id})

    def process_register_account(self, account_id):
        from accounts.prototypes import AccountPrototype
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))

    def cmd_release_account(self, account_id):
        return self.send_cmd('release_account', {'account_id': account_id})

    def process_release_account(self, account_id):
        from accounts.prototypes import AccountPrototype
        self.storage.release_account_data(AccountPrototype.get_by_id(account_id))
        self.supervisor_worker.cmd_account_released(account_id)

    def cmd_logic_task(self, account_id, task_id):
        return self.send_cmd('logic_task', {'task_id': task_id,
                                            'account_id': account_id})

    def process_logic_task(self, account_id, task_id):
        task = postponed_tasks.PostponedTaskPrototype.get_by_id(task_id)
        task.process(self.logger, storage=self.storage)
        # storage data MUST be saved in task.process method
        task.save()

    def cmd_mark_hero_as_not_fast(self, account_id, hero_id):
        self.send_cmd('mark_hero_as_not_fast', {'hero_id': hero_id,
                                                'account_id': account_id})

    def process_mark_hero_as_not_fast(self, account_id, hero_id):
        self.storage.heroes[hero_id].is_fast = False

    def cmd_mark_hero_as_active(self, account_id, hero_id):
        self.send_cmd('mark_hero_as_active', {'hero_id': hero_id,
                                              'account_id': account_id})

    def process_mark_hero_as_active(self, account_id, hero_id):
        self.storage.heroes[hero_id].mark_as_active()

    def cmd_highlevel_data_updated(self):
        self.send_cmd('highlevel_data_updated')

    def process_highlevel_data_updated(self):
        settings.refresh()

        self.storage.on_highlevel_data_updated()

    def cmd_set_might(self, account_id, hero_id, might):
        self.send_cmd('set_might', {'hero_id': hero_id, 'might': might, 'account_id': account_id})

    def process_set_might(self, account_id, hero_id, might):

        hero = self.storage.heroes[hero_id]
        hero.might = might
        hero.might_updated_time = datetime.datetime.now()
        hero.save()
