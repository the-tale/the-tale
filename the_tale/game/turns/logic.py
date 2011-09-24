# -*- coding: utf-8 -*-
from django.db import connection
from django.conf import settings as project_settings
from django_next.utils.decorators import nested_commit_on_success

from ..angels.logic import next_turn_pre_update_angels
from ..heroes.logic import next_turn_pre_update_heroes
from ..actions.logic import next_turn_update_actions
from ..cards.logic import next_turn_process_cards

from .prototypes import TurnPrototype, get_latest_turn

@nested_commit_on_success
def next_turn():

    cur_turn = get_latest_turn()

    new_turn = TurnPrototype.create();

    next_turn_pre_update_angels(cur_turn, new_turn)

    next_turn_pre_update_heroes(cur_turn, new_turn)

    if project_settings.DEBUG_DB:
        print 'queries after heroes pre-update: %d' % len(connection.queries)

    next_turn_process_cards(cur_turn, new_turn)

    if project_settings.DEBUG_DB:
        print 'queries after processing cards: %d' % len(connection.queries)

    next_turn_update_actions(cur_turn, new_turn)

    if project_settings.DEBUG_DB:
        print 'queries after actions: %d' % len(connection.queries)
