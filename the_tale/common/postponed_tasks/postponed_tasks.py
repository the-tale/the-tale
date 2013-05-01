# coding: utf-8

from common.postponed_tasks.prototypes import postponed_task, POSTPONED_TASK_LOGIC_RESULT

@postponed_task
class FakePostponedInternalTask(object):

    TYPE = 'fake-task'
    INITIAL_STATE = 666

    def __init__(self, state=888, result_state=POSTPONED_TASK_LOGIC_RESULT.SUCCESS):
        self.state = state
        self.result_state = result_state

    def process(self, main_task):
        return self.result_state

    def serialize(self): return {'state': self.state,
                                 'result_state': self.result_state}

    @classmethod
    def deserialize(cls, data):
        return cls(**data)

    @property
    def response_data(self): return {'test_value': 666}

    @property
    def error_message(self): return u'some error message'

    @property
    def uuid(self): return 777
