
import smart_imports

smart_imports.all()


class CollectionsError(utils_exceptions.TheTaleError):
    MSG = 'collections error'


class SaveNotRegisteredCollectionError(CollectionsError):
    MSG = 'try to save collection %(collection)s not from storage'


class SaveNotRegisteredKitError(CollectionsError):
    MSG = 'try to save kit %(kit)s not from storage'


class SaveNotRegisteredItemError(CollectionsError):
    MSG = 'try to save item %(item)s not from storage'
