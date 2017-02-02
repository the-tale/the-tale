
import logging


LOG_FORMAT = '[%(levelname)s %(asctime)s %(module)s %(process)d] %(message)s'


def initilize(config):
    root = logging.getLogger()

    root.setLevel(getattr(logging, config['level'].upper()))

    logging.basicConfig(format=LOG_FORMAT)
