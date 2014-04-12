# coding: utf-8
import os
import sys
import time
import traceback
import subprocess

from optparse import make_option

from django.core.management.base import BaseCommand
from django.conf import settings as project_settings

from dext.utils import pid

def initialize_newrelic():
    import newrelic.agent
    newrelic.agent.initialize(project_settings.NEWRELIC_CONF_PATH)


def construct_command(environment, worker):

    class Command(BaseCommand):

        help = 'run "%s"' % worker.name

        requires_model_validation = False

        @pid.protector(worker.pid)
        def handle(self, *args, **options):

            try:
                worker.initialize()

                if project_settings.NEWRELIC_ENABLED:
                    initialize_newrelic()

                worker.run()

            except KeyboardInterrupt:
                pass
            except Exception:
                traceback.print_exc()
                worker.logger.error('Infrastructure worker exception: %s' % worker.name,
                                    exc_info=sys.exc_info(),
                                    extra={} )

            # TODO: close worker's queues

    return Command


def construct_workers_manager(help, process_pid, workers): # pylint: disable=W0622,R0912,W0613

    workers = filter(None, workers) # pylint: disable=W0110

    class Command(BaseCommand):

        help = help

        requires_model_validation = False

        option_list = BaseCommand.option_list + ( make_option('-c', '--command',
                                                              action='store',
                                                              type=str,
                                                              dest='command',
                                                              help='start|stop|restart|status'), )

        def start(self):
            for worker in workers:
                worker.clean_queues()

            for worker in workers:
                print 'start %s' % worker.command_name
                with open(os.devnull, 'w') as devnull:
                    subprocess.Popen(['django-admin.py', worker.command_name, '--settings', 'the_tale.settings'], stdin=devnull, stdout=devnull, stderr=devnull)


        def stop(self):
            for worker in reversed(workers):
                if worker.stop_signal_required and pid.check(worker.pid):
                    print '%s found, send stop command' % worker.name
                    worker.cmd_stop()
                    print 'waiting answer'
                    answer_cmd = worker.stop_queue.get(block=True)
                    answer_cmd.ack()
                    print 'answer received'

            while any(pid.check(worker.pid) for worker in workers):
                time.sleep(0.1)


        def force_stop(self):
            for worker in reversed(workers):
                print 'force stop %s' % worker.command_name
                pid.force_kill(worker.command_name)

        def before_start(self): pass
        def before_stop(self): pass
        def before_force_stop(self): pass

        def after_start(self): pass
        def after_stop(self): pass
        def after_force_stop(self): pass


        @pid.protector(process_pid)
        def handle(self, *args, **options):

            command = options['command']

            if command == 'start':
                self.before_start()
                self.start()
                self.after_start()
                print 'infrastructure started'

            elif command == 'stop':
                self.before_stop()
                self.stop()
                self.after_stop()
                print 'infrastructure stopped'

            elif command == 'force_stop':
                self.before_force_stop()
                self.force_stop()
                self.after_force_stop()
                print 'infrastructure stopped (force)'

            elif command == 'restart':
                self.stop()
                self.start()
                print 'infrastructure restarted'

            elif command == 'status':
                print 'command "%s" does not implemented yet ' % command

            else:
                print 'command did not specified'


    return Command
