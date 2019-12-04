
import smart_imports

smart_imports.all()


class Workers(object):

    def __init__(self):
        pass

    def __iter__(self):
        return (worker
                for worker in self.__dict__.values()
                if isinstance(worker, workers.BaseWorker))

    def get_by_name(self, name):
        for worker in self.__dict__.values():
            if isinstance(worker, workers.BaseWorker) and worker.name == name:
                    return worker
        return None


class BaseEnvironment(object):

    def __init__(self):
        self.initialized = False
        self.initializing = False
        self._workers = Workers()

    @property
    def workers(self):

        if not self.initialized and not self.initializing:
            self.initializing = True
            self.initialize()
            self.initializing = False

        return self._workers

    def initialize(self):
        self.initialized = True

    def deinitialize(self):
        self.initialized = False


def get_environment():
    module = importlib.import_module(conf.settings.ENVIRONMENT_MODULE)
    return module.environment
