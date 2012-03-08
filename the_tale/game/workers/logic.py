# coding: utf-8
import heapq
import traceback

from dext.utils.decorators import nested_commit_on_success

from ..heroes.prototypes import get_hero_by_id
from ..bundles import get_bundle_by_id

class CMD_TYPE:
    INITIALIZE = 'initialize'
    NEXT_TURN = 'next_turn'
    REGISTER_BUNDLE = 'register_bundle'
    ACTIVATE_ABILITY = 'activate_ability'
    REGISTER_HERO = 'register_hero'
    CHOOSE_HERO_ABILITY = 'choose_hero_ability'
    STOP = 'stop'

class LogicException(Exception): pass

class Worker(object):

    def __init__(self, connection, game_queue):
        self.game_queue = connection.SimpleQueue(game_queue)
        self.exception_raised = False
        self.stop_required = False
        self.initialized = False
        print 'GAME CONSTRUCTED'

    def set_supervisor_worker(self, supervisor_worker):
        self.supervisor_worker = supervisor_worker

    def close_queries(self):
        # self.game_queue.close()
        pass

    def clean_queues(self):
        self.game_queue.queue.purge()

    def run(self):

        while not self.exception_raised and not self.stop_required:
            cmd = self.game_queue.get(block=True)
            cmd.ack()
            self.process_cmd(cmd.payload)

    def process_cmd(self, cmd):
        cmd_type = cmd['type']
        cmd_data = cmd['data']

        print '<%s> %r' % (cmd_type, cmd_data)

        if not self.initialized and cmd_type != CMD_TYPE.INITIALIZE:
            print 'ERROR: receive cmd before initialization'
            return

        try:
            { CMD_TYPE.INITIALIZE: self.process_initialize,
              CMD_TYPE.NEXT_TURN: self.process_next_turn,
              CMD_TYPE.REGISTER_BUNDLE: self.process_register_bundle,
              CMD_TYPE.ACTIVATE_ABILITY: self.process_activate_ability,
              CMD_TYPE.REGISTER_HERO: self.process_register_hero,
              CMD_TYPE.CHOOSE_HERO_ABILITY: self.process_choose_hero_ability,
              CMD_TYPE.STOP: self.process_stop}[cmd_type](**cmd_data)
        except Exception, e:
            self.exception_raised = True
            print 'EXCEPTION: %s' % e
            traceback.print_exc()


    def send_cmd(self, tp, data={}):
        self.game_queue.put({'type': tp, 'data': data}, serializer='json', compression=None)

    def cmd_initialize(self, turn_number, worker_id):
        self.send_cmd(CMD_TYPE.INITIALIZE, {'turn_number': turn_number, 'worker_id': worker_id})

    def process_initialize(self, turn_number, worker_id):

        if self.initialized:
            print 'WARNING: game already initialized, do reinitialization'

        self.initialized = True
        self.turn_number = turn_number
        self.bundles = {}
        self.queue = []
        self.angels2bundles = {}
        self.heroes2bundles = {}
        self.worker_id = worker_id

        print 'GAME INITIALIZED'

        self.supervisor_worker.cmd_answer('initialize', self.worker_id)

    def cmd_next_turn(self, turn_number):
        return self.send_cmd(CMD_TYPE.NEXT_TURN, data={'turn_number': turn_number})

    def process_next_turn(self, turn_number):
        with nested_commit_on_success():
            self.turn_number += 1

            if turn_number != self.turn_number:
                raise LogicException('dessinchonization: workers turn number (%d) not equal to command turn number (%d)' % (self.turn_number, turn_number))

            if not len(self.queue):
                return 

            while True:
                turn_number, bundle_id = self.queue[0]

                if turn_number > self.turn_number:
                    break

                bundle = self.bundles[bundle_id]
                next_turn_number = bundle.process_turn(self.turn_number)

                if next_turn_number <= self.turn_number:
                    raise LogicException('bundle try to process itself twice on one turn')

                heapq.heappushpop(self.queue, (next_turn_number, bundle.id) )
                bundle.save_data()

        self.supervisor_worker.cmd_answer('next_turn', self.worker_id)

    def cmd_stop(self):
        return self.send_cmd(CMD_TYPE.STOP)

    def process_stop(self):
        # no need to save bundles, since they automaticaly saved on evety turn
        self.initialized = False
        self.supervisor_worker.cmd_answer('stop', self.worker_id)

    def cmd_register_bundle(self, bundle_id):
        return self.send_cmd(CMD_TYPE.REGISTER_BUNDLE, {'bundle_id': bundle_id})

    def process_register_bundle(self, bundle_id):
        bundle = get_bundle_by_id(id=bundle_id)

        if bundle.id in self.bundles:
            print 'WARNING: bundle with id "%d" has already registerd in worker, probably on initialization step' % bundle.id
            return 

        self.bundles[bundle.id] = bundle

        for angel_id in bundle.angels.keys():
            self.angels2bundles[angel_id] = bundle.id

        for hero_id in bundle.heroes.keys():
            self.heroes2bundles[hero_id] = bundle.id            

        heapq.heappush(self.queue, (0, bundle_id))


    def cmd_activate_ability(self, ability_task_id):
        return self.send_cmd(CMD_TYPE.ACTIVATE_ABILITY, {'ability_task_id': ability_task_id})

    def process_activate_ability(self, ability_task_id):
        with nested_commit_on_success():
            from ..abilities.prototypes import AbilityTaskPrototype
            
            task = AbilityTaskPrototype.get_by_id(ability_task_id)
            bundle = self.bundles[self.angels2bundles[task.angel_id]]
            task.process(bundle, self.turn_number)
            task.save()
            bundle.save_data()


    def cmd_register_hero(self, hero_id):
        return self.send_cmd(CMD_TYPE.REGISTER_HERO, {'hero_id': hero_id})

    def process_register_hero(self, hero_id):
        hero = get_hero_by_id(hero_id)
        bundle = self.bundles[self.angels2bundles[hero.angel_id]] 
        bundle.add_hero(hero)
        self.heroes2bundles[hero.id] = bundle


    def cmd_choose_hero_ability(self, ability_task_id):
        self.send_cmd(CMD_TYPE.CHOOSE_HERO_ABILITY, {'ability_task_id': ability_task_id})


    def process_choose_hero_ability(self, ability_task_id):
        with nested_commit_on_success():
            from ..heroes.prototypes import ChooseAbilityTaskPrototype
            
            task = ChooseAbilityTaskPrototype.get_by_id(ability_task_id)

            bundle = self.bundles[self.heroes2bundles[task.hero_id]]

            task.process(bundle)
            task.save()
            bundle.save_data()

