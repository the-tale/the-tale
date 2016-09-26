# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError

class QuestError(TheTaleError):
    MSG = 'hero error'


class UnknownRequirementError(QuestError):
    MSG = 'unknown state requirement: %(requirement)r'


class UnknownPowerRecipientError(QuestError):
    MSG = 'unknown state action: %(recipient)r'

class UnknownUpgadeEquipmentTypeError(QuestError):
    MSG = 'unknown upgrade equipment: %(type)r'
