# -*- coding: utf-8 -*-
from celery.task import Task

class cmd(Task):

    name = 'supervisor'
    exchange = 'supervisor'
    routing_key = 'supervisor.cmd'

    def __init__(self):
        pass

    def run(self, cmd):

        if cmd == 'next_turn':
            from . import game
            game.cmd.next_turn()

        return 0

    @classmethod
    def next_turn(cls):
        t = cls.apply_async(args=['next_turn'])
        return t

