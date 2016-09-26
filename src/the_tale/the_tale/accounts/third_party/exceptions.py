# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError


class ThirdPartyError(TheTaleError):
    MSG = 'third party error'

class UnkwnownAuthorisationStateError(ThirdPartyError):
    MSG = 'unknown authorisation state: %(state)s'
