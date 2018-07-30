
import smart_imports

smart_imports.all()


class QuestError(utils_exceptions.TheTaleError):
    MSG = 'hero error'


class UnknownRequirementError(QuestError):
    MSG = 'unknown state requirement: %(requirement)r'


class UnknownPowerRecipientError(QuestError):
    MSG = 'unknown state action: %(recipient)r'


class UnknownUpgadeEquipmentTypeError(QuestError):
    MSG = 'unknown upgrade equipment: %(type)r'
