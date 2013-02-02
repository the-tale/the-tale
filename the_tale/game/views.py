# coding: utf-8

from django.core.urlresolvers import reverse

from dext.views import handler, validate_argument
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
from game.pvp.prototypes import Battle1x1Prototype

class GameResource(Resource):

    def initialize(self, *args, **kwargs):
        super(GameResource, self).initialize(*args, **kwargs)

    @login_required
    @handler('', method='get')
    def game_page(self):

        battle = Battle1x1Prototype.get_active_by_account_id(self.account.id)

        if battle and battle.state.is_processing:
            return self.redirect(reverse('game:pvp:'))

        return self.template('game/game_page.html',
                             {'map_settings': map_settings,
                              'game_settings': game_settings } )

    @validate_argument('account', AccountPrototype.get_by_id, 'game.info', u'неверный идентификатор аккаунта')
    @handler('info', method='get')
    def info(self, account):

        data = {}

        data['mode'] = 'pve'

        data['turn'] = self.time.ui_info()

        hero = HeroPrototype.get_by_account_id(account.id)
        data['hero'] = hero.ui_info(for_last_turn=False)

        if self.account and self.account.id == account.id:
            abilities_data = AbilitiesData.objects.get(hero_id=hero.id)
            data['abilities'] = [ability(abilities_data).ui_info() for ability_type, ability in ABILITIES.items()]

            quest = QuestPrototype.get_for_hero(hero.id)
            if quest:
                data['hero']['quests'] = quest.ui_info(hero)
            else:
                data['hero']['quests'] = {}

            data['pvp'] = {'waiting': False}

            battle = Battle1x1Prototype.get_active_by_account_id(account.id)

            if battle:
                if battle.state.is_waiting:
                    data['pvp']['waiting'] = True
                if battle.state.is_processing or battle.state.is_prepairing:
                    data['mode'] = 'pvp'

        return self.json_ok(data=data)

    @debug_required
    @staff_required()
    @handler('next-turn', method=['post'])
    def next_turn(self):

        from .workers.environment import workers_environment
        workers_environment.supervisor.cmd_next_turn()

        return self.json(status='ok')
