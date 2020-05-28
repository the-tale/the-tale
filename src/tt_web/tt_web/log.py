
import uuid
import logging


LOG_FORMAT = '[%(levelname)s %(asctime)s %(module)s %(process)d] %(message)s'


def initilize(config):
    root = logging.getLogger()

    root.setLevel(getattr(logging, config['level'].upper()))

    logging.basicConfig(format=LOG_FORMAT)

    logging.info('logging initialize with log level: %s', config['level'])


class ContextLogger:
    __slots__ = ('context_uid',)

    def __init__(self):
        self.context_uid = uuid.uuid4().hex

    def debug(self, *args, **kwargs):
        self._log(logging.debug, *args, **kwargs)

    def info(self, *args, **kwargs):
        self._log(logging.info, *args, **kwargs)

    def warning(self, *args, **kwargs):
        self._log(logging.warning, *args, **kwargs)

    def error(self, *args, **kwargs):
        self._log(logging.error, *args, **kwargs)

    def critical(self, *args, **kwargs):
        self._log(logging.critical, *args, **kwargs)

    def exception(self, *args, **kwargs):
        self._log(logging.exception, *args, **kwargs)

    def _log(self, callback, message, *args, **kwargs):
        callback('<{}> {}'.format(self.context_uid, message), *args, **kwargs)
