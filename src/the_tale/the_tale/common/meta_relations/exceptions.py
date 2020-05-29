
import smart_imports

smart_imports.all()


class MetaRelationsError(utils_exceptions.TheTaleError):
    pass


class DuplicateRelationError(MetaRelationsError):
    MSG = 'relation with such TYPE has been registered already: %(type)s'


class DuplicateTypeError(MetaRelationsError):
    MSG = 'type with such TYPE has been registered already: %(type)s'


class WrongTypeError(MetaRelationsError):
    MSG = 'type with such TYPE has not been registered: %(type)s'


class WrongObjectError(MetaRelationsError):
    MSG = 'object %(object)s of type %(type)s is not exist'


class WrongUIDFormatError(MetaRelationsError):
    MSG = 'wrong uid format: %(uid)s'


class WrongTagFormatError(MetaRelationsError):
    MSG = 'wrong uid format: %(tag)s'


class ObjectsNotFound(MetaRelationsError):
    MSG = 'can not find objects with type "%(type)s" and ids: "%(ids)s"'
