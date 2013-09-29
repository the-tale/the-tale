# coding: utf-8

from common.utils.exceptions import TheTaleError

class QuestError(TheTaleError):
    MSG = u'hero error'


class UnknownRequirement(QuestError):
    MSG = u'unknown state requirement: %(requirement)r'


class UnknownAction(QuestError):
    MSG = u'unknown state action: %(action)r'


class UnknownPowerRecipient(QuestError):
    MSG = u'unknown state action: %(recipient)r'
