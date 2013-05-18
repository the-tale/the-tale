# coding: utf-8

from portal.workers.long_commands import Worker as LongCommands

class QUEUE:
    LONG_COMMANDS = 'long_commands'
    LONG_COMMANDS_STOP = 'long_commands_stop'


class Environment(object):

    def __init__(self):
        pass

    def initialize(self):
        self.long_commands = LongCommands(command_queue=QUEUE.LONG_COMMANDS, stop_queue=QUEUE.LONG_COMMANDS_STOP)

    def deinitialize(self):
        self.long_commands.close_queries()

    def clean_queues(self):
        self.long_commands.clean_queues()

workers_environment = Environment()
workers_environment.initialize()
