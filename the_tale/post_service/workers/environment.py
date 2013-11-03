# coding: utf-8

from the_tale.common.amqp_queues.environment import BaseEnvironment

from the_tale.post_service.workers.message_sender import Worker as MessageSender


class Environment(BaseEnvironment):

    def initialize(self):
        self.message_sender = MessageSender(messages_queue='message_sender_messages_queue', stop_queue='message_sender_stop')


workers_environment = Environment()
