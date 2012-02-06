# coding: utf-8

from kombu import BrokerConnection

from django.conf import settings as project_settings

from .supervisor import Worker as Supervisor
from .logic import Worker as Logic
from .highlevel import Worker as Highlevel

class QUEUE:
    GAME = 'game_queue'
    SUPERVISOR = 'supervisor_queue'
    SUPERVISOR_ANSWERS = 'answers_queue'
    HIGHLEVEL = 'highlevel_queue'
    STOP = 'stop'

class Environment(object):

    def __init__(self):
        pass

    def initialize(self):
        self.connection = BrokerConnection(project_settings.AMQP_CONNECTION_URL)

        self.connection.connect()

        self.logic = Logic(connection=self.connection, game_queue=QUEUE.GAME)
        self.supervisor = Supervisor(connection=self.connection, 
                                     supervisor_queue=QUEUE.SUPERVISOR, 
                                     answers_queue=QUEUE.SUPERVISOR_ANSWERS,
                                     stop_queue=QUEUE.STOP)
        self.highlevel = Highlevel(connection=self.connection, highlevel_queue=QUEUE.HIGHLEVEL)

        self.logic.set_supervisor_worker(self.supervisor)
        self.highlevel.set_supervisor_worker(self.supervisor)

        self.supervisor.set_logic_worker(self.logic)
        self.supervisor.set_highlevel_worker(self.highlevel)

    def deinitialize(self):
        self.supervisor.close_queries()
        self.logic.close_queries()
        self.connection.close()

    def clean_queues(self):
        self.logic.clean_queues()
        self.highlevel.clean_queues()
        self.supervisor.clean_queues()


workers_environment = Environment()
workers_environment.initialize()
