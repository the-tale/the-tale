# coding: utf-8

from dext.views import handler, validate_argument

from the_tale.common.utils.resources import Resource
from the_tale.common.utils.decorators import login_required

from the_tale.game.heroes.prototypes import HeroPrototype

from the_tale.game.abilities.deck import ABILITIES

class AbilitiesResource(Resource):

    @login_required
    def initialize(self, ability_type=None, *argv, **kwargs):
        super(AbilitiesResource, self).initialize(*argv, **kwargs)
        self.ability_type = ability_type

        if self.ability_type not in ABILITIES:
            return self.auto_error('abilities.wrong_ability', u'У вас нет такой способности')

        self.ability = ABILITIES[self.ability_type]()


    @validate_argument('building', int, 'abilities', u'Неверный идентификатор здания')
    @validate_argument('battle', int, 'abilities', u'Неверный идентификатор сражения')
    @handler('#ability_type', 'activate', method='post')
    def activate(self, building=None, battle=None):

        task = self.ability.activate(HeroPrototype.get_by_account_id(self.account.id), data={'building_id': building,
                                                                                             'battle': battle})

        return self.json_processing(task.status_url)
