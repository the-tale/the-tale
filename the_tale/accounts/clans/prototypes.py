# coding: utf-8

from django.db import models, IntegrityError

from dext.utils.decorators import nested_commit_on_success

from common.utils.prototypes import BasePrototype
from common.utils import bbcode

from accounts.clans.models import Clan, Membership, MembershipRequest
from accounts.clans.relations import MEMBER_ROLE, MEMBERSHIP_REQUEST_TYPE
from accounts.clans import exceptions


class ClanPrototype(BasePrototype): #pylint: disable=R0904
    _model_class = Clan
    _readonly = ('id',
                 'created_at',
                 'updated_at',
                 'members_number')
    _bidirectional = ('name', 'abbr', 'motto', 'description')
    _get_by = ('id',)

    @property
    def description_html(self):
         return bbcode.render(self.description)

    @classmethod
    @nested_commit_on_success
    def create(cls, owner, abbr, name, motto, description):

        clan_model = cls._model_class.objects.create(name=name,
                                                     abbr=abbr,
                                                     motto=motto,
                                                     description=description,
                                                     members_number=1)

        clan = cls(clan_model)

        MembershipPrototype.create(owner, clan, role=MEMBER_ROLE.LEADER)

        return clan

    @nested_commit_on_success
    def add_member(self, account):
        try:
            MembershipPrototype.create(account, self, role=MEMBER_ROLE.MEMBER)
        except IntegrityError:
            raise exceptions.AddMemberFromClanError(member_id=account.id, clan_id=self.id)

        self._model_class.objects.filter(id=self.id).update(members_number=models.F('members_number')+1)
        self.save()

    @nested_commit_on_success
    def remove_member(self, account):
        membership = MembershipPrototype.get_by_account_id(account.id)
        if membership is None:
            raise exceptions.RemoveNotMemberFromClanError(member_id=account.id, clan_id=self.id)
        if membership.clan_id != self.id:
            raise exceptions.RemoveMemberFromWrongClanError(member_id=account.id, clan_id=self.id)
        if membership.role._is_LEADER:
            raise exceptions.RemoveLeaderFromClanError(member_id=account.id, clan_id=self.id)

        membership.remove()

        self._model.members_number = MembershipPrototype._db_filter(clan_id=self.id).count()
        self.save()

    def save(self):
        self._model.save()

    def remove(self):
        MembershipPrototype._db_filter(clan_id=self.id).delete()
        self._model.delete()



class MembershipPrototype(BasePrototype): #pylint: disable=R0904
    _model_class = Membership
    _readonly = ('id',
                 'created_at',
                 'updated_at',
                 'clan_id',
                 'account_id',
                 'role')
    _bidirectional = ()
    _get_by = ('clan_id', 'account_id')

    @classmethod
    def create(cls, account, clan, role):
        model = cls._model_class.objects.create(clan=clan._model,
                                                account=account._model,
                                                role=role)
        return cls(model)

    def remove(self):
        self._model.delete()


class MembershipRequestPrototype(BasePrototype): #pylint: disable=R0904
    _model_class = MembershipRequest
    _readonly = ('id',
                 'created_at',
                 'updated_at',
                 'clan_id',
                 'account_id',
                 'text')
    _bidirectional = ('type',)
    _get_by = ('id', 'clan_id', 'account_id')

    @classmethod
    def create(cls, account, clan, text, type):

        model = cls._model_class.objects.create(clan=clan._model,
                                                account=account._model,
                                                type=type,
                                                text=text)
        return cls(model)

    @classmethod
    def get_for_clan(cls, clan_id):
        models = cls._db_filter(clan_id=clan_id, type=MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT).order_by('created_at')
        return [cls(model=model) for model in models]

    @classmethod
    def get_for_account(cls, account_id):
        models = cls._db_filter(account_id=account_id, type=MEMBERSHIP_REQUEST_TYPE.FROM_CLAN).order_by('created_at')
        return [cls(model=model) for model in models]

    @property
    def text_html(self):
         return bbcode.render(self.text)

    def remove(self):
        self._model.delete()
