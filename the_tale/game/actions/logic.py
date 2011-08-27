# -*- coding: utf-8 -*-
from django_next.utils.decorators import nested_commit_on_success

from .models import Action
from .prototypes import get_action_by_model

@nested_commit_on_success
def next_turn_update_actions(cur_turn, next_turn):

    # from django.db import connection

    # x = len(connection.queries)
    # print x
   
    for action_model in list(Action.get_related_query().filter(leader=True).order_by('-created_at')):
        try:

            # y = x
            # x = len(connection.queries)
            # print x

            # if x - y > 7:
            #     print list(reversed(list(connection.queries)))[:x-y]
            #     raise Exception('!')

            action = get_action_by_model(model=action_model)
            action.process_action()

        except Exception, e:
            if e.__class__ in []:
                continue
            raise
