
import smart_imports

smart_imports.all()


class Account(utils_meta_relations.MetaType):
    __slots__ = ('caption', )
    TYPE = 7
    TYPE_CAPTION = 'Хранитель'

    def __init__(self, caption, **kwargs):
        super(Account, self).__init__(**kwargs)
        self.caption = caption

    @property
    def url(self):
        return dext_urls.url('accounts:show', self.id)

    @classmethod
    def create_from_object(cls, account):
        return cls(id=account.id, caption=account.nick_verbose)

    @classmethod
    def create_from_id(cls, id):
        from . import prototypes
        account = prototypes.AccountPrototype.get_by_id(id)
        if account is None:
            return None

        return cls.create_from_object(account)

    @classmethod
    def create_from_ids(cls, ids):
        return [cls.create_from_id(id) for id in ids]
