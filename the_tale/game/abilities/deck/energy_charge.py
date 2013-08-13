# coding: utf-8


from game.abilities.prototypes import AbilityPrototype
from game.abilities.deck.help import Help


class EnergyCharge(AbilityPrototype):

    COST = 0
    NAME = u'Энергия'
    DESCRIPTION = u'Восстановить полный запас энергии'

    def use(self, data, storage, **kwargs): # pylint: disable=R0911

        hero = storage.heroes[data['hero_id']]

        if hero.energy_charges == 0:
            return False, None, ()

        if hero.energy >= Help.COST:
            return False, None, ()

        hero.energy_charges -= 1
        hero.change_energy(hero.energy_maximum)

        return True, None, ()
