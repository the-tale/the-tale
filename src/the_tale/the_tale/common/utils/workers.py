
import smart_imports

smart_imports.all()


class BaseWorker(amqp_queues_workers.BaseWorker):
    LOGGER_PREFIX = 'the-tale'
