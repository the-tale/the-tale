# coding: utf-8

from common.amqp_queues.environment import BaseEnvironment

from portal.workers.long_commands import Worker as LongCommands


class Environment(BaseEnvironment):

    def initialize(self):
        self.long_commands = LongCommands(command_queue='long_commands', stop_queue='long_commands_stop')


workers_environment = Environment()
workers_environment.initialize()
