

import smart_imports

smart_imports.all()


class CardsError(utils_exceptions.TheTaleError):
    MSG = 'cards error'


class RemoveUnexistedCardError(CardsError):
    MSG = 'try to remove unexisted card: %(card_uid)r'


class WrongNumberOfCombinedCardsError(CardsError):
    MSG = 'try to combine unexpected number of cards'


class UnknownPreference(CardsError):
    MSG = 'unknown preferece: %(preference)s'
