# coding: utf-8
import heapq

from celery.task import Task

from django_next.utils.decorators import nested_commit_on_success

from ..heroes.prototypes import get_hero_by_id
from ..bundles import get_bundle_by_id

class GameException(Exception): pass

class TASK_TYPE:
    INITIALIZE = 'initialize'
    NEXT_TURN = 'next_turn'
    PUSH_BUNDLE = 'push_bundle'
    ACTIVATE_ABILITY = 'activate_ability'
    REGISTER_HERO = 'register_hero'

class game(Task):

    name = 'game'
    exchange = 'game'
    routing_key = 'game.cmd'

    def __init__(self):
        print 'CONSTRUCT GAME'
        self.initialized = False
        # self.uuid = random.randint(0, 100)
        self.exception_raised = False

    def initialize(self):
        print 'INIT GAME'
        self.initialized = True
        
        self.turn_number = 0
        self.bundles = {}
        self.queue = []
        self.angels2bundles = {}
        self.heroes2bundles = {}

    def get_angel(self, angel_id):
        return self.bundles[self.angels2bundles[angel_id]].angels[angel_id]

    def get_hero(self, hero_id):
        return self.bundles[self.heroes2bundles[hero_id]].heroes[hero_id]

    def register_bundle(self, bundle):

        if bundle.id in self.bundles:
            print 'bundle with id "%d" has already registerd in worker, probably on initialization step' % bundle.id
            return 

        self.bundles[bundle.id] = bundle
        for angel_id in bundle.angels.keys():
            self.angels2bundles[angel_id] = bundle.id
        for hero_id in bundle.heroes.keys():
            self.heroes2bundles[hero_id] = bundle.id            
        self.push_bundle(0, bundle)

    def push_bundle(self, next_turn, bundle):
        heapq.heappush(self.queue, (next_turn, bundle.id))

    def log_cmd(self, cmd, params):
        print 'game: %s %r' % (cmd, params)

    def log_task(self):
        print '---------------------'
        print self.request.id
        print self.request.taskset
        print self.request.args
        print self.request.kwargs
        print self.request.retries
        print self.request.is_eager
        print self.request.delivery_info
        print '---------------------'

    def run(self, cmd, params):

        try:

            if self.exception_raised:
                print 'skip command becouse of exception'
                return 0

            if not self.initialized:
                self.initialize()

            self.log_cmd(cmd, params)
        
            if cmd == TASK_TYPE.INITIALIZE:
                self.turn_number = params['turn_number']

            elif cmd == TASK_TYPE.NEXT_TURN:
                steps_delta = params['steps_delta']
                while steps_delta:
                    steps_delta -= 1
                    with nested_commit_on_success():
                        self.next_turn()

            elif cmd == TASK_TYPE.PUSH_BUNDLE:
                bundle = get_bundle_by_id(id=params['id'])
                self.register_bundle(bundle)

            elif cmd == TASK_TYPE.ACTIVATE_ABILITY:
                with nested_commit_on_success():
                    from ..abilities.deck import ABILITIES
                    ability = ABILITIES[params['ability_type']]
                    bundle = self.bundles[self.angels2bundles[params['form']['angel_id']]] 
                    ability.process(bundle, params['form'])
                    bundle.save()

            elif cmd == TASK_TYPE.REGISTER_HERO:
                hero = get_hero_by_id(params['hero_id'])
                bundle = self.bundles[self.angels2bundles[hero.angel_id]] 
                bundle.add_hero(hero)
                self.heroes2bundles[hero.id] = bundle
        except:
            self.exception_raised = True
            raise

        return 0
    
    def next_turn(self):
        self.turn_number += 1

        if not len(self.queue):
            return 

        while True:
            turn_number, bundle_id = self.queue[0]

            if turn_number > self.turn_number:
                break

            bundle = self.bundles[bundle_id]
            next_turn_number = bundle.process_turn(self.turn_number)

            if next_turn_number <= self.turn_number:
                raise GameException('bundle try to process itself twice on one turn')

            heapq.heappushpop(self.queue, (next_turn_number, bundle.id) )
            bundle.save()

    @classmethod
    def cmd_initialize(cls, turn_number):
        t = cls.apply_async(args=[TASK_TYPE.INITIALIZE, {'turn_number': turn_number}])
        return t

    @classmethod
    def cmd_next_turn(cls, steps_delta):
        t = cls.apply_async(args=[TASK_TYPE.NEXT_TURN, {'steps_delta': steps_delta}])
        return t

    @classmethod
    def cmd_push_bundle(cls, bundle):
        t = cls.apply_async(args=[TASK_TYPE.PUSH_BUNDLE, {'id': bundle.id}])
        return t

    @classmethod
    def cmd_activate_ability(cls, ability_type, form):
        t = cls.apply_async(args=[TASK_TYPE.ACTIVATE_ABILITY, {'ability_type': ability_type, 'form': form}])
        return t

    @classmethod
    def cmd_register_hero(cls, hero_id):
        t = cls.apply_async(args=[TASK_TYPE.REGISTER_HERO, {'hero_id': hero_id}])
        return t

