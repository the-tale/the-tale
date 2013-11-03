# coding: utf-8

import sys
import Queue

from the_tale.common.amqp_queues import exceptions
from the_tale.common.amqp_queues.connection import connection
from django.conf import settings as project_settings

def run_with_newrelic(method, method_data):
    import newrelic.agent

    application = newrelic.agent.application()
    name = newrelic.agent.callable_name(method)

    with newrelic.agent.BackgroundTask(application, name):
        return method(**method_data)


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

    def run_simple(self):
        while not self.exception_raised and not self.stop_required:
            cmd = self.command_queue.get(block=True)
            cmd.ack()
            self.process_cmd(cmd.payload)

    def close_queries(self):
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
                    raise exceptions.NoCmdMethodError(method=cmd_name)

            if attribute.startswith('cmd_'):
                cmd_name = attribute[4:]
                if ('process_%s' % cmd_name) not in attributes:
                    raise exceptions.NoProcessMethodError(method=cmd_name)


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
            cmd = self.commands[cmd_type]

            if project_settings.NEWRELIC_ENABLED:
                run_with_newrelic(cmd, cmd_data)
            else:
                cmd(**cmd_data)
        except Exception: # pylint: disable=W0703
            self.exception_raised = True
            self.logger.error('Exception in worker "%r"' % self,
                              exc_info=sys.exc_info(),
                              extra={} )

    def wait_answers_from(self, code, workers=(), timeout=60.0):

        while workers:

            try:
                answer_cmd = self.answers_queue.get(block=True, timeout=timeout)
                answer_cmd.ack()
            except Queue.Empty:
                raise exceptions.WaitAnswerTimeoutError(code=code, workers=workers, timeout=timeout)

            cmd = answer_cmd.payload

            if cmd['code'] == code:
                worker_id = cmd['worker']
                if worker_id in workers:
                    workers.remove(worker_id)
                else:
                    raise exceptions.UnexpectedAnswerError(cmd=cmd)
            else:
                raise exceptions.WrongAnswerError(cmd=cmd, workers=workers)

    def cmd_answer(self, code, worker):
        self.answers_queue.put({'code': code, 'worker': worker}, serializer='json', compression=None)
