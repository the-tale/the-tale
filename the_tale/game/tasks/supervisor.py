# -*- coding: utf-8 -*-
from celery.task import Task

from django_next.utils.decorators import nested_commit_on_success

from ..turns.prototypes import TurnPrototype
from ..bundles import get_bundle_by_id, get_bundle_by_model
from ..models import Bundle

class TASK_TYPE:
    NEXT_TURN = 'next_turn'
    NEW_BUNDLE = 'new_bundle'
    ACTIVATE_CARD = 'activate_card'
    REGISTER_HERO = 'register_hero'

class supervisor(Task):

    name = 'supervisor'
    exchange = 'supervisor'
    routing_key = 'supervisor.cmd'

    def __init__(self):
        print 'CONSTRUCT SUPERVISOR'
        self.initialized = False

    def initialize(self):
        self.initialized = True

        print 'INIT_SUPERVISOR'
        from .game import game
        from ..turns.prototypes import get_latest_turn
        turn = get_latest_turn()
        game.cmd_initialize(turn_number=turn.id)

        self.load_bundles()

    def load_bundles(self):
        for bundle_model in Bundle.objects.all():
            bundle = get_bundle_by_model(bundle_model)
            self.push_worker(bundle)

    def log_cmd(self, cmd, params):
        print 'supervisor: %s %r' % (cmd, params)

    def push_worker(self, bundle):
        from .game import game
        bundle.owner = 'worker'
        bundle.save()
        game.cmd_push_bundle(bundle)

    def run(self, cmd, params):

        if not self.initialized:
            self.initialize()

        from .game import game

        self.log_cmd(cmd, params)

        if cmd == TASK_TYPE.NEXT_TURN:
            game.cmd_next_turn(params['steps_delta'])
            TurnPrototype.create()

        elif cmd == TASK_TYPE.NEW_BUNDLE:
            with nested_commit_on_success():
                bundle = get_bundle_by_id(params['id'])
                self.push_worker(bundle)

        elif cmd == TASK_TYPE.ACTIVATE_CARD:
            game.cmd_activate_card(params['id'], params['data'])

        return 0

    @classmethod
    def cmd_next_turn(cls, steps_delta):
        t = cls.apply_async(args=[TASK_TYPE.NEXT_TURN, {'steps_delta': steps_delta}])
        return t

    @classmethod
    def cmd_new_bundle(cls, bundle):
        t = cls.apply_async(args=[TASK_TYPE.NEW_BUNDLE, {'id': bundle.id}])
        return t

    @classmethod
    def cmd_activate_card(cls, card, data):
        t = cls.apply_async(args=[TASK_TYPE.ACTIVATE_CARD, {'id': card.id, 'data': data}])
        return t

    @classmethod
    def cmd_register_hero(cls, hero):
        t = cls.apply_async(args=[TASK_TYPE.REGISTER_HERO, {'id': hero.id}])
        return t

    

