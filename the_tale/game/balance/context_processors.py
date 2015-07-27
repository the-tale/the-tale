# coding: utf-8

from the_tale.game.balance import constants as c, formulas as f


def balance(request): # pylint: disable=W0613
    return {'c': c,
            'f': f}
