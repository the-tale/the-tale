# -*- coding: utf-8 -*-

from django_next.views.resources import handler
from common.utils.resources import Resource

from .cards.logic import get_angel_deck
from .heroes.logic import get_angel_heroes

from .turns.models import Turn
from .turns.prototypes import get_latest_turn

from .map import settings as map_settings

class GameResource(Resource):

    def __init__(self, request, *args, **kwargs):
        super(GameResource, self).__init__(request, *args, **kwargs)

    @handler('', method='get')
    def game_page(self):
        return self.template('game/game_page.html',
                             {'map_settings': map_settings} )

    @handler('info', method='get')
    def info(self):
        data = {}

        data['turn'] = {'number': -1}
        try:
            turn = get_latest_turn()
            data['turn'] = turn.ui_info()
        except Turn.DoesNotExist:
            pass

        data['deck'] = dict( (card.id, card.ui_info()) for card in get_angel_deck(self.angel.id) )
        data['heroes'] = dict( (hero.id, hero.ui_info()) for hero in get_angel_heroes(self.angel.id) )
        return self.json(status='ok', 
                         turn_number=1,
                         data=data);


