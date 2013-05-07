# coding: utf-8

from common.amqp_queues.django_commands import construct_workers_manager

from accounts.workers.environment import workers_environment as accounts_workers_environment
from post_service.workers.environment import workers_environment as post_service_workers_environment
from bank.workers.environment import workers_environment as bank_workers_environment
from common.postponed_tasks.workers.environment import workers_environment as postponed_tasks_workers_environment

Command = construct_workers_manager(help='run infrastructure workers',
                                    process_pid='game_workers',
                                    environments=[accounts_workers_environment,
                                                  post_service_workers_environment,
                                                  postponed_tasks_workers_environment,
                                                  bank_workers_environment],
                                    # bank worker MUST be places in start of the list
                                    # since it MUST be stopped latest
                                    workers=(bank_workers_environment.bank_processor,
                                             postponed_tasks_workers_environment.refrigerator,
                                             post_service_workers_environment.message_sender,
                                             accounts_workers_environment.registration,
                                             accounts_workers_environment.accounts_manager  ) )
