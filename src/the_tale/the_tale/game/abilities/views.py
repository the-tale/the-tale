# coding: utf-8

from dext.views import handler, validate_argument

from the_tale.common.utils.resources import Resource
from the_tale.common.utils.decorators import login_required
from the_tale.common.utils import api

from the_tale.game.abilities.deck import ABILITIES
from the_tale.game.abilities.relations import ABILITY_TYPE

from the_tale.game.heroes import logic as heroes_logic


def argument_to_ability(ability_type): return ABILITIES.get(ABILITY_TYPE(ability_type))

class AbilitiesResource(Resource):

    @login_required
    @validate_argument('ability', argument_to_ability, 'abilities', u'Неверный идентификатор способности')
    def initialize(self, ability=None, *argv, **kwargs):
        super(AbilitiesResource, self).initialize(*argv, **kwargs)
        self.ability = ability()

    @api.handler(versions=('1.0',))
    @validate_argument('building', int, 'abilities', u'Неверный идентификатор здания')
    @validate_argument('battle', int, 'abilities', u'Неверный идентификатор сражения')
    @handler('#ability', 'api', 'use', method='post')
    def use(self, api_version, building=None, battle=None):
        u'''
Использование одной из способностей игрока (список способностей см. в разделе типов)

- **адрес:** /game/abilities/<идентификатор способности>/api/use
- **http-метод:** POST
- **версии:** 1.0
- **параметры:**
    * GET: building — идентификатор здания, если способность касается здания
    * GET: battle — идентификатор pvp сражения, если способность касается операций с pvp сражением
- **возможные ошибки**: нет

Метод является «неблокирующей операцией» (см. документацию), формат ответа соответствует ответу для всех «неблокирующих операций».

Цена использования способностей возвращается при запросе базовой информации.
        '''

        task = self.ability.activate(heroes_logic.load_hero(account_id=self.account.id),
                                     data={'building_id': building,
                                           'battle_id': battle})

        return self.processing(task.status_url)
