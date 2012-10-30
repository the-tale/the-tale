# coding: utf-8
import heapq
import datetime

from dext.settings import settings

from django.utils.log import getLogger
from django.conf import settings as project_settings

from dext.utils.decorators import nested_commit_on_success

from common.amqp_queues import BaseWorker

from game.bundles import BundlePrototype
from game.prototypes import TimePrototype


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

        self.initialized = True
        self.turn_number = turn_number
        self.bundles = {}
        self.queue = []
        self.heroes2bundles = {}
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
                raise LogicException('dessinchonization: workers turn number (%d) not equal to saved turn number (%d)' % (self.turn_number, TimePrototype.get_current_turn_number()))

            while self.queue:
                turn_number, bundle_id = self.queue[0]

                if turn_number > self.turn_number:
                    break

                bundle = self.bundles[bundle_id]
                next_turn_number = bundle.process_turn()

                if next_turn_number <= self.turn_number:
                    raise LogicException('bundle try to process itself twice on one turn')

                heapq.heappushpop(self.queue, (next_turn_number, bundle.id) )
                bundle.save_data()

        if project_settings.DEBUG_DATABASE_USAGE:
            log_sql_queries(turn_number)

        self.supervisor_worker.cmd_answer('next_turn', self.worker_id)

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        # no need to save bundles, since they automaticaly saved on every turn
        self.initialized = False
        self.supervisor_worker.cmd_answer('stop', self.worker_id)
        self.stop_required = True
        self.logger.info('LOGIC STOPPED')

    def cmd_register_bundle(self, bundle_id):
        return self.send_cmd('register_bundle', {'bundle_id': bundle_id})

    def process_register_bundle(self, bundle_id):
        from accounts.prototypes import AccountPrototype

        bundle = BundlePrototype.get_by_id(bundle_id)

        if bundle.id in self.bundles:
            self.logger.warn('WARNING: bundle with id "%d" has already registerd in worker, probably on initialization step' % bundle.id)
            return

        self.bundles[bundle.id] = bundle

        # update info about fast accounts
        for hero_id, hero in bundle.heroes.items():
            self.heroes2bundles[hero_id] = bundle.id
            hero.is_fast = AccountPrototype.get_by_id(hero.account_id).is_fast

        heapq.heappush(self.queue, (0, bundle_id))


    def cmd_activate_ability(self, ability_task_id):
        return self.send_cmd('activate_ability', {'ability_task_id': ability_task_id})

    def process_activate_ability(self, ability_task_id):
        with nested_commit_on_success():
            from ..abilities.prototypes import AbilityTaskPrototype

            task = AbilityTaskPrototype.get_by_id(ability_task_id)
            bundle = self.bundles[self.heroes2bundles[task.hero_id]]
            task.process(bundle)
            bundle.save_data() # just to enshure, that if syddenly transaction will be removed, bundle will be saved before task
            task.save()


    def cmd_choose_hero_ability(self, ability_task_id):
        self.send_cmd('choose_hero_ability', {'ability_task_id': ability_task_id})


    def process_choose_hero_ability(self, ability_task_id):
        with nested_commit_on_success():
            from ..heroes.prototypes import ChooseAbilityTaskPrototype

            task = ChooseAbilityTaskPrototype.get_by_id(ability_task_id)

            bundle = self.bundles[self.heroes2bundles[task.hero_id]]

            task.process(bundle)
            task.save()
            bundle.save_data()

    def cmd_choose_hero_preference(self, preference_task_id):
        self.send_cmd('choose_hero_preference', {'preference_task_id': preference_task_id})


    def process_choose_hero_preference(self, preference_task_id):
        with nested_commit_on_success():
            from ..heroes.preferences import ChoosePreferencesTaskPrototype

            task = ChoosePreferencesTaskPrototype.get_by_id(preference_task_id)

            bundle = self.bundles[self.heroes2bundles[task.hero_id]]

            task.process(bundle)
            task.save()
            bundle.save_data()

    def cmd_mark_hero_as_not_fast(self, hero_id):
        self.send_cmd('mark_hero_as_not_fast', {'hero_id': hero_id})

    def process_mark_hero_as_not_fast(self, hero_id):
        self.bundles[self.heroes2bundles[hero_id]].heroes[hero_id].is_fast = False

    def cmd_mark_hero_as_active(self, hero_id):
        self.send_cmd('mark_hero_as_active', {'hero_id': hero_id})

    def process_mark_hero_as_active(self, hero_id):
        self.bundles[self.heroes2bundles[hero_id]].heroes[hero_id].mark_as_active()

    def cmd_highlevel_data_updated(self):
        self.send_cmd('highlevel_data_updated')

    def process_highlevel_data_updated(self):
        settings.refresh()

        for bundle in self.bundles.values():
            bundle.on_highlevel_data_updated()

    def cmd_set_might(self, hero_id, might):
        self.send_cmd('set_might', {'hero_id': hero_id, 'might': might})

    def process_set_might(self, hero_id, might):
        bundle = self.bundles[self.heroes2bundles[hero_id]]

        hero = bundle.heroes[hero_id]
        hero.might = might
        hero.might_updated_time = datetime.datetime.now()
        hero.save()
