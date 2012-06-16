# coding: utf-8

class FakeMessanger(object):

    def __init__(self):
        self.messages = []

    def add_message(self, name, current_time, **kwargs):
        self.messages.append(name)
