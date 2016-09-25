# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError

class ClansError(TheTaleError): pass

class AddMemberFromClanError(ClansError):
    MSG = u'can not add member %(member_id)d in clan %(clan_id)d since it has already in clan'

class RemoveNotMemberFromClanError(ClansError):
    MSG = u'account %(member_id)d not participate in any clan (try to remove from clan %(clan_id)s)'

class RemoveMemberFromWrongClanError(ClansError):
    MSG = u'account %(member_id)d not member of clan %(clan_id)d'

class RemoveLeaderFromClanError(ClansError):
    MSG = u'account %(member_id)d is leader of clan %(clan_id)d and can not be removed'
