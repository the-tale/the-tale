# coding: utf-8

from the_tale.game.companions.exceptions import CompanionsError


class CompanionsAbilitiesError(CompanionsError):
    MSG = u'companions abilities error'


class NotOrderedUIDSError(CompanionsAbilitiesError):
    MSG = u'uids in container MUST be ordered'
