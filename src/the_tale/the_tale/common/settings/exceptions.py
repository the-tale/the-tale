

import smart_imports

smart_imports.all()


class SettingsError(utils_exceptions.TheTaleError):
    MSG = 'settings error'


class WrongKeyType(SettingsError):
    MSG = 'wrong key type: %(key)r'


class WrongValueType(SettingsError):
    MSG = 'wrong value type: %(value)r'


class UnregisteredKey(SettingsError):
    MSG = 'unregistered key: %(key)s'


class KeyNotInSettings(SettingsError):
    MSG = 'key "%(key)r" not in settings'
