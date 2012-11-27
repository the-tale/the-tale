# coding: utf-8

class FakePostpondTaskPrototype(object):

    def __init__(self, id_=0):
        self.id = id_

    def add_postsave_action(self, action): pass

    def extend_postsave_actions(self, actions): pass
