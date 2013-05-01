# coding: utf-8

from common.postponed_tasks.workers.refrigerator import Worker as Refrigerator

class QUEUE:
    REFRIGERATOR_MESSAGES = 'refrigerator_messages_queue'
    REFRIGERATOR_STOP = 'refrigerator_stop_queue'


class Environment(object):

    def __init__(self):
        pass

    def initialize(self):
        self.refrigerator = Refrigerator(messages_queue=QUEUE.REFRIGERATOR_MESSAGES, stop_queue=QUEUE.REFRIGERATOR_STOP)

    def deinitialize(self):
        self.refrigerator.close_queries()

    def clean_queues(self):
        self.refrigerator.clean_queues()


workers_environment = Environment()
workers_environment.initialize()
