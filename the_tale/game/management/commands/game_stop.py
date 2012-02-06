# coding: utf-8

from django.core.management.base import BaseCommand

from ...workers.environment import workers_environment

class Command(BaseCommand):

    help = 'stop game workers'

    requires_model_validation = False

    def handle(self, *args, **options):

        print 'send stop command'

        workers_environment.supervisor.cmd_stop()

        print 'waiting answer'
        
        answer_cmd = workers_environment.supervisor.stop_queue.get(block=True)
        answer_cmd.ack()

        print 'answer received, game stopped, you can kill workers now'



