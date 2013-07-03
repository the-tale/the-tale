# coding: utf-8

from common.amqp_queues.environment import BaseEnvironment

from post_service.workers.message_sender import Worker as MessageSender


class Environment(BaseEnvironment):

    def initialize(self):
        self.message_sender = MessageSender(messages_queue='message_sender_messages_queue', stop_queue='message_sender_stop')


workers_environment = Environment()
workers_environment.initialize()
