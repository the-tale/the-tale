# coding: utf-8

from django.utils.log import getLogger

from dext.settings import settings

from the_tale.common.amqp_queues import connection, BaseWorker
from the_tale.common import postponed_tasks

class RegistrationException(Exception): pass

class Worker(BaseWorker):

    logger = getLogger('the-tale.workers.accounts_registration')
    name = 'accounts registration'
    command_name = 'accounts_registration'

    def __init__(self, registration_queue, stop_queue):
        super(Worker, self).__init__(command_queue=registration_queue)
        self.stop_queue = connection.create_simple_buffer(stop_queue)
        self.initialized = True

    def clean_queues(self):
        super(Worker, self).clean_queues()
        self.stop_queue.queue.purge()

    def initialize(self):
        postponed_tasks.autodiscover()
        postponed_tasks.PostponedTaskPrototype.reset_all()
        self.logger.info('REGISTRATION INITIALIZED')

    def run(self):

        while not self.exception_raised and not self.stop_required:
            game_cmd = self.command_queue.get(block=True)
            # game_cmd.ack()

            settings.refresh()

            self.process_cmd(game_cmd.payload)

    def cmd_task(self, task_id):
        return self.send_cmd('task', {'task_id': task_id})

    def process_task(self, task_id):
        task = postponed_tasks.PostponedTaskPrototype.get_by_id(task_id)
        task.process(self.logger)
        task.save()

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        self.initialized = False
        self.stop_required = True
        self.stop_queue.put({'code': 'stopped', 'worker': 'registration'}, serializer='json', compression=None)
        self.logger.info('REGISTRATION STOPPED')
