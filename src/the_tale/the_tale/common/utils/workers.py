# coding: utf-8

from dext.common import amqp_queues


class BaseWorker(amqp_queues.BaseWorker):
    LOGGER_PREFIX = 'the-tale.workers'
