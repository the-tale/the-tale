# coding: utf-8
import time
import Queue

from django.utils.log import getLogger

from common.amqp_queues import connection, BaseWorker


from post_service.conf import post_service_settings


class MessageSenderException(Exception): pass

class Worker(BaseWorker):

    def __init__(self, messages_queue, stop_queue):
        super(Worker, self).__init__(logger=getLogger('post_service.workers.message_sender'), command_queue=messages_queue)
        self.stop_queue = connection.SimpleQueue(stop_queue)
        self.initialized = True

    def clean_queues(self):
        super(Worker, self).clean_queues()
        self.stop_queue.queue.purge()

    def initialize(self):
        self.logger.info('MESSAGE SENDER INITIALIZED')

    def run(self):

        while not self.exception_raised and not self.stop_required:
            try:
                cmd = self.command_queue.get_nowait()
                cmd.ack()
                self.process_cmd(cmd.payload)
            except Queue.Empty:
                self.send_messages()
                time.sleep(post_service_settings.MESSAGE_SENDER_DELAY)

    def send_messages(self):
        pass

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        self.initialized = False
        self.stop_required = True
        self.stop_queue.put({'code': 'stopped', 'worker': 'message_sender'}, serializer='json', compression=None)
        self.logger.info('MESSAGE SENDER STOPPED')
