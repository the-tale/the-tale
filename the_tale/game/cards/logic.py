# -*- coding: utf-8 -*-

from .models import Card
from .prototypes import get_card_by_model

def get_angel_deck(angel_id):
    cards = Card.objects.filter(angel=angel_id)
    deck = [get_card_by_model(card) for card in cards]
    return deck
