# coding: utf-8

class FakeLogger(object):

    def debug(*argv, **kwargs): pass
    def info(*argv, **kwargs): pass
    def warn(*argv, **kwargs): pass
    def error(*argv, **kwargs): pass
