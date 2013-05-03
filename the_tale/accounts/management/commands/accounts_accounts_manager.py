# coding: utf-8

from common.amqp_workers.django_commands import construct_command
from accounts.workers.environment import workers_environment

Command = construct_command(workers_environment, workers_environment.accounts_manager)
