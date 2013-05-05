# coding: utf-8

from common.amqp_queues.django_commands import construct_command
from common.postponed_tasks.workers.environment import workers_environment

Command = construct_command(workers_environment, workers_environment.refrigerator)
