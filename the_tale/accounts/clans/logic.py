# coding: utf-8


from common.utils.decorators import lazy_property

from accounts.payments.relations import PERMANENT_PURCHASE_TYPE

from accounts.clans.prototypes import ClanPrototype, MembershipPrototype
from accounts.clans.conf import clans_settings

class ClanInfo(object):

    def __init__(self, account):
        self.account = account

    @lazy_property
    def can_create_clan(self):
        if not self.account.is_authenticated() or self.account.is_fast or self.membership is not None:
            return False

        if PERMANENT_PURCHASE_TYPE.CLAN_OWNERSHIP_RIGHT in self.account.permanent_purchases:
            return True

        return self.account.might >= clans_settings.OWNER_MIGHT_REQUIRED


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
