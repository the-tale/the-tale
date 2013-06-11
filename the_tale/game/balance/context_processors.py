# coding: utf-8

from game.balance import constants as c, formulas as f, enums as e


def balance(request): # pylint: disable=W0613
    return {'c': c,
            'f': f,
            'e': e}
