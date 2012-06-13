# coding: utf-8

class FakeMessanger(object):

    def __init__(self):
        self.messages = []

    def add_message(self, name, **kwargs):
        self.messages.append(name)
