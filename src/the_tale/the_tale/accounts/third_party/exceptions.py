# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError


class ThirdPartyError(TheTaleError):
    MSG = u'third party error'

class UnkwnownAuthorisationStateError(ThirdPartyError):
    MSG = u'unknown authorisation state: %(state)s'
