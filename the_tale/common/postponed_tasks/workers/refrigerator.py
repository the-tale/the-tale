# coding: utf-8

import time
import Queue
import datetime

from the_tale.common.utils.workers import BaseWorker

from the_tale.common.postponed_tasks.conf import postponed_tasks_settings
from the_tale.common.postponed_tasks.prototypes import PostponedTaskPrototype, POSTPONED_TASK_LOGIC_RESULT, autodiscover


class RefrigeratorException(Exception): pass


class Worker(BaseWorker):

    def clean_queues(self):
        super(Worker, self).clean_queues()
        self.stop_queue.queue.purge()

    def initialize(self):
        self.initialized = True
        self.next_task_process_time = datetime.datetime.now()
        self.tasks = {}
        autodiscover()
        PostponedTaskPrototype.reset_all()
        self.logger.info('REFRIGERATOR INITIALIZED')

    def run(self):

        while not self.exception_raised and not self.stop_required:
            try:
                cmd = self.command_queue.get_nowait()
                # cmd.ack()
                self.process_cmd(cmd.payload)
            except Queue.Empty:
                if self.next_task_process_time < datetime.datetime.now():
                    self.check_tasks()
                    self.next_task_process_time = datetime.datetime.now() + datetime.timedelta(seconds=postponed_tasks_settings.TASK_WAIT_DELAY)
                time.sleep(0.1)

    def check_tasks(self):

        for task in list(self.tasks.values()):
            task.process(self.logger)
            task.do_postsave_actions()

            if task.internal_result != POSTPONED_TASK_LOGIC_RESULT.WAIT:
                del self.tasks[task.id]

    def cmd_wait_task(self, task_id):
        return self.send_cmd('wait_task', {'task_id': task_id})

    def process_wait_task(self, task_id):
        self.tasks[task_id] = PostponedTaskPrototype.get_by_id(task_id)

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        self.initialized = False
        self.stop_required = True
        self.stop_queue.put({'code': 'stopped', 'worker': 'refrigerator'}, serializer='json', compression=None)
        self.logger.info('REFRIGERATOR STOPPED')
