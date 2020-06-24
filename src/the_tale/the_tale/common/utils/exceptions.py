
import smart_imports

smart_imports.all()


class TheTaleError(Exception):
    MSG = NotImplemented

    def __init__(self, **kwargs):
        super().__init__(self.MSG % kwargs)
        self.arguments = kwargs


class ViewError(TheTaleError):
    MSG = 'error [%(code)s] in view: %(message)s'

    @property
    def code(self):
        return self.arguments['code']

    @property
    def http_status(self):
        http_status = self.arguments.get('http_status')

        if http_status is None:
            return relations.HTTP_STATUS.OK

        if isinstance(http_status, numbers.Integral):
            return relations.HTTP_STATUS(http_status)

        return http_status

    @property
    def message(self):
        return self.arguments['message']

    @property
    def info(self):
        return self.arguments.get('info', {})


class InternalViewError(TheTaleError):
    pass


class DuplicateViewNameError(InternalViewError):
    MSG = 'duplicate view name "%(name)s"'


class SingleNameMustBeSpecifiedError(InternalViewError):
    MSG = 'single argument name must be specified (not less, not more)'


class WrongProcessorArgumentError(InternalViewError):
    MSG = 'processor "%(processor)s" received wrong argument name "%(argument)s"'
