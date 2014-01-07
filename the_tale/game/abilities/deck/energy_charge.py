# coding: utf-8


from the_tale.game.abilities.prototypes import AbilityPrototype
from the_tale.game.abilities.relations import ABILITY_TYPE, ABILITY_RESULT


class EnergyCharge(AbilityPrototype):
    TYPE = ABILITY_TYPE.ENERGY_CHARGE

    def use(self, data, storage, **kwargs): # pylint: disable=R0911

        hero = storage.heroes[data['hero_id']]

        if hero.energy_charges == 0:
            return ABILITY_RESULT.FAILED, None, ()

        if hero.energy >= ABILITY_TYPE.HELP.cost:
            return ABILITY_RESULT.FAILED, None, ()

        hero.energy_charges -= 1
        hero.change_energy(hero.energy_maximum)

        return ABILITY_RESULT.SUCCESSED, None, ()
