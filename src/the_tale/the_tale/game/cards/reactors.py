
from the_tale.game import relations as game_relations


class BaseReactor:
    __slots__ = ('own_card_type',)

    def __init__(self):
        self.own_card_type = None


    def initialize(self, own_card_type):
        self.own_card_type = own_card_type


    def descrption(self):
        return None


    def check_types(self, cards):
        return all(card.type == self.own_card_type for card in cards)


    def check_data_equality(self, cards):
        return all(card.data == cards[0].data for card in cards)


    def combine(self, combined_cards):
        raise NotImplementedError


class AutoNextCardReactor(BaseReactor):
    __slots__ = ('next_card_type',)

    def __init__(self):
        self.next_card_type = None


    def initialize(self, **kwargs):
        from . import cards
        super().initialize(**kwargs)

        for card in cards.CARD.records:
            if self.own_card_type.effect.__class__ == card.effect.__class__ and self.own_card_type.rarity.value == card.rarity.value - 1:
                self.next_card_type = card
                break


class Simple3(AutoNextCardReactor):
    __slots__ = ()

    def descrption(self):
        return '3 x «{}» => «{}»'.format(self.own_card_type.text, self.next_card_type.text)


    def combine(self, combined_cards):
        if len(combined_cards) != 3:
            return None

        if not self.check_types(combined_cards):
            return None

        return self.next_card_type.effect.create_card(available_for_auction=all(card.available_for_auction for card in combined_cards),
                                                      type=self.next_card_type)


class Special3(BaseReactor):
    __slots__ = ('next_card_type_name',)

    def __init__(self, next_card_type_name):
        super().__init__()
        self.next_card_type_name = next_card_type_name


    @property
    def next_card_type(self):
        from . import cards
        return getattr(cards.CARD, self.next_card_type_name)


    def descrption(self):
        return '3 x «{}» => «{}»'.format(self.own_card_type.text, self.next_card_type.text)


    def combine(self, combined_cards):
        if len(combined_cards) != 3:
            return None

        if not self.check_types(combined_cards):
            return None

        return self.next_card_type.effect.create_card(available_for_auction=all(card.available_for_auction for card in combined_cards),
                                                      type=self.next_card_type)


class SameHabbits3(AutoNextCardReactor):
    __slots__ = ()

    def descrption(self):
        return '3 x одинаковых «{}» => «{}» с тем же эффектом'.format(self.own_card_type.text, self.next_card_type.text)


    def combine(self, combined_cards):
        if len(combined_cards) != 3:
            return None

        if not self.check_types(combined_cards):
            return None

        if not self.check_data_equality(combined_cards):
            return None

        return self.next_card_type.effect.create_card(available_for_auction=all(card.available_for_auction for card in combined_cards),
                                                      type=self.next_card_type,
                                                      habit=game_relations.HABIT_TYPE(combined_cards[0].data['habit_id']),
                                                      direction=combined_cards[0].data['direction'])


class Same2(BaseReactor):
    __slots__ = ()

    def descrption(self):
        return '2 x «{}» => «{}» с другим эффектом'.format(self.own_card_type.text, self.own_card_type.text)


    def combine(self, combined_cards):

        if len(combined_cards) != 2:
            return None

        if not self.check_types(combined_cards):
            return None

        new_card = None

        excluded_data = [card.data for card in combined_cards]

        while new_card is None or new_card.data in excluded_data:
            new_card = self.own_card_type.effect.create_card(available_for_auction=all(card.available_for_auction for card in combined_cards),
                                                             type=self.own_card_type)

        return new_card


class SameEqual2(AutoNextCardReactor):

    def descrption(self):
        return '2 x одинаковых «{}» => «{}» с другим эффектом'.format(self.own_card_type.text, self.own_card_type.text)


    def combine(self, combined_cards):
        if len(combined_cards) != 2:
            return None

        if not self.check_types(combined_cards):
            return None

        if not self.check_data_equality(combined_cards):
            return None

        new_card = None

        excluded_data = [card.data for card in combined_cards]

        while new_card is None or new_card.data in excluded_data:
            new_card = self.own_card_type.effect.create_card(available_for_auction=all(card.available_for_auction for card in combined_cards),
                                                             type=self.own_card_type)

        return new_card


class SamePower3(AutoNextCardReactor):

    def descrption(self):
        return '3 x одинаковых «{}» => «{}» с тем же эффектом'.format(self.own_card_type.text, self.next_card_type.text)


    def combine(self, combined_cards):
        if len(combined_cards) != 3:
            return None

        if not self.check_types(combined_cards):
            return None

        if not self.check_data_equality(combined_cards):
            return None

        return self.next_card_type.effect.create_card(available_for_auction=all(card.available_for_auction for card in combined_cards),
                                                      type=self.next_card_type,
                                                      direction=combined_cards[0].data['direction'])
