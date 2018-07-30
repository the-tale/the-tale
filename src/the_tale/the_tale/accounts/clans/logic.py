
import smart_imports

smart_imports.all()


class ClanInfo(object):

    def __init__(self, account):
        self.account = account

    @utils_decorators.lazy_property
    def membership(self):
        if self.account.is_authenticated:
            return prototypes.MembershipPrototype.get_by_account_id(self.account.id)

    @utils_decorators.lazy_property
    def clan(self):
        if self.membership:
            return prototypes.ClanPrototype.get_by_id(self.membership.clan_id)

    @utils_decorators.lazy_property
    def clan_id(self):
        if self.membership:
            return self.membership.clan_id

    def is_member_of(self, clan):
        return self.membership and clan and self.membership.clan_id == clan.id

    def is_owner_of(self, clan):
        return self.is_member_of(clan) and self.membership.role.is_LEADER

    @property
    def can_invite(self):
        return self.membership and self.membership.role.is_LEADER

    @property
    def can_remove(self):
        return self.membership and self.membership.role.is_LEADER
