# coding: utf-8


class BaseEnvironment(object):

    def __init__(self):
        self.initialized = False

    def __getattribute__(self, name):
        if not super(BaseEnvironment, self).__getattribute__('initialized'):
            super(BaseEnvironment, self).__getattribute__('initialize')()
        return super(BaseEnvironment, self).__getattribute__(name)

    def initialize(self):
        pass

    def deinitialize(self):
        pass
