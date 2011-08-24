# -*- coding: utf-8 -*-
from django_next.utils.decorators import nested_commit_on_success

from .models import Action
from .prototypes import get_action_by_model

@nested_commit_on_success
def next_turn_update_actions(cur_turn, next_turn):
    
    for action_model in list(Action.objects.all().order_by('-created_at')):
        try:
            action = get_action_by_model(base_model=action_model)
            action.process()
            
            #action.save()

        except Exception, e:
            if e.__class__ in []:
                continue
            raise
