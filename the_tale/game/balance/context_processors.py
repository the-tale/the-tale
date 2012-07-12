# coding: utf-8

from game.balance import constants as c, formulas as f, calculated as calc


def balance(request):
    return {'c': c,
            'f': f,
            'calc': calc}
