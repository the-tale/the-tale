# -*- coding: utf-8 -*-

from dext.views.resources import handler
from dext.utils.decorators import staff_required, debug_required

from common.utils.resources import Resource

from game.angels.prototypes import AngelPrototype

from game.map.conf import map_settings
from game.quests.prototypes import QuestPrototype

from game.conf import game_settings

class GameResource(Resource):

    def __init__(self, request, *args, **kwargs):
        super(GameResource, self).__init__(request, *args, **kwargs)

    @handler('', method='get')
    def game_page(self):
        return self.template('game/game_page.html',
                             {'map_settings': map_settings,
                              'game_settings': game_settings,
                              'angel': self.account.angel if self.account else None } )

    @handler('info', method='get')
    def info(self, angel=None):
        data = {}

        data['turn'] = self.time.ui_info()

        is_own_angel = False

        if self.account:
            own_angel = self.account.angel

            if angel is None:
                angel = own_angel
                is_own_angel = True

            else:
                angel = AngelPrototype.get_by_id(int(angel))

                if angel is None:
                    return self.json(status='error', error=u'Вы запрашиваете информацию несуществующего игрока')

                if own_angel.id == angel.id:
                    is_own_angel = True

        if angel:

            hero = angel.get_hero()

            if is_own_angel:
                data['angel'] = angel.ui_info(turn_number=self.time.turn_number)

            data['hero'] = hero.ui_info()

            quest = QuestPrototype.get_for_hero(hero.id)
            if quest:
                data['hero']['quests'] = quest.ui_info(hero)
            else:
                data['hero']['quests'] = {}

        return self.json(status='ok', data=data)

    @debug_required
    @staff_required()
    @handler('next-turn', method=['post'])
    def next_turn(self):

        from .workers.environment import workers_environment
        workers_environment.supervisor.cmd_next_turn()

        return self.json(status='ok')
