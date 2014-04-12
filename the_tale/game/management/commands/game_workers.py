# coding: utf-8

from the_tale.game.conf import game_settings
from the_tale.game.workers.environment import workers_environment

from the_tale.common.amqp_queues.django_commands import construct_workers_manager

from the_tale.game.prototypes import GameState

_BaseCommand = construct_workers_manager(help='run game workers',
                                         process_pid='game_workers',
                                         workers=(workers_environment.supervisor,
                                                  workers_environment.logic,
                                                  workers_environment.highlevel if game_settings.ENABLE_WORKER_HIGHLEVEL else None,
                                                  workers_environment.turns_loop if game_settings.ENABLE_WORKER_TURNS_LOOP else None,
                                                  workers_environment.pvp_balancer if game_settings.ENABLE_PVP else None) )

class Command(_BaseCommand):

    def before_force_stop(self):
        GameState.stop()
