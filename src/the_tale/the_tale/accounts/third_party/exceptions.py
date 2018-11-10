
import smart_imports

smart_imports.all()


class ThirdPartyError(utils_exceptions.TheTaleError):
    MSG = 'third party error'


class UnkwnownAuthorisationStateError(ThirdPartyError):
    MSG = 'unknown authorisation state: %(state)s'
