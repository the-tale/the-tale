# coding: utf-8
import gc
import datetime

# from dext.common.utils import profile

from the_tale.amqp_environment import environment

from the_tale.common.utils import workers
from the_tale.common import postponed_tasks

from the_tale.game.prototypes import TimePrototype
from the_tale.game.logic_storage import LogicStorage
from the_tale.game.conf import game_settings

from the_tale.game.quests import logic as quests_logic


class LogicException(Exception): pass



class Worker(workers.BaseWorker):
    STOP_SIGNAL_REQUIRED = False

    def initialize(self):
        # worker initialized by supervisor
        pass

    def cmd_initialize(self, turn_number, worker_id):
        self.send_cmd('initialize', {'turn_number': turn_number, 'worker_id': worker_id})

    def process_initialize(self, turn_number, worker_id):

        if self.initialized:
            self.logger.warn('WARNING: game already initialized, do reinitialization')

        self.storage = LogicStorage()

        self.initialized = True
        self.turn_number = turn_number
        self.queue = []
        self.worker_id = worker_id

        self.logger.info('GAME INITIALIZED')

        environment.workers.supervisor.cmd_answer('initialize', self.worker_id)

    def cmd_next_turn(self, turn_number):
        return self.send_cmd('next_turn', data={'turn_number': turn_number})

    # @profile.profile_decorator('/home/tie/repos/mine/the-tale/profile.info')
    def process_next_turn(self, turn_number):

        self.turn_number += 1

        if turn_number != self.turn_number:
            raise LogicException('dessinchonization: workers turn number (%d) not equal to command turn number (%d)' % (self.turn_number, turn_number))


        if TimePrototype.get_current_turn_number() != self.turn_number:
            raise LogicException('dessinchonization: workers turn number (%d) not equal to saved turn number (%d)' % (self.turn_number,
                                                                                                                      TimePrototype.get_current_turn_number()))

        self.storage.process_turn(logger=self.logger)
        self.storage.save_changed_data(logger=self.logger)

        for hero_id in self.storage.skipped_heroes:
            hero = self.storage.heroes[hero_id]
            if hero.actions.current_action.bundle_id in self.storage.ignored_bundles:
                continue
            environment.workers.supervisor.cmd_account_release_required(hero.account_id)

        environment.workers.supervisor.cmd_answer('next_turn', self.worker_id)

        if game_settings.COLLECT_GARBAGE and self.turn_number % game_settings.COLLECT_GARBAGE_PERIOD == 0:
            self.logger.info('GC: start')
            gc.collect()
            self.logger.info('GC: end')

    def release_account(self, account_id):
        if account_id not in self.storage.accounts_to_heroes:
            environment.workers.supervisor.cmd_account_released(account_id)
            return

        hero = self.storage.accounts_to_heroes[account_id]
        bundle_id = hero.actions.current_action.bundle_id

        if bundle_id in self.storage.ignored_bundles:
            return

        with self.storage.on_exception(self.logger,
                                       message='LogicWorker.process_release_account catch exception, while processing hero %d, try to save all bundles except %d',
                                       data=(hero.id, bundle_id),
                                       excluded_bundle_id=bundle_id):
            self.storage.release_account_data(account_id)
            environment.workers.supervisor.cmd_account_released(account_id)

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        # no need to save data, since they automaticaly saved on every turn
        self.initialized = False
        self.storage.save_all(logger=self.logger)
        environment.workers.supervisor.cmd_answer('stop', self.worker_id)
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
        self.release_account(account_id)

    def cmd_logic_task(self, account_id, task_id):
        return self.send_cmd('logic_task', {'task_id': task_id,
                                            'account_id': account_id})

    def process_logic_task(self, account_id, task_id): # pylint: disable=W0613
        hero = self.storage.accounts_to_heroes[account_id]
        bundle_id = hero.actions.current_action.bundle_id

        if bundle_id in self.storage.ignored_bundles:
            return

        with self.storage.on_exception(self.logger,
                                       message='LogicWorker.process_logic_task catch exception, while processing hero %d, try to save all bundles except %d',
                                       data=(hero.id, bundle_id),
                                       excluded_bundle_id=bundle_id):
            task = postponed_tasks.PostponedTaskPrototype.get_by_id(task_id)
            task.process(self.logger, storage=self.storage)
            task.do_postsave_actions()

            self.storage.recache_bundle(bundle_id)


    def cmd_force_save(self, account_id):
        return self.send_cmd('force_save', {'account_id': account_id})

    def process_force_save(self, account_id): # pylint: disable=W0613
        hero = self.storage.accounts_to_heroes[account_id]
        bundle_id = hero.actions.current_action.bundle_id
        if bundle_id in self.storage.ignored_bundles:
            return
        self.storage.save_bundle_data(bundle_id=bundle_id)

    def cmd_start_hero_caching(self, account_id):
        self.send_cmd('start_hero_caching', {'account_id': account_id})

    def process_start_hero_caching(self, account_id):
        hero = self.storage.accounts_to_heroes[account_id]

        if hero.actions.current_action.bundle_id in self.storage.ignored_bundles:
            return

        hero.ui_caching_started_at = datetime.datetime.now()
        self.storage.recache_bundle(hero.actions.current_action.bundle_id)

    def cmd_update_hero_with_account_data(self, account_id, is_fast, premium_end_at, active_end_at, ban_end_at, might, actual_bills):
        self.send_cmd('update_hero_with_account_data', {'account_id': account_id,
                                                        'is_fast': is_fast,
                                                        'premium_end_at': premium_end_at,
                                                        'active_end_at': active_end_at,
                                                        'ban_end_at': ban_end_at,
                                                        'might': might,
                                                        'actual_bills': actual_bills})

    def process_update_hero_with_account_data(self, account_id, is_fast, premium_end_at, active_end_at, ban_end_at, might, actual_bills):
        hero = self.storage.accounts_to_heroes[account_id]

        if hero.actions.current_action.bundle_id in self.storage.ignored_bundles:
            return

        hero.update_with_account_data(is_fast=is_fast,
                                      premium_end_at=datetime.datetime.fromtimestamp(premium_end_at),
                                      active_end_at=datetime.datetime.fromtimestamp(active_end_at),
                                      ban_end_at=datetime.datetime.fromtimestamp(ban_end_at),
                                      might=might,
                                      actual_bills=actual_bills)
        self.storage.save_bundle_data(hero.actions.current_action.bundle_id)

    def cmd_highlevel_data_updated(self):
        self.send_cmd('highlevel_data_updated')

    def process_highlevel_data_updated(self):
        self.storage.on_highlevel_data_updated()

    def cmd_setup_quest(self, account_id, knowledge_base):
        return self.send_cmd('setup_quest', {'account_id': account_id,
                                             'knowledge_base': knowledge_base})

    def process_setup_quest(self, account_id, knowledge_base):
        hero = self.storage.accounts_to_heroes[account_id]
        bundle_id = hero.actions.current_action.bundle_id

        if bundle_id in self.storage.ignored_bundles:
            return

        with self.storage.on_exception(self.logger,
                                       message='LogicWorker.process_logic_task catch exception, while processing hero %d, try to save all bundles except %d',
                                       data=(hero.id, bundle_id),
                                       excluded_bundle_id=bundle_id):
            quests_logic.setup_quest_for_hero(hero, knowledge_base)
            self.storage.recache_bundle(bundle_id)
