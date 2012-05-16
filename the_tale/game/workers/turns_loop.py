# coding: utf-8
import sys
import time
import traceback
import Queue

from django.utils.log import getLogger

from game.conf import game_settings

logger = getLogger('the-tale.workers.game_turns_loop')

class CMD_TYPE:
    INITIALIZE = 'initialize'
    STOP = 'stop'

class TurnsLoopException(Exception): pass

class Worker(object):

    def __init__(self, connection, game_queue):
        self.game_queue = connection.SimpleQueue(game_queue)
        self.exception_raised = False
        self.stop_required = False
        self.initialized = False

    def set_supervisor_worker(self, supervisor_worker):
        self.supervisor_worker = supervisor_worker

    def close_queries(self):
        # self.game_queue.close()
        pass

    def clean_queues(self):
        self.game_queue.queue.purge()

    def run(self):

        while not self.exception_raised and not self.stop_required:
            try:
                cmd = self.game_queue.get_nowait()
                cmd.ack()
                self.process_cmd(cmd.payload)
            except Queue.Empty:
                logger.info('send next turn command')
                self.supervisor_worker.cmd_next_turn()
                time.sleep(game_settings.TURN_DELAY)

    def process_cmd(self, cmd):
        cmd_type = cmd['type']
        cmd_data = cmd['data']

        logger.info('<%s> %r' % (cmd_type, cmd_data))

        if not self.initialized and cmd_type != CMD_TYPE.INITIALIZE:
            logger.error('ERROR: receive cmd before initialization')
            return

        try:
            { CMD_TYPE.INITIALIZE: self.process_initialize,
              CMD_TYPE.STOP: self.process_stop}[cmd_type](**cmd_data)
        except Exception, e:
            self.exception_raised = True
            logger.error('EXCEPTION: %s' % e)
            traceback.print_exc()

            logger.error('Game worker exception: game_logic',
                         exc_info=sys.exc_info(),
                         extra={} )


    def send_cmd(self, tp, data={}):
        self.game_queue.put({'type': tp, 'data': data}, serializer='json', compression=None)

    def cmd_initialize(self, worker_id):
        self.send_cmd(CMD_TYPE.INITIALIZE, {'worker_id': worker_id})

    def process_initialize(self, worker_id):

        if self.initialized:
            logger.warn('WARNING: turn loop already initialized, do reinitialization')

        self.initialized = True
        self.worker_id = worker_id

        logger.info('TURN LOOP INITIALIZED')

        self.supervisor_worker.cmd_answer('initialize', self.worker_id)

    def cmd_stop(self):
        return self.send_cmd(CMD_TYPE.STOP)

    def process_stop(self):
        # no need to save bundles, since they automaticaly saved on every turn
        self.initialized = False
        self.supervisor_worker.cmd_answer('stop', self.worker_id)
        self.stop_required = True
        logger.info('TURN LOOP STOPPED')
