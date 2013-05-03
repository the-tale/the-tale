# coding: utf-8

from game.conf import game_settings
from game.workers.environment import workers_environment

from common.amqp_workers.django_commands import construct_workers_manager

Command = construct_workers_manager(help='run game workers',
                                    pid='game_workers',
                                    workers=(workers_environment.game_settings,
                                             workers_environment.game_logic,
                                             workers_environment.game_highlevel if game_settings.ENABLE_WORKER_HIGHLEVEL else None,
                                             workers_environment.turns_loop if game_settings.ENABLE_WORKER_TURNS_LOOP else None,
                                             workers_environment.game_might_calculator if game_settings.ENABLE_WORKER_MIGHT_CALCULATOR else None,
                                             workers_environment.game_long_commands if game_settings.ENABLE_WORKER_LONG_COMMANDS else None,
                                             workers_environment.game_pvp_balancer if game_settings.ENABLE_PVP else None) )
