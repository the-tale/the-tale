# coding: utf-8

from rels.django_staff import DjangoEnum

from the_tale.common.utils.enum import create_enum

from the_tale.game.pvp.prototypes import Battle1x1Prototype

from the_tale.game.workers.environment import workers_environment

from the_tale.game.abilities.prototypes import AbilityPrototype
from the_tale.game.heroes.prototypes import HeroPrototype


ABILITY_TASK_STEP = create_enum('ABILITY_TASK_STEP', (('ERROR', 0, u'ошибка'),
                                                      ('LOGIC', 1, u'логика'),
                                                      ('PVP_BALANCER', 2, u'pvp балансировщик'),
                                                      ('SUCCESS', 3, u'обработка завершена') ))


class ACCEPT_BATTLE_RESULT(DjangoEnum):
    _records = ( ('BATTLE_NOT_FOUND', 1, u'битва не найдена'),
                 ('WRONG_ACCEPTED_BATTLE_STATE', 2, u'герой не успел принять вызов'),
                 ('WRONG_INITIATOR_BATTLE_STATE', 3, u'герой уже находится в сражении'),
                 ('NOT_IN_QUEUE', 4, u'битва не находится в очереди балансировщика'),
                 ('PROCESSED', 5, u'обработана') )


class ArenaPvP1x1Accept(AbilityPrototype):

    COST = 1
    NAME = u'Принять вызов'
    DESCRIPTION = u'Принять вызов другого героя'

    @classmethod
    def accept_battle(cls, pvp_balancer, battle_id, hero_id):

        accepted_battle = Battle1x1Prototype.get_by_id(battle_id)

        if accepted_battle is None:
            return ACCEPT_BATTLE_RESULT.BATTLE_NOT_FOUND

        if not accepted_battle.state._is_WAITING:
            return ACCEPT_BATTLE_RESULT.WRONG_ACCEPTED_BATTLE_STATE

        if not accepted_battle.account_id in pvp_balancer.arena_queue:
            return ACCEPT_BATTLE_RESULT.NOT_IN_QUEUE

        initiator_id = HeroPrototype.get_by_id(hero_id).account_id

        initiator_battle = Battle1x1Prototype.get_by_account_id(initiator_id)

        if initiator_battle is not None and not initiator_battle.state._is_WAITING:
            return ACCEPT_BATTLE_RESULT.WRONG_INITIATOR_BATTLE_STATE

        if initiator_id not in pvp_balancer.arena_queue:
            pvp_balancer.add_to_arena_queue(hero_id)

        pvp_balancer.force_battle(accepted_battle.account_id, initiator_id)

        return ACCEPT_BATTLE_RESULT.PROCESSED


    def use(self, data, step, main_task_id, storage, pvp_balancer, **kwargs):

        if step is None:

            hero = storage.heroes[data['hero_id']]

            return None, ABILITY_TASK_STEP.PVP_BALANCER, ((lambda: workers_environment.pvp_balancer.cmd_logic_task(hero.account_id, main_task_id)), )

        elif step == ABILITY_TASK_STEP.PVP_BALANCER:

            accept_result = self.accept_battle(pvp_balancer, data['battle'], data['hero_id'])

            if not accept_result._is_PROCESSED:
                return False, ABILITY_TASK_STEP.ERROR, ()

            return True, ABILITY_TASK_STEP.SUCCESS, ()
