from tt_web import exceptions


class DataProtectorError(exceptions.BaseError):
    pass


class CanNotConstructPlugin(DataProtectorError):
    MESSAGE = 'Can not construct plugin, error: {exception}'
