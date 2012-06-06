# coding: utf-8

from django.utils.log import getLogger

from common.amqp_queues import connection, BaseWorker

class RegistrationException(Exception): pass

class Worker(BaseWorker):

    def __init__(self, registration_queue, stop_queue):
        super(Worker, self).__init__(logger=getLogger('accounts.workers.registration'), command_queue=registration_queue)
        self.stop_queue = connection.SimpleQueue(stop_queue)

        self.initialized = True

    def clean_queues(self):
        self.registration_queue.queue.purge()

    def run(self):

        while not self.exception_raised and not self.stop_required:
            game_cmd = self.command_queue.get(block=True)
            game_cmd.ack()
            self.process_game_cmd(game_cmd.payload)

    def cmd_register(self):
        return self.send_cmd('register')

    def process_register(self):
        pass

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        self.stop_required = True
        self.stop_queue.put({'code': 'stopped', 'worker': 'registration'}, serializer='json', compression=None)
        self.logger.info('REGISTRATION STOPPED')
