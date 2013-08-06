# coding: utf-8

from dext.utils.decorators import nested_commit_on_success

from common.utils.prototypes import BasePrototype

from accounts.clans.models import Clan, ClanMembership
from accounts.clans.relations import MEMBER_ROLE



class ClanPrototype(BasePrototype): #pylint: disable=R0904
    _model_class = Clan
    _readonly = ('id',
                 'created_at',
                 'updated_at',
                 'members_number')
    _bidirectional = ('name', 'abbr', 'motto', 'description')
    _get_by = ('id',)


    @classmethod
    @nested_commit_on_success
    def create(cls, owner, abbr, name, motto, description):

        clan_model = cls._model_class.objects.create(name=name,
                                                     abbr=abbr,
                                                     motto=motto,
                                                     description=description,
                                                     members_number=1)

        clan = cls(clan_model)

        ClanMembershipPrototype.create(owner, clan, role=MEMBER_ROLE.LEADER)

        return clan



class ClanMembershipPrototype(BasePrototype): #pylint: disable=R0904
    _model_class = ClanMembership
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
