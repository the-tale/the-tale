# coding: utf-8

from the_tale.common.amqp_queues.django_commands import construct_workers_manager

from the_tale.accounts.workers.environment import workers_environment as accounts_workers_environment
from the_tale.accounts.achievements.workers.environment import workers_environment as achievements_workers_environment
from the_tale.post_service.workers.environment import workers_environment as post_service_workers_environment
from the_tale.bank.workers.environment import workers_environment as bank_workers_environment
from the_tale.common.postponed_tasks.workers.environment import workers_environment as postponed_tasks_workers_environment
from the_tale.portal.workers.environment import workers_environment as portal_workers_environment

from the_tale.portal.conf import portal_settings

Command = construct_workers_manager(help='run infrastructure workers',
                                    process_pid='game_workers',
                                    # bank worker MUST be places in start of the list
                                    # since it MUST be stopped latest
                                    workers=(bank_workers_environment.bank_processor,
                                             # bank_workers_environment.dengionline_banker,
                                             bank_workers_environment.xsolla_banker,
                                             postponed_tasks_workers_environment.refrigerator,
                                             post_service_workers_environment.message_sender,
                                             accounts_workers_environment.registration,
                                             accounts_workers_environment.accounts_manager,
                                             achievements_workers_environment.achievements_manager,
                                             portal_workers_environment.long_commands if portal_settings.ENABLE_WORKER_LONG_COMMANDS else None) )
