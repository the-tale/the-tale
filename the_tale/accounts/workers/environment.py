# coding: utf-8

from accounts.workers.registration import Worker as Registration


class QUEUE:
    REGISTRATION = 'registration_queue'
    REGISTRATION_STOP = 'registration_queue_stop'


class Environment(object):

    def __init__(self):
        pass

    def initialize(self):
        self.registration = Registration(registration_queue=QUEUE.REGISTRATION, stop_queue=QUEUE.REGISTRATION_STOP)

    def deinitialize(self):
        self.registration.close_queries()

    def clean_queues(self):
        self.registration.clean_queues()


workers_environment = Environment()
workers_environment.initialize()
