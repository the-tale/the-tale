# coding: utf-8

from django.core.urlresolvers import reverse

from dext.views import handler, validate_argument_with_resource
from dext.utils.decorators import debug_required

from common.utils.decorators import staff_required, login_required
from common.utils.resources import Resource

from game.abilities.models import AbilitiesData
from game.abilities.deck import ABILITIES

from game.heroes.prototypes import HeroPrototype

from game.map.conf import map_settings

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

    @validate_argument_with_resource('account', Resource.validate_account_argument, 'game.info', u'неверный идентификатор аккаунта')
    @handler('info', method='get')
    def info(self, account):

        data = {}

        data['mode'] = 'pve'

        data['turn'] = self.time.ui_info()

        hero = HeroPrototype.get_by_account_id(account.id)

        is_own_hero = self.account and self.account.id == account.id

        if is_own_hero:
            data['hero'] = hero.cached_ui_info(from_cache=True)
            abilities_data = AbilitiesData.objects.get(hero_id=hero.id)
            data['abilities'] = [ability(abilities_data).ui_info() for ability_type, ability in ABILITIES.items()]

            data['pvp'] = {'waiting': False}

            battle = Battle1x1Prototype.get_active_by_account_id(account.id)

            if battle:
                if battle.state.is_waiting:
                    data['pvp']['waiting'] = True
                if battle.state.is_processing or battle.state.is_prepairing:
                    data['mode'] = 'pvp'
        else:
            data['hero'] = hero.ui_info(for_last_turn=True, quests_info=False)

        return self.json_ok(data=data)

    @debug_required
    @staff_required()
    @handler('next-turn', method=['post'])
    def next_turn(self):

        from .workers.environment import workers_environment
        workers_environment.supervisor.cmd_next_turn()

        return self.json(status='ok')
