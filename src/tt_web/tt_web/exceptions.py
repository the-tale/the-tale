
class BaseError(Exception):
    MESSAGE = None

    def __init__(self, **kwargs):
        super(BaseError, self).__init__(self.MESSAGE.format(**kwargs))
        self.arguments = kwargs


class ApiError(BaseError):
    MESSAGE = 'error [{code}] in view: {message}'

    @property
    def code(self): return self.arguments['code']

    @property
    def message(self): return self.arguments['message']

    @property
    def details(self): return self.arguments.get('details', {})


class SyncPointTimeoutError(BaseError):
    MESSAGE = 'timeout {timeout} while locking key "{key}"'
