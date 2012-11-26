# coding: utf-8

from game.pvp.prototypes import Battle1x1Prototype

from game.workers.environment import workers_environment

from game.abilities.prototypes import AbilityPrototype

class ArenaPvP1x1LeaveQueue(AbilityPrototype):

    COST = 0

    COMMAND_PREFIX = 'arena_pvp_1x1_leave_queue'

    NAME = u'Выйти из очереди'
    DESCRIPTION = u'Выйти из очереди на арену'

    def use(self, storage, hero, form):

        battle = Battle1x1Prototype.get_active_by_account_id(hero.account_id)

        if battle is None:
            return True

        workers_environment.pvp_balancer.cmd_leave_arena_queue(battle.id)

        hero.add_message('angel_ability_arena_pvp_1x1_leave_queue', hero=hero)

        return True
