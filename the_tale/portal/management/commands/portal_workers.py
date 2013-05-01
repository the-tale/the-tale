# coding: utf-8
import os
import time
import subprocess

from optparse import make_option

from django.core.management.base import BaseCommand

from dext.utils import pid

from accounts.workers.environment import workers_environment as accounts_workers_environment
from post_service.workers.environment import workers_environment as post_service_workers_environment
from bank.workers.environment import workers_environment as bank_workers_environment

def start():
    with open(os.devnull, 'w') as devnull:
        subprocess.Popen(['./manage.py', 'accounts_registration'], stdin=devnull, stdout=devnull, stderr=devnull)

    with open(os.devnull, 'w') as devnull:
        subprocess.Popen(['./manage.py', 'post_service_message_sender'], stdin=devnull, stdout=devnull, stderr=devnull)

    with open(os.devnull, 'w') as devnull:
        subprocess.Popen(['./manage.py', 'bank_bank_processor'], stdin=devnull, stdout=devnull, stderr=devnull)

    print 'infrastructure started'

def stop():
    if pid.check('accounts_registration'):
        print 'registration found, send stop command'
        accounts_workers_environment.registration.cmd_stop()
        print 'waiting answer'
        answer_cmd = accounts_workers_environment.registration.stop_queue.get(block=True)
        answer_cmd.ack()
        print 'answer received'

    if pid.check('post_service_message_sender'):
        print 'post service message sender found, send stop command'
        post_service_workers_environment.message_sender.cmd_stop()
        print 'waiting answer'
        answer_cmd = post_service_workers_environment.message_sender.stop_queue.get(block=True)
        answer_cmd.ack()
        print 'answer received'

    if pid.check('bank_bank_processor'):
        print 'bank processor found, send stop command'
        bank_workers_environment.bank_processor.cmd_stop()
        print 'waiting answer'
        answer_cmd = bank_workers_environment.bank_processor.stop_queue.get(block=True)
        answer_cmd.ack()
        print 'answer received'

    while (pid.check('accounts_registration') or
           pid.check('post_service_message_sender') or
           pid.check('bank_bank_processor')):
        time.sleep(0.1)

    print 'infrastructure stopped'


class Command(BaseCommand):

    help = 'run infrastructure workers'

    requires_model_validation = False

    option_list = BaseCommand.option_list + ( make_option('-c', '--command',
                                                          action='store',
                                                          type=str,
                                                          dest='command',
                                                          help='start|stop|restart|status'),
                                              )

    @pid.protector('game_workers')
    def handle(self, *args, **options):
        command = options['command']

        if command == 'start':
            start()
        elif command == 'stop':
            stop()
        elif command == 'force_stop':
            pid.force_kill('accounts_registration')
            pid.force_kill('post_service_message_sender')
            print 'infrastructure stopped'

        elif command == 'restart':
            start()
            stop()
            print 'infrastructure restarted '

        elif command == 'status':
            print 'command "%s" does not implemented yet ' % command

        else:
            print 'command did not specified'
