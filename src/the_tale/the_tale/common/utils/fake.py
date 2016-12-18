# coding: utf-8

class FakeLogger(object):

    def debug(self, *argv, **kwargs): pass
    def info(self, *argv, **kwargs): pass
    def warn(self, *argv, **kwargs): pass
    def error(self, *argv, **kwargs): pass


class FakeWorkerCommand(object):

    def __init__(self):
        self.commands = []

    def __call__(self, *args):
        self.commands.append(tuple(args))
