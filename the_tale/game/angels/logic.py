# -*- coding: utf-8 -*-

from .models import Angel
from .prototypes import get_angel_by_model

def next_turn_pre_update_angels(cur_turn, next_turn):

    for angel_model in list(Angel.get_related_query().all() ):
        angel = get_angel_by_model(angel_model)

        angel.next_turn_pre_update(next_turn)
        angel.save()    
