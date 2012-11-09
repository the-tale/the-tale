# coding: utf-8

from accounts.prototypes import AccountPrototype

from game.pvp.prototypes import Battle1x1Prototype

from game.workers.environment import workers_environment

from game.abilities.prototypes import AbilityPrototype

class ArenaPvP1x1(AbilityPrototype):

    COST = 1

    COMMAND_PREFIX = 'arena_pvp_1x1'

    NAME = u'Отправить на арену'
    DESCRIPTION = u'Отправить героя на гладиаторскую арену'

    def use(self, storage, hero, form):

        battle = Battle1x1Prototype.create(AccountPrototype.get_by_id(hero.account_id))

        workers_environment.pvp_balancer.cmd_add_to_arena_queue(battle.id)

        hero.add_message('angel_ability_arena_pvp_1x1', hero=hero)

        return True
