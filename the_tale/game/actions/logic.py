# -*- coding: utf-8 -*-
from django_next.utils.decorators import nested_commit_on_success

from .models import Action, ActionIdleness
from .prototypes import get_action_by_model

@nested_commit_on_success
def next_turn_update_actions(cur_turn, next_turn):
    
    for action_model in Action.objects.all().order_by('-created_at'):
        try:
            if not ActionIdleness.objects.all().exists():
                raise Exception('ERROR 1')

            action = get_action_by_model(base_model=action_model)
            action.process()
            action.save()

            if not ActionIdleness.objects.all().exists():
                raise Exception('ERROR 2')


        except Exception, e:
            if e.__class__ in []:
                continue
            raise
            print '%s: %s' % (e.__class__, e)
