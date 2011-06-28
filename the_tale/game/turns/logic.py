# -*- coding: utf-8 -*-

from django_next.utils.decorators import nested_commit_on_success

from ..heroes.logic import next_turn_pre_update_heroes, next_turn_post_update_heroes
from ..actions.logic import next_turn_update_actions
from ..cards.logic import next_turn_process_cards

from .prototypes import TurnPrototype

@nested_commit_on_success
def next_turn(cur_turn):

    new_turn = TurnPrototype.create();

    next_turn_pre_update_heroes(cur_turn, next_turn)

    next_turn_process_cards(cur_turn, next_turn)

    next_turn_update_actions(cur_turn, next_turn)

    next_turn_post_update_heroes(cur_turn, next_turn)

    # raise Exception('SUCCESS')
