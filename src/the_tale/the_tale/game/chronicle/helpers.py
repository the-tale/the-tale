
import smart_imports

smart_imports.all()


class FakeRecord(records.RecordBase):
    def __init__(self, type_, index=0, turn_number=0, actors={}):
        self.TYPE = type_
        self.index = index
        self.created_at_turn = turn_number
        self.actors = actors

    def get_text(self): return 'record_text_%d_%d' % (self.created_at_turn, self.index)
