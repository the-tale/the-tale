# coding: utf-8

from the_tale.game.pvp.prototypes import Battle1x1Prototype

class PvPTestsMixin(object):

    def pvp_create_battle(self, account, enemy, state=None, calculate_rating=False):
        battle = Battle1x1Prototype.create(account)
        if enemy:
            battle.set_enemy(enemy)
        if state is not None:
            battle.state = state
        battle.calculate_rating = calculate_rating
        battle.save()
        return battle
