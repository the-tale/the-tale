# coding: utf-8

class TheTaleError(Exception):
    MSG = None

    def __init__(self, **kwargs):
        super(TheTaleError, self).__init__(self.MSG % kwargs)
