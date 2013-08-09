# coding: utf-8


from common.utils.decorators import lazy_property
from accounts.clans.prototypes import ClanPrototype, MembershipPrototype

class ClanInfo(object):

    def __init__(self, account):
        self.account = account

    @lazy_property
    def can_create_clan(self):
        return self.account.is_authenticated() and not self.account.is_fast and self.membership is None

    @lazy_property
    def membership(self):
        if self.account.is_authenticated():
            return MembershipPrototype.get_by_account_id(self.account.id)

    @lazy_property
    def clan(self):
        if self.membership:
            return ClanPrototype.get_by_id(self.membership.clan_id)

    @lazy_property
    def clan_id(self):
        if self.membership:
            return self.membership.clan_id

    def is_member_of(self, clan):
        return self.membership and clan and self.membership.clan_id == clan.id

    def is_owner_of(self, clan):
        return self.is_member_of(clan) and self.membership.role._is_LEADER

    @property
    def can_invite(self):
        return self.membership and self.membership.role._is_LEADER

    @property
    def can_remove(self):
        return self.membership and self.membership.role._is_LEADER
