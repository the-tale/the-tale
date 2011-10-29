# -*- coding: utf-8 -*-
from celery.task import Task

from django_next.utils.decorators import nested_commit_on_success
from django.conf import settings as project_settings

from ..prototypes import get_current_time
from ..bundles import get_bundle_by_id, get_bundle_by_model
from ..models import Bundle

class TASK_TYPE:
    NEXT_TURN = 'next_turn'
    NEW_BUNDLE = 'new_bundle'
    ACTIVATE_ABILITY = 'activate_ability'
    REGISTER_HERO = 'register_hero'

class supervisor(Task):

    name = 'supervisor'
    exchange = 'supervisor'
    routing_key = 'supervisor.cmd'

    def __init__(self):
        print 'CONSTRUCT SUPERVISOR'
        self.initialized = False
        self.time = get_current_time()

    def initialize(self):
        self.initialized = True

        print 'INIT_SUPERVISOR'
        from .game import game
        game.cmd_initialize(turn_number=self.time.turn_number)

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
            self.time.increment_turn()
            self.time.save()

        elif cmd == TASK_TYPE.NEW_BUNDLE:
            print nested_commit_on_success()
            with nested_commit_on_success():
                bundle = get_bundle_by_id(params['id'])
                self.push_worker(bundle)

        elif cmd == TASK_TYPE.ACTIVATE_ABILITY:
            game.cmd_activate_ability(params['ability_type'], params['form'])

        elif cmd == TASK_TYPE.REGISTER_HERO:
            game.cmd_register_hero(params['hero_id'])

        return 0

    @classmethod
    def _do_task(cls, cmd, args):
        return cls.apply_async(args=[cmd, args])

    @classmethod
    def cmd_next_turn(cls, steps_delta):
        return cls._do_task(TASK_TYPE.NEXT_TURN, {'steps_delta': steps_delta})

    @classmethod
    def cmd_new_bundle(cls, bundle_id):
        return cls._do_task(TASK_TYPE.NEW_BUNDLE, {'id': bundle_id})

    @classmethod
    def cmd_activate_ability(cls, ability_type, form):
        return cls._do_task(TASK_TYPE.ACTIVATE_ABILITY, {'ability_type': ability_type, 'form': form})

    @classmethod
    def cmd_register_hero(cls, hero_id):
        return cls._do_task(TASK_TYPE.REGISTER_HERO, {'hero_id': hero_id})

    

