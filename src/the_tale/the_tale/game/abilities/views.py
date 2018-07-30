
import smart_imports

smart_imports.all()


def argument_to_ability(ability_type): return deck.ABILITIES.get(relations.ABILITY_TYPE(ability_type))


class AbilitiesResource(utils_resources.Resource):

    @utils_decorators.login_required
    @dext_old_views.validate_argument('ability', argument_to_ability, 'abilities', 'Неверный идентификатор способности')
    def initialize(self, ability=None, *argv, **kwargs):
        super(AbilitiesResource, self).initialize(*argv, **kwargs)
        self.ability = ability()

    @utils_api.handler(versions=('1.0',))
    @dext_old_views.validate_argument('battle', int, 'abilities', 'Неверный идентификатор сражения')
    @dext_old_views.handler('#ability', 'api', 'use', method='post')
    def use(self, api_version, battle=None):
        task = self.ability.activate(heroes_logic.load_hero(account_id=self.account.id),
                                     data={'battle_id': battle})

        if task is None:
            return self.error('game.abilities.use.no_enough_energy', 'Недостаточно энергии')

        return self.processing(task.status_url)
