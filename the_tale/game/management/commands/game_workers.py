# coding: utf-8
import os
import time
import subprocess

from optparse import make_option

from django.core.management.base import BaseCommand

from dext.utils import pid

from game.conf import game_settings
from game.workers.environment import workers_environment

def start():
    with open(os.devnull, 'w') as devnull:
        subprocess.Popen(['./manage.py', 'game_supervisor'], stdin=devnull, stdout=devnull, stderr=devnull)
        subprocess.Popen(['./manage.py', 'game_logic'], stdin=devnull, stdout=devnull, stderr=devnull)

        if game_settings.ENABLE_WORKER_HIGHLEVEL:
            subprocess.Popen(['./manage.py', 'game_highlevel'], stdin=devnull, stdout=devnull, stderr=devnull)

        if game_settings.ENABLE_WORKER_TURNS_LOOP:
            subprocess.Popen(['./manage.py', 'game_turns_loop'], stdin=devnull, stdout=devnull, stderr=devnull)

        if game_settings.ENABLE_WORKER_MIGHT_CALCULATOR:
            subprocess.Popen(['./manage.py', 'game_might_calculator'], stdin=devnull, stdout=devnull, stderr=devnull)

        if game_settings.ENABLE_WORKER_LONG_COMMANDS:
            subprocess.Popen(['./manage.py', 'game_long_commands'], stdin=devnull, stdout=devnull, stderr=devnull)

        if game_settings.ENABLE_PVP:
            subprocess.Popen(['./manage.py', 'pvp_balancer'], stdin=devnull, stdout=devnull, stderr=devnull)

    print 'game started'

def stop():
    if pid.check('game_supervisor'):
        print 'supervisor found, send stop command'
        workers_environment.supervisor.cmd_stop()
        print 'waiting answer'
        answer_cmd = workers_environment.supervisor.stop_queue.get(block=True)
        answer_cmd.ack()
        print 'answer received'

    while (pid.check('game_supervisor') or
           pid.check('game_logic') or
           pid.check('game_highlevel') or
           pid.check('game_turns_loop') or
           pid.check('game_might_calculator') or
           pid.check('game_pvp_balancer') or
           pid.check('game_long_commands') ):
        time.sleep(0.1)

    print 'game stopped'


class Command(BaseCommand):

    help = 'run game logic'

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
            pid.force_kill('game_supervisor')
            pid.force_kill('game_logic')
            pid.force_kill('game_highlevel')
            pid.force_kill('game_turns_loop')
            pid.force_kill('game_might_calculator')
            pid.force_kill('game_long_commands')
            pid.force_kill('game_pvp_balancer')

            print 'game stopped'

        elif command == 'restart':
            start()
            stop()
            print 'game restarted '

        elif command == 'status':
            print 'command "%s" does not implemented yet ' % command

        else:
            print 'command did not specified'
