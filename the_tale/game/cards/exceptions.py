# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError

class CardsError(TheTaleError):
    MSG = u'cards error'


class RemoveUnexistedCardError(CardsError):
    MSG = u'try to remove unexisted card: %(card)r (count: %(count)d)'
