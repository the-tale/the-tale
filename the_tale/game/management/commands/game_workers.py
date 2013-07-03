# coding: utf-8

from game.conf import game_settings
from game.workers.environment import workers_environment

from common.amqp_queues.django_commands import construct_workers_manager

Command = construct_workers_manager(help='run game workers',
                                    process_pid='game_workers',
                                    workers=(workers_environment.supervisor,
                                             workers_environment.logic,
                                             workers_environment.highlevel if game_settings.ENABLE_WORKER_HIGHLEVEL else None,
                                             workers_environment.turns_loop if game_settings.ENABLE_WORKER_TURNS_LOOP else None,
                                             workers_environment.might_calculator if game_settings.ENABLE_WORKER_MIGHT_CALCULATOR else None,
                                             workers_environment.pvp_balancer if game_settings.ENABLE_PVP else None) )
