# coding: utf-8

from django.core.urlresolvers import reverse

from dext.views import handler, validate_argument_with_resource
from dext.utils.decorators import debug_required

from common.utils.decorators import staff_required, login_required
from common.utils.resources import Resource
from common.utils import api

from accounts.clans.prototypes import ClanPrototype

from game.heroes.relations import EQUIPMENT_SLOT

from game.map.conf import map_settings
from game.map.storage import map_info_storage

from game.conf import game_settings
from game.pvp.prototypes import Battle1x1Prototype
from game import logic as game_logic

class GameResource(Resource):

    def initialize(self, *args, **kwargs):
        super(GameResource, self).initialize(*args, **kwargs)

    @login_required
    @handler('', method='get')
    def game_page(self):

        battle = Battle1x1Prototype.get_by_account_id(self.account.id)

        if battle and battle.state._is_PROCESSING:
            return self.redirect(reverse('game:pvp:'))

        clan = None
        if self.account.clan_id is not None:
            clan = ClanPrototype.get_by_id(self.account.clan_id)

        return self.template('game/game_page.html',
                             {'map_settings': map_settings,
                              'game_settings': game_settings,
                              'EQUIPMENT_SLOT': EQUIPMENT_SLOT,
                              'current_map_version': map_info_storage.version,
                              'clan': clan} )

    @api.handler(versions=('1.0',))
    @validate_argument_with_resource('account', Resource.validate_account_argument, 'game.info', u'неверный идентификатор аккаунта', raw=True)
    @handler('api', 'info', name='api-info', method='get')
    def info(self, api_version=None, account=None):

        if account is None and self.account.is_authenticated():
            account = self.account

        data = game_logic.form_game_info(account=account)

        return self.ok(data=data)

    @debug_required
    @staff_required()
    @handler('next-turn', method=['post'])
    def next_turn(self):

        from .workers.environment import workers_environment
        workers_environment.supervisor.cmd_next_turn()

        return self.json(status='ok')
