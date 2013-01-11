# coding: utf-8

from game.pvp.prototypes import Battle1x1Prototype

class PvPTestsMixin(object):

    def pvp_create_battle(self, account, enemy, state=None):
        battle = Battle1x1Prototype.create(account)
        if enemy:
            battle.set_enemy(enemy)
        if state is not None:
            battle.state = state
        battle.save()
        return battle
