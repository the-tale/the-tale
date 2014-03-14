# coding: utf-8
import time
import Queue
import datetime

from django.utils.log import getLogger

from dext.settings import settings

from the_tale.common.amqp_queues import connection, BaseWorker

from the_tale.post_service.prototypes import MessagePrototype
from the_tale.post_service.conf import post_service_settings


class MessageSenderException(Exception): pass

class Worker(BaseWorker):

    logger = getLogger('the-tale.workers.post_service_message_sender')
    name = 'message sender'
    command_name = 'post_service_message_sender'

    def __init__(self, messages_queue, stop_queue):
        super(Worker, self).__init__(command_queue=messages_queue)
        self.stop_queue = connection.SimpleQueue(stop_queue)

    def clean_queues(self):
        super(Worker, self).clean_queues()
        self.stop_queue.queue.purge()

    def initialize(self):
        self.initialized = True
        self.next_message_process_time = datetime.datetime.now()
        self.logger.info('MESSAGE SENDER INITIALIZED')

    def run(self):

        while not self.exception_raised and not self.stop_required:
            try:
                cmd = self.command_queue.get_nowait()
                # cmd.ack()
                self.process_cmd(cmd.payload)
            except Queue.Empty:
                if self.next_message_process_time < datetime.datetime.now():
                    if not self.send_message(MessagePrototype.get_priority_message()):
                        self.next_message_process_time = datetime.datetime.now() + datetime.timedelta(seconds=post_service_settings.MESSAGE_SENDER_DELAY)
                time.sleep(1.0)

    def send_message(self, message):

        settings.refresh()

        if message is None:
            return False

        if (not post_service_settings.ENABLE_MESSAGE_SENDER or
            (settings.get(post_service_settings.SETTINGS_ALLOWED_KEY) is None and
             message.handler.settings_type_uid not in settings.get(post_service_settings.SETTINGS_FORCE_ALLOWED_KEY, ''))):
            self.logger.info('skip message %s' % message.uid)
            message.skip()
            return True

        self.logger.info('process message %s' % message.uid)

        message.process()

        if message.state.is_PROCESSED:
            self.logger.info('message %s status %s' % (message.uid, message.state))
        else:
            self.logger.error('message %s status %s ' % (message.uid, message.state))

        return True

    def cmd_send_now(self, message_id):
        return self.send_cmd('send_now', {'message_id': message_id})

    def process_send_now(self, message_id):
        self.send_message(MessagePrototype.get_by_id(message_id))

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        self.initialized = False
        self.stop_required = True
        self.stop_queue.put({'code': 'stopped', 'worker': 'message_sender'}, serializer='json', compression=None)
        self.logger.info('MESSAGE SENDER STOPPED')
