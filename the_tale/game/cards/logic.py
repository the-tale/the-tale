# -*- coding: utf-8 -*-

from .models import Card, CardsQueueItem
from .prototypes import get_card_by_model, get_card_queue_item_by_model

def get_angel_deck(angel_id):
    cards = Card.objects.filter(angel=angel_id)
    deck = [get_card_by_model(card) for card in cards]
    return deck


def next_turn_process_cards(cur_turn, next_turn):
    cards_queue = CardsQueueItem.objects.filter(turn=cur_turn.model).order_by('created_at')

    for card_queue_item in [get_card_queue_item_by_model(item_model) for item_model in list(cards_queue)]:
        card_queue_item.process()
