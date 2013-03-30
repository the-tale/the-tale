# coding: utf-8

from post_service.workers.registration import Worker as MessageSender

class QUEUE:
    MESSAGE_SENDER_MESSAGES = 'message_sender_messages_queue'
    MESSAGE_SENDER_STOP = 'message_sender_stop'


class Environment(object):

    def __init__(self):
        pass

    def initialize(self):
        self.message_sender = MessageSender(messages_queue=QUEUE.MESSAGE_SENDER_MESSAGES_QUEUE, stop_queue=QUEUE.MESSAGE_SENDER_STOP)

    def deinitialize(self):
        self.message_sender.close_queries()

    def clean_queues(self):
        self.message_sender.clean_queues()


workers_environment = Environment()
workers_environment.initialize()
