
import smart_imports

smart_imports.all()


class ClansError(utils_exceptions.TheTaleError):
    pass


class AddMemberFromClanError(ClansError):
    MSG = 'can not add member %(member_id)d in clan %(clan_id)d since it has already in clan'


class RemoveNotMemberFromClanError(ClansError):
    MSG = 'account %(member_id)d not participate in any clan (try to remove from clan %(clan_id)s)'


class RemoveMemberFromWrongClanError(ClansError):
    MSG = 'account %(member_id)d not member of clan %(clan_id)d'


class RemoveLeaderFromClanError(ClansError):
    MSG = 'account %(member_id)d is leader of clan %(clan_id)d and can not be removed'
