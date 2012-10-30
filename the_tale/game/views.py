# -*- coding: utf-8 -*-

from dext.views.resources import handler
from dext.utils.decorators import debug_required

from common.utils.decorators import staff_required, login_required
from common.utils.resources import Resource

from accounts.prototypes import AccountPrototype

from game.abilities.models import AbilitiesData
from game.abilities.deck import ABILITIES

from game.heroes.prototypes import HeroPrototype

from game.map.conf import map_settings
from game.quests.prototypes import QuestPrototype

from game.conf import game_settings

class GameResource(Resource):

    def initialize(self, *args, **kwargs):
        super(GameResource, self).initialize(*args, **kwargs)

    @login_required
    @handler('', method='get')
    def game_page(self):
        return self.template('game/game_page.html',
                             {'map_settings': map_settings,
                              'game_settings': game_settings } )

    @login_required
    @handler('info', method='get')
    def info(self, account=None):

        if account is None:
            account = self.account
        else:
            try:
                account = int(account)
            except ValueError:
                return self.json_error('game.info.wrong_account_id', u'Неверный идентификатор аккаунта')

            account = AccountPrototype.get_by_id(account)

            if account is None:
                return self.json_error('game.info.account_not_exists', u'Аккаунт не найден')

        data = {}

        data['turn'] = self.time.ui_info()

        hero = HeroPrototype.get_by_account_id(account.id)
        data['hero'] = hero.ui_info()

        if self.account.id == account.id:
            abilities_data = AbilitiesData.objects.get(hero_id=hero.id)
            data['abilities'] = [ability(abilities_data).ui_info() for ability_type, ability in ABILITIES.items()]

            quest = QuestPrototype.get_for_hero(hero.id)
            if quest:
                data['hero']['quests'] = quest.ui_info(hero)
            else:
                data['hero']['quests'] = {}

        return self.json_ok(data=data)

    @debug_required
    @staff_required()
    @handler('next-turn', method=['post'])
    def next_turn(self):

        from .workers.environment import workers_environment
        workers_environment.supervisor.cmd_next_turn()

        return self.json(status='ok')
