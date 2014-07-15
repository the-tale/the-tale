# coding: utf-8

from the_tale.common.amqp_queues.environment import BaseEnvironment

from the_tale.portal.workers.long_commands import Worker as LongCommands


class Environment(BaseEnvironment):

    def initialize(self):
        self.long_commands = LongCommands(command_queue='portal_long_commands', stop_queue='portal_long_commands_stop')


workers_environment = Environment()
