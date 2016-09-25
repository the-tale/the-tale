# coding: utf-8

from dext.common.utils import urls

from the_tale.common.utils import meta_relations

from . import prototypes


class Account(meta_relations.MetaType):
    __slots__ = ('caption', )
    TYPE = 7
    TYPE_CAPTION = u'Хранитель'

    def __init__(self, caption, **kwargs):
        super(Account, self).__init__(**kwargs)
        self.caption = caption

    @property
    def url(self):
        return urls.url('accounts:show', self.id)

    @classmethod
    def create_from_object(cls, account):
        return cls(id=account.id, caption=account.nick_verbose)

    @classmethod
    def create_from_id(cls, id):
        account = prototypes.AccountPrototype.get_by_id(id)
        if account is None:
            return None

        return cls.create_from_object(account)

    @classmethod
    def create_from_ids(cls, ids):
        return [cls.create_from_id(id) for id in ids]
