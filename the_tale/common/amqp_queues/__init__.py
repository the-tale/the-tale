# coding: utf-8

from common.amqp_queues.connection import connection
from common.amqp_queues.workers import BaseWorker

__all__ = ['connection', 'BaseWorker']
