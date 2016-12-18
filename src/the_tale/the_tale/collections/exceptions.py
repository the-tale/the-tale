# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError


class CollectionsError(TheTaleError):
    MSG = 'collections error'


class SaveNotRegisteredCollectionError(CollectionsError):
    MSG = 'try to save collection %(collection)s not from storage'


class SaveNotRegisteredKitError(CollectionsError):
    MSG = 'try to save kit %(kit)s not from storage'


class SaveNotRegisteredItemError(CollectionsError):
    MSG = 'try to save item %(item)s not from storage'
