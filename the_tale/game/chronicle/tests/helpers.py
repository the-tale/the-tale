# coding: utf-8

from game.chronicle.records import RecordBase

class FakeRecord(RecordBase):
    def __init__(self, type_, index=0, turn_number=0, actors={}):
        self.TYPE = type_
        self.index = index
        self.created_at_turn = turn_number
        self.actors = actors
        self.substitutions = {}

    def get_text(self): return 'record_text_%d_%d' % (self.created_at_turn, self.index)
