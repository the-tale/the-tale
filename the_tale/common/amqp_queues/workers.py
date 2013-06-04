# coding: utf-8

import sys

from common.amqp_queues.exceptions import AmqpQueueException
from common.amqp_queues.connection import connection

class BaseWorker(object):

    logger = None
    name = None
    command_name = None
    stop_signal_required = True

    def __init__(self, command_queue):
        self.command_queue = connection.SimpleQueue(command_queue)

        self.exception_raised = False
        self.stop_required = False
        self.initialized = False

        self.commands = {}

        self.prepair_commands_map()

    @property
    def pid(self): return self.command_name

    def close_queries(self):
        # TODO: implement
        pass

    def clean_queues(self):
        self.command_queue.queue.purge()

    def prepair_commands_map(self):

        attributes = set(dir(self))

        for attribute in attributes:
            if attribute in ['process_cmd', 'cmd_answer']:
                continue

            if attribute.startswith('process_'):
                cmd_name = attribute[8:]
                if ('cmd_%s' % cmd_name) in attributes:
                    self.commands[cmd_name] = getattr(self, attribute)
                else:
                    raise AmqpQueueException('method "%s" specified without appropriate cmd_* method')

            if attribute.startswith('cmd_'):
                cmd_name = attribute[4:]
                if ('process_%s' % cmd_name) not in attributes:
                    raise AmqpQueueException('method "%s" specified without appropriate process_* method')


    def send_cmd(self, tp, data=None):
        self.command_queue.put({'type': tp, 'data': data if data else {}}, serializer='json', compression=None)


    def process_cmd(self, cmd):
        cmd_type = cmd['type']
        cmd_data = cmd['data']

        self.logger.info('<%s> %r' % (cmd_type, cmd_data))

        if not self.initialized and cmd_type != 'initialize':
            self.logger.error('ERROR: receive cmd before initialization')
            return

        try:
            self.commands[cmd_type](**cmd_data)
        except Exception: # pylint: disable=W0703
            self.exception_raised = True
            self.logger.error('Exception in worker "%r"' % self,
                              exc_info=sys.exc_info(),
                              extra={} )

    def wait_answers_from(self, code, workers=()):

        while workers:

            answer_cmd = self.answers_queue.get(block=True)
            answer_cmd.ack()

            cmd = answer_cmd.payload

            if cmd['code'] == code:
                worker_id = cmd['worker']
                if worker_id in workers:
                    workers.remove(worker_id)
                else:
                    raise AmqpQueueException('unexpected unswer from worker: %r' % cmd)
            else:
                raise AmqpQueueException('wrong answer: %r, expected answers from %r' % (cmd, workers))

    def cmd_answer(self, code, worker):
        self.answers_queue.put({'code': code, 'worker': worker}, serializer='json', compression=None)
