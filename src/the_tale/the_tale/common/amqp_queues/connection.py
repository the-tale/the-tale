
import smart_imports

smart_imports.all()


class SimpleQueue(kombu_simple.SimpleQueue):

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
                raise queue.Empty()
            elapsed += time.time() - time_start
            remaining = timeout and timeout - elapsed or None


class SimpleBuffer(SimpleQueue):
    no_ack = True
    queue_opts = dict(durable=False,
                      auto_delete=False)
    exchange_opts = dict(durable=False,
                         delivery_mode='transient',
                         auto_delete=False)


class Connection(kombu.Connection):

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


def __getattr__(name):
    # code is disabled due to moving the game to readonly mode
    return None

    if name != 'connection':
        raise AttributeError(f"module {__name__} has no attribute {name}")

    connection = Connection(django_settings.AMQP_CONNECTION_URL)  # pylint: disable=C0103

    connection.connect()

    return connection
