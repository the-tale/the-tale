# coding: utf-8

from django.core.urlresolvers import reverse

from dext.views.resources import handler

from common.utils.decorators import login_required
from common.utils.resources import Resource

from accounts.prototypes import AccountPrototype

from game.heroes.prototypes import HeroPrototype

from game.pvp.prototypes import Battle1x1Prototype
from game.conf import game_settings

class PvPResource(Resource):

    def initialize(self, *args, **kwargs):
        super(PvPResource, self).initialize(*args, **kwargs)

    def fill_account_info(self, data, account):
        hero = HeroPrototype.get_by_account_id(account.id)

        data['hero'] = hero.ui_info()

    @login_required
    @handler('', method='get')
    def pvp_page(self):

        battle = Battle1x1Prototype.get_by_account_id(self.account.id)

        if battle is None or not battle.state.is_processing:
            return self.redirect(reverse('game:'))

        own_hero = HeroPrototype.get_by_account_id(battle.account_id)
        own_abilities = sorted(own_hero.abilities.all, key=lambda x: x.NAME)

        enemy_hero = HeroPrototype.get_by_account_id(battle.enemy_id)
        enemy_abilities = sorted(enemy_hero.abilities.all, key=lambda x: x.NAME)
        return self.template('pvp/pvp_page.html',
                             {'enemy_account': AccountPrototype.get_by_id(battle.enemy_id),
                              'own_abilities': own_abilities,
                              'enemy_abilities': enemy_abilities,
                              'game_settings': game_settings} )

    @login_required
    @handler('info', method='get')
    def info(self):

        battle = Battle1x1Prototype.get_by_account_id(self.account.id)

        if battle is None or not battle.state.is_processing:
            return self.json_ok(data={'mode': 'pve',
                                      'turn': self.time.ui_info()})

        data = {'mode': 'pvp',
                'turn': self.time.ui_info(),
                'account': {},
                'enemy': {}}

        account = self.account
        enemy = AccountPrototype.get_by_id(battle.enemy_id)

        self.fill_account_info(data['account'], account)
        self.fill_account_info(data['enemy'], enemy)

        return self.json_ok(data=data)
