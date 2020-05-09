
import smart_imports

smart_imports.all()


_NEXT_WORKER_NUMBER = 0


class BaseWorker(object):
    STOP_SIGNAL_REQUIRED = True
    RECEIVE_ANSWERS = False
    LOGGER_PREFIX = None
    REFRESH_SETTINGS = True
    FULL_CMD_LOG = False
    GET_CMD_TIMEOUT = 1.0
    NO_CMD_TIMEOUT = 0.0

    @classmethod
    def get_next_number(cls):
        global _NEXT_WORKER_NUMBER
        _NEXT_WORKER_NUMBER += 1
        return _NEXT_WORKER_NUMBER

    def __init__(self, name):
        self.name = name

        self.number = self.get_next_number()

        self.command_queue = connection.connection.create_simple_buffer('%s_command' % self.name, no_ack=True)
        self.stop_queue = connection.connection.create_simple_buffer('%s_stop' % self.name, no_ack=True) if self.STOP_SIGNAL_REQUIRED else None
        self.answers_queue = connection.connection.create_simple_buffer('%s_answers' % self.name, no_ack=True) if self.RECEIVE_ANSWERS else None

        self.logger = logging.getLogger('%s.%s' % (self.LOGGER_PREFIX, self.name))

        self.exception_raised = False
        self.stop_required = False
        self.initialized = False

        self.commands = {}

        self.prepair_commands_map()

    def on_sigterm(self, signal_code, frame):
        if self.logger:
            self.logger.info('SIGTERM received')

        if self.STOP_SIGNAL_REQUIRED:
            if self.logger:
                self.logger.info('set stop_required flag')
            self.stop_required = True
        else:
            if self.logger:
                self.logger.info('do not set stop_required flag: worker does not process stop signals')

    def run(self):
        from the_tale.common.settings import settings

        while not self.exception_raised and not self.stop_required:
            try:
                django_db.reset_queries()

                cmd = self.command_queue.get(block=True, timeout=self.GET_CMD_TIMEOUT)

                if self.REFRESH_SETTINGS:
                    settings.refresh()
                self.process_cmd(cmd.payload)
            except queue.Empty:
                if self.REFRESH_SETTINGS:
                    settings.refresh()
                self.process_no_cmd()
                if self.NO_CMD_TIMEOUT:
                    time.sleep(self.NO_CMD_TIMEOUT)

        self.on_stop()

        self.logger.info('loop stopped')

    def on_stop(self):
        pass

    def process_no_cmd(self):
        pass

    def close_queries(self):
        pass

    def clean_queues(self):
        self.command_queue.queue.purge()

    def prepair_commands_map(self):

        attributes = set(dir(self))

        for attribute in attributes:
            if attribute in ['process_cmd', 'cmd_answer', 'process_no_cmd']:
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

    def _prepair_cmd_data_for_log(self, data):
        if self.FULL_CMD_LOG:
            return data

        return {key: value for key, value in data.items() if not isinstance(value, dict)}

    def process_cmd(self, cmd):
        cmd_type = cmd['type']
        cmd_data = cmd['data']

        self.logger.info('<%s> %r' % (cmd_type, self._prepair_cmd_data_for_log(cmd_data)))

        if not self.initialized and cmd_type != 'initialize':
            self.logger.error('ERROR: receive cmd before initialization')
            return

        try:
            self.commands[cmd_type](**cmd_data)
        except Exception: # pylint: disable=W0703
            self.exception_raised = True
            self.logger.error('Exception in worker "%r"' % self,
                              exc_info=sys.exc_info(),
                              extra={})

    def wait_answers_from(self, code, workers=(), timeout=60.0):

        while workers:

            try:
                answer_cmd = self.answers_queue.get(block=True, timeout=timeout)
                # answer_cmd.ack()
            except queue.Empty:
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
