# coding: utf-8
from django.utils.log import getLogger
logger = getLogger('the-tale.workers.game_supervisor')

class BaseEnvironment(object):

    def __init__(self):
        self.initialized = False

    def __getattribute__(self, name):
        if not super(BaseEnvironment, self).__getattribute__('initialized'):
            import sys
            if 'game_supervisor' in sys.argv:
                logger.error('ENVIRONMENT INITIALIZATION > ')
            super(BaseEnvironment, self).__getattribute__('initialize')()
            self.initialized = True
            if 'game_supervisor' in sys.argv:
                logger.error('ENVIRONMENT INITIALIZATION < %r' % self.initialized)
        return super(BaseEnvironment, self).__getattribute__(name)

    def initialize(self):
        pass

    def deinitialize(self):
        pass
