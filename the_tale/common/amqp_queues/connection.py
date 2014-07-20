# coding: utf-8

import time
import socket
from Queue import Empty

from kombu import Connection as KombuConnection # pylint: disable=E0611
from kombu.simple import SimpleQueue as KombuSimpleQueue

from django.conf import settings as project_settings


class SimpleQueue(KombuSimpleQueue):

    def get(self, block=True, timeout=None):
        if self.buffer:
            return self.buffer.popleft()

        if not block:
            return self.get_nowait()

        self._consume()

        elapsed = 0.0
        remaining = timeout

        while True:
            time_start = time.time()

            if self.buffer:
                return self.buffer.popleft()

            try:
                self.channel.connection.client.drain_events(
                            timeout=timeout and remaining)
            except socket.timeout:
                raise Empty()
            elapsed += time.time() - time_start
            remaining = timeout and timeout - elapsed or None


class SimpleBuffer(SimpleQueue):
    no_ack = True
    queue_opts = dict(durable=False,
                      auto_delete=True)
    exchange_opts = dict(durable=False,
                         delivery_mode='transient',
                         auto_delete=True)


class Connection(KombuConnection):

    def create_simple_buffer(self,
                             name,
                             no_ack=None,
                             queue_opts=None,
                             exchange_opts=None,
                             channel=None,
                             **kwargs):

        # return SimpleQueue(channel or self,
        #                    name,
        #                    no_ack,
        #                    queue_opts,
        #                    exchange_opts,
        #                    **kwargs)
        return SimpleBuffer(channel or self,
                            name,
                            no_ack,
                            queue_opts,
                            exchange_opts,
                             **kwargs)


connection = Connection(project_settings.AMQP_CONNECTION_URL) # pylint: disable=C0103

connection.connect()
