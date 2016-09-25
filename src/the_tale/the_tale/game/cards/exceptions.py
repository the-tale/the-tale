# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError

class CardsError(TheTaleError):
    MSG = u'cards error'


class RemoveUnexistedCardError(CardsError):
    MSG = u'try to remove unexisted card: %(card_uid)r'

class HelpCountBelowZero(CardsError):
    MSG = u'try decrease help count below zero (current_value: %(current_value)d, delta: %(delta)d)'
