# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError

class AmqpQueuesError(TheTaleError):
    MSG = None


class UnexpectedAnswerError(AmqpQueuesError):
    MSG = u'unexpected unswer from worker: %(cmd)r'


class WrongAnswerError(AmqpQueuesError):
    MSG = u'wrong answer: %(cmd)r, expected answers from %(workers)r'


class WaitAnswerTimeoutError(AmqpQueuesError):
    MSG = u'timeout (%(timeout)f sec) while waiting answer code "%(code)s" from workers %(workers)r'


class NoCmdMethodError(AmqpQueuesError):
    MSG = u'method "%(method)s" specified without appropriate cmd_* method'

class NoProcessMethodError(AmqpQueuesError):
    MSG = u'method "%(method)s" specified without appropriate process_* method'
