
import smart_imports

smart_imports.all()


class ClansError(utils_exceptions.TheTaleError):
    pass


class AddMemberFromClanError(ClansError):
    MSG = 'can not add member %(member_id)d in clan %(clan_id)d since it has already in clan'


class RemoveMemberFromWrongClanError(ClansError):
    MSG = 'account %(member_id)d not member of clan %(clan_id)d'


class RemoveLeaderFromClanError(ClansError):
    MSG = 'account %(member_id)d is leader of clan %(clan_id)d and can not be removed'


class NotStaticPermission(ClansError):
    MSG = 'permission %(permission)s is not static (require member)'


class NotOnMemberPermission(ClansError):
    MSG = 'permission %(permission)s is not on member (require static)'


class CanNotDetermineRightsForUnknownClan(ClansError):
    MSG = 'can not determine rights for unknown clan'


class CanNotDetermineRightsForUnknownInitiator(ClansError):
    MSG = 'can not determine rights for unknown initiator'


class ClansInfosStorageError(ClansError):
    MSG = 'clans infos storage error: %(message)s'
