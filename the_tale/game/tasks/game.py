# coding: utf-8
from celery.task import Task

class cmd(Task):

    name = 'game'
    exchange = 'game'
    routing_key = 'game.cmd'

    def __init__(self):
        pass

    def run(self, cmd):

        if cmd == 'next_turn':
            from ..turns.logic import next_turn
            next_turn()

        return 0

    @classmethod
    def next_turn(cls):
        t = cls.apply_async(args=['next_turn'])
        return t



