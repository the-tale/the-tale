# -*- coding: utf-8 -*-

from django_next.views.resources import handler
from common.utils.resources import Resource
from common.utils.decorators import login_required

from .heroes.logic import get_angel_heroes

from .turns.models import Turn
from .turns.prototypes import get_latest_turn

from .map import settings as map_settings
from .angels.prototypes import get_angel_by_id

class GameResource(Resource):

    def __init__(self, request, *args, **kwargs):
        super(GameResource, self).__init__(request, *args, **kwargs)

    @login_required
    @handler('', method='get')
    def game_page(self, angel=None):
        if angel is None:
            angel = self.angel.id
        return self.template('game/game_page.html',
                             {'map_settings': map_settings,
                              'angel_id': angel} )

    @handler('info', method='get')
    def info(self, angel=None):
        data = {}

        data['turn'] = {'number': -1}
        try:
            turn = get_latest_turn()
            data['turn'] = turn.ui_info()
        except Turn.DoesNotExist:
            pass

        if self.angel:
            if angel is None:
                angel = self.angel.id

        if angel:
            foreign_angel = get_angel_by_id(int(angel))
            data['heroes'] = dict( (hero.id, hero.ui_info()) for hero in get_angel_heroes(foreign_angel.id) )

        return self.json(status='ok', data=data)


