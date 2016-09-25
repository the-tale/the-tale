# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError

class QuestError(TheTaleError):
    MSG = u'hero error'


class UnknownRequirementError(QuestError):
    MSG = u'unknown state requirement: %(requirement)r'


class UnknownPowerRecipientError(QuestError):
    MSG = u'unknown state action: %(recipient)r'

class UnknownUpgadeEquipmentTypeError(QuestError):
    MSG = u'unknown upgrade equipment: %(type)r'
