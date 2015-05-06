# coding: utf-8

from the_tale.common.utils.workers import BaseWorker
from the_tale.common import postponed_tasks

class RegistrationException(Exception): pass

class Worker(BaseWorker):

    def clean_queues(self):
        super(Worker, self).clean_queues()
        self.stop_queue.queue.purge()

    def initialize(self):
        self.initialized = True
        postponed_tasks.PostponedTaskPrototype.reset_all()
        self.logger.info('REGISTRATION INITIALIZED')

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
