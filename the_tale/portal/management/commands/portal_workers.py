# coding: utf-8

from accounts.workers.environment import workers_environment as accounts_workers_environment
from post_service.workers.environment import workers_environment as post_service_workers_environment
from bank.workers.environment import workers_environment as bank_workers_environment
from common.postponed_tasks.workers.environment import workers_environment as postponed_tasks_workers_environment

from common.amqp_workers.django_commands import construct_workers_manager

Command = construct_workers_manager(help='run infrastructure workers',
                                    pid='game_workers',
                                    workers=(accounts_workers_environment.registration,
                                             post_service_workers_environment.message_sender,
                                             postponed_tasks_workers_environment.refrigerator,
                                             bank_workers_environment.bank_processor) )
