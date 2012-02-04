# -*- coding: utf-8 -*-

from dext.views.resources import handler
from dext.utils.decorators import staff_required, debug_required

from common.utils.resources import Resource

from .heroes.logic import get_angel_heroes

from .prototypes import get_current_time

from .map import settings as map_settings
from .angels.prototypes import get_angel_by_id

from . import settings as game_settings

class GameResource(Resource):

    def __init__(self, request, *args, **kwargs):
        super(GameResource, self).__init__(request, *args, **kwargs)

    @handler('', method='get')
    def game_page(self):
        return self.template('game/game_page.html',
                             {'map_settings': map_settings,
                              'game_settings': game_settings} )

    @handler('info', method='get')
    def info(self, angel=None):
        data = {}

        data['turn'] = get_current_time().ui_info()

        if self.angel:
            if angel is None:
                angel = self.angel.id

        if angel:
            foreign_angel = get_angel_by_id(int(angel))
            data['heroes'] = dict( (hero.id, hero.ui_info()) for hero in get_angel_heroes(foreign_angel.id) )

        return self.json(status='ok', data=data)

    @debug_required
    @staff_required()
    @handler('next_turn', method=['post'])
    def next_turn(self):

        from .workers.environment import workers_environment
        workers_environment.supervisor.cmd_next_turn()

        return self.json(status='ok')



