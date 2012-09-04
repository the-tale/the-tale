# coding: utf-8

from game.balance import constants as c, formulas as f


def balance(request):
    return {'c': c,
            'f': f}
