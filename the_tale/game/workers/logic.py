# coding: utf-8
import heapq

from django.utils.log import getLogger
from django.conf import settings as project_settings

from dext.utils.decorators import nested_commit_on_success

from common.amqp_queues import BaseWorker

from game.heroes.prototypes import get_hero_by_id
from game.bundles import get_bundle_by_id


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
        self.angels2bundles = {}
        self.heroes2bundles = {}
        self.worker_id = worker_id

        self.logger.info('GAME INITIALIZED')

        self.supervisor_worker.cmd_answer('initialize', self.worker_id)

    def cmd_next_turn(self, turn_number):
        return self.send_cmd('next_turn', data={'turn_number': turn_number})

    def process_next_turn(self, turn_number):
        from game.logic import log_sql_queries

        with nested_commit_on_success():
            self.turn_number += 1

            if turn_number != self.turn_number:
                raise LogicException('dessinchonization: workers turn number (%d) not equal to command turn number (%d)' % (self.turn_number, turn_number))

            while self.queue:
                turn_number, bundle_id = self.queue[0]

                if turn_number > self.turn_number:
                    break

                bundle = self.bundles[bundle_id]
                next_turn_number = bundle.process_turn(self.turn_number)

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
        self.logger.info('GAME STOPPED')

    def cmd_register_bundle(self, bundle_id):
        return self.send_cmd('register_bundle', {'bundle_id': bundle_id})

    def process_register_bundle(self, bundle_id):
        bundle = get_bundle_by_id(id=bundle_id)

        if bundle.id in self.bundles:
            self.logger.warn('WARNING: bundle with id "%d" has already registerd in worker, probably on initialization step' % bundle.id)
            return

        self.bundles[bundle.id] = bundle

        for angel_id in bundle.angels.keys():
            self.angels2bundles[angel_id] = bundle.id

        for hero_id in bundle.heroes.keys():
            self.heroes2bundles[hero_id] = bundle.id

        heapq.heappush(self.queue, (0, bundle_id))


    def cmd_activate_ability(self, ability_task_id):
        return self.send_cmd('activate_ability', {'ability_task_id': ability_task_id})

    def process_activate_ability(self, ability_task_id):
        with nested_commit_on_success():
            from ..abilities.prototypes import AbilityTaskPrototype

            task = AbilityTaskPrototype.get_by_id(ability_task_id)
            bundle = self.bundles[self.angels2bundles[task.angel_id]]
            task.process(bundle, self.turn_number)
            task.save()
            bundle.save_data()


    def cmd_register_hero(self, hero_id):
        return self.send_cmd('register_hero', {'hero_id': hero_id})

    def process_register_hero(self, hero_id):
        hero = get_hero_by_id(hero_id)
        bundle = self.bundles[self.angels2bundles[hero.angel_id]]
        bundle.add_hero(hero)
        self.heroes2bundles[hero.id] = bundle


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
