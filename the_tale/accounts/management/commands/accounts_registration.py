# coding: utf-8

from the_tale.common.amqp_queues.django_commands import construct_command
from the_tale.accounts.workers.environment import workers_environment

Command = construct_command(workers_environment, workers_environment.registration)
