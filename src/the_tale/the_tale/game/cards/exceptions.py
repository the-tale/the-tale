
from the_tale.common.utils.exceptions import TheTaleError


class CardsError(TheTaleError):
    MSG = 'cards error'


class RemoveUnexistedCardError(CardsError):
    MSG = 'try to remove unexisted card: %(card_uid)r'


class WrongNumberOfCombinedCardsError(CardsError):
    MSG = 'try to combine unexpected number of cards'


class UnknownPreference(CardsError):
    MSG = 'unknown preferece: %(preference)s'
